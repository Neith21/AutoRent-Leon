<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
    mdiFileDocumentPlusOutline, mdiFileEyeOutline, mdiFilterVariant, mdiSortAscending,
    mdiSortDescending, mdiCloseCircleOutline, mdiFilePdfBox, mdiFileExcel,
    mdiFileDelimited, mdiPencil
} from '@mdi/js'
import CardBoxModal from '@/components/CardBoxModal.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseButton from '@/components/BaseButton.vue'
import FormControl from '@/components/FormControl.vue'
import NotificationBar from '@/components/NotificationBar.vue';
import axios from 'axios'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import { saveAs } from 'file-saver'
import * as XLSX from 'xlsx'
import { useMainStore } from '@/stores/main';
import { useAuthStore } from '@/stores/authStore';

const mainStore = useMainStore()
const authStore = useAuthStore()
const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL;

const invoices = ref([])
const loading = ref(false)

const searchTerm = ref('')
const invoiceNumberFilter = ref('')
const customerNameFilter = ref('')
const statusFilter = ref('')
const sortDescending = ref(false)

const perPage = ref(10)
const currentPage = ref(0)

const isDetailModalActive = ref(false)
const isEditStatusModalActive = ref(false)
const selectedInvoiceForView = ref({})
const currentInvoiceForEdit = ref({ id: null, status: '' })

const statusOptions = [
    { id: 'Emitida', label: 'Emitida' },
    { id: 'Pagada', label: 'Pagada' },
    { id: 'Anulada', label: 'Anulada' },
]

const uniqueStatuses = computed(() => {
    if (!invoices.value) return [];
    return [...new Set(invoices.value.map(inv => inv.status).filter(Boolean))].sort();
});

const restrictedSearchFields = [
    'created_by', 'created_by_name', 'created_at',
    'modified_by', 'modified_by_name', 'updated_at', 'rental_id'
];

const filteredInvoices = computed(() => {
    let filtered = [...invoices.value];

    if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase();
        filtered = filtered.filter(invoice => {
            const searchFields = authStore.isSuperuser
                ? Object.values(invoice)
                : Object.entries(invoice).filter(([key]) => !restrictedSearchFields.includes(key)).map(([, val]) => val);
            return searchFields.some(val => val && val.toString().toLowerCase().includes(term));
        });
    }

    if (invoiceNumberFilter.value) {
        filtered = filtered.filter(i => i.invoice_number && i.invoice_number.toLowerCase().includes(invoiceNumberFilter.value.toLowerCase()));
    }
    if (customerNameFilter.value) {
        filtered = filtered.filter(i => i.customer_name && i.customer_name.toLowerCase().includes(customerNameFilter.value.toLowerCase()));
    }
    if (statusFilter.value) {
        filtered = filtered.filter(i => i.status === statusFilter.value);
    }

    filtered.sort((a, b) => sortDescending.value ? b.id - a.id : a.id - b.id);
    return filtered;
});

const itemsPaginated = computed(() =>
    filteredInvoices.value.slice(perPage.value * currentPage.value, perPage.value * (currentPage.value + 1))
)
const numPages = computed(() => Math.ceil(filteredInvoices.value.length / perPage.value))
const currentPageHuman = computed(() => currentPage.value + 1)
const pagesList = computed(() => Array.from({ length: numPages.value }, (_, i) => i))

watch([searchTerm, invoiceNumberFilter, customerNameFilter, statusFilter, sortDescending], () => {
    currentPage.value = 0;
});

const toggleSortOrder = () => sortDescending.value = !sortDescending.value;
const sortIcon = computed(() => sortDescending.value ? mdiSortDescending : mdiSortAscending);

const clearAllFilters = () => {
    searchTerm.value = ''; invoiceNumberFilter.value = ''; customerNameFilter.value = ''; statusFilter.value = '';
};

const getAuthConfig = () => ({ headers: { Authorization: `Bearer ${authStore.authToken}` } })

const fetchInvoices = async () => {
    if (!authStore.authToken) return;
    loading.value = true;
    try {
        const response = await axios.get(`${API_URL}invoice`, getAuthConfig())
        invoices.value = response.data?.data || []
    } catch (e) {
        console.error('Error obteniendo facturas:', e)
        mainStore.notify({ color: 'danger', message: 'Error obteniendo facturas: ' + (e.response?.data?.message || e.message) })
    } finally {
        loading.value = false
    }
}

onMounted(async () => {
    if (authStore.checkLoggedIn()) {
        await authStore.fetchUserPermissions();
    }
    await fetchInvoices();
})

const openCreateInvoice = () => router.push({ name: 'invoiceCreate' });
const openDetailModal = (invoice) => { selectedInvoiceForView.value = invoice; isDetailModalActive.value = true; };
const openEditStatusModal = (invoice) => {
    currentInvoiceForEdit.value = { id: invoice.id, status: invoice.status };
    isEditStatusModalActive.value = true;
};

const handleUpdateStatus = async () => {
    if (!currentInvoiceForEdit.value.id) return;
    loading.value = true;
    try {
        const payload = { status: currentInvoiceForEdit.value.status };
        await axios.put(`${API_URL}invoice/${currentInvoiceForEdit.value.id}`, payload, getAuthConfig());
        mainStore.notify({ color: 'success', message: 'Estado de la factura actualizado.' });
        await fetchInvoices();
    } catch (e) {
        console.error('Error actualizando estado:', e);
        mainStore.notify({ color: 'danger', message: 'Error al actualizar: ' + (e.response?.data?.message || e.message) });
    } finally {
        isEditStatusModalActive.value = false;
        loading.value = false;
    }
}

const handleIssueInvoice = async () => {
    if (!selectedInvoiceForView.value || !selectedInvoiceForView.value.id) return;
    loading.value = true;
    try {
        const invoiceId = selectedInvoiceForView.value.id;
        await axios.post(`${API_URL}invoice/issue-invoice/${invoiceId}`, {}, getAuthConfig());
        mainStore.notify({ color: 'success', message: 'La factura está siendo enviada al cliente.' });
        isDetailModalActive.value = false;
    } catch (e) {
        console.error('Error al emitir factura:', e);
        mainStore.notify({
            color: 'danger',
            message: 'Error al emitir factura: ' + (e.response?.data?.message || e.message)
        });
    } finally {
        loading.value = false;
    }
};

// --- Lógica de Exportación ---
const getTableHeaders = () => {
    const headers = ["ID", "N° Factura", "ID Alquiler", "Cliente", "Monto Total", "Estado", "Fecha Emisión"];
    if (authStore.isSuperuser) {
        headers.push("Creado por", "Fecha Creación", "Modificado por", "Fecha Modificación");
    }
    return headers;
};

const getInvoiceDataForExport = (invoice) => {
    const data = [
        invoice.id, invoice.invoice_number, invoice.rental_id, invoice.customer_name, invoice.total_amount,
        invoice.status, invoice.issue_date
    ];
    if (authStore.isSuperuser) {
        data.push(invoice.created_by_name || '', invoice.created_at || '', invoice.modified_by_name || '', invoice.updated_at || '');
    }
    return data;
};

const exportToPDF = () => {
    try {
        const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
        doc.setFontSize(18); doc.text('Reporte de Facturas', 14, 22);
        const tableColumn = getTableHeaders();
        const tableRows = filteredInvoices.value.map(getInvoiceDataForExport);
        autoTable(doc, { head: [tableColumn], body: tableRows, startY: 35, theme: 'grid' });
        doc.save('facturas.pdf');
        mainStore.notify({ color: 'success', message: 'Exportado a PDF con éxito.' });
    } catch (error) { mainStore.notify({ color: 'danger', message: 'Error al generar PDF: ' + error.message }); }
};

const exportToCSV = () => {
    try {
        const headers = getTableHeaders();
        let csvContent = "\uFEFF" + headers.join(',') + '\n';
        filteredInvoices.value.forEach(invoice => {
            const row = getInvoiceDataForExport(invoice).map(cell => `"${String(cell ?? '').replace(/"/g, '""')}"`);
            csvContent += row.join(',') + '\n';
        });
        saveAs(new Blob([csvContent], { type: 'text/csv;charset=utf-8;' }), 'facturas.csv');
        mainStore.notify({ color: 'success', message: 'Exportado a CSV con éxito.' });
    } catch (error) { mainStore.notify({ color: 'danger', message: 'Error al generar CSV: ' + error.message }); }
};

const exportToExcel = () => {
    try {
        const headers = getTableHeaders();
        const data = filteredInvoices.value.map(getInvoiceDataForExport);
        data.unshift(headers);
        const ws = XLSX.utils.aoa_to_sheet(data);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Facturas");
        XLSX.writeFile(wb, 'facturas.xlsx');
        mainStore.notify({ color: 'success', message: 'Exportado a Excel con éxito.' });
    } catch (error) { mainStore.notify({ color: 'danger', message: 'Error al generar Excel: ' + error.message }); }
};
</script>

<template>
    <div v-if="mainStore.notification && mainStore.notification.show" class="sticky top-0 z-[51] px-4 md:px-6">
        <NotificationBar v-model="mainStore.notification.show" :color="mainStore.notification.color"
            :icon="mainStore.notification.icon" @dismiss="mainStore.dismissNotification()" class="mt-2 shadow-lg">
            <span v-html="mainStore.notification.message?.replace(/\n/g, '<br>')"></span>
        </NotificationBar>
    </div>

    <!-- Modal para editar estado -->
    <CardBoxModal v-model="isEditStatusModalActive" title="Actualizar Estado de Factura">
        <form @submit.prevent="handleUpdateStatus">
            <div class="space-y-4 px-4 py-2">
                <p>Seleccione el nuevo estado para la factura <strong>N° {{ currentInvoiceForEdit.id }}</strong>.</p>
                <FormControl v-model="currentInvoiceForEdit.status" :options="statusOptions" />
            </div>
            <div class="mt-6 px-4 py-3 flex justify-end space-x-2 bg-gray-50 dark:bg-gray-800 rounded-b-lg">
                <BaseButton label="Cancelar" color="whiteDark" type="button" @click="isEditStatusModalActive = false"
                    :disabled="loading" />
                <BaseButton :label="loading ? 'Actualizando...' : 'Actualizar Estado'" color="info" type="submit"
                    :disabled="loading" />
            </div>
        </form>
    </CardBoxModal>

    <!-- Modal para ver detalles -->
    <CardBoxModal v-model="isDetailModalActive" :title="`Detalles Factura: ${selectedInvoiceForView.invoice_number}`">
        <div v-if="selectedInvoiceForView.id" class="space-y-2 text-sm p-4">
            <p><strong>ID Factura:</strong> {{ selectedInvoiceForView.id }}</p>
            <p><strong>N° Factura:</strong> {{ selectedInvoiceForView.invoice_number }}</p>
            <p><strong>Alquiler ID:</strong> {{ selectedInvoiceForView.rental_id }}</p>
            <p><strong>Cliente:</strong> {{ selectedInvoiceForView.customer_name }} ({{
                selectedInvoiceForView.customer_type }})</p>
            <p><strong>Monto Total:</strong> <span class="font-bold text-emerald-600">${{
                selectedInvoiceForView.total_amount }}</span></p>
            <p><strong>Estado:</strong> {{ selectedInvoiceForView.status }}</p>
            <p><strong>Fecha Emisión:</strong> {{ selectedInvoiceForView.issue_date }}</p>
            <div class="pt-2 mt-2 border-t">
                <h3 class="text-md font-semibold mt-2">Detalle de Pagos (Referencia):</h3>
                <pre
                    class="whitespace-pre-wrap text-xs bg-gray-100 dark:bg-gray-700 p-2 rounded mt-1">{{ selectedInvoiceForView.reference || 'Sin detalles.' }}</pre>
            </div>
            <div v-if="authStore.isSuperuser" class="pt-2 mt-2 border-t">
                <h3 class="text-md font-semibold mt-2">Auditoría:</h3>
                <p><strong>Creado por:</strong> {{ selectedInvoiceForView.created_by_name || 'N/A' }}</p>
                <p><strong>Fecha Creación:</strong> {{ selectedInvoiceForView.created_at }}</p>
                <p><strong>Modificado por:</strong> {{ selectedInvoiceForView.modified_by_name || 'N/A' }}</p>
                <p><strong>Fecha Modificación:</strong> {{ selectedInvoiceForView.updated_at }}</p>
            </div>
        </div>
        <div class="px-4 py-3 flex justify-end space-x-2 bg-gray-50 dark:bg-gray-800 rounded-b-lg">
            <BaseButton
                v-if="selectedInvoiceForView.status === 'Emitida'"
                label="Emitir Factura"
                color="success"
                :icon="mdiEmailSendOutline"
                :disabled="loading"
                @click="handleIssueInvoice"
            />
            <BaseButton label="Cerrar" color="info" @click="isDetailModalActive = false" />
        </div>
    </CardBoxModal>

    <div class="mb-6 flex flex-col md:flex-row items-center justify-between gap-4 px-4 md:px-0" style="margin: 1rem;">
        <BaseButton color="info" :icon="mdiFileDocumentPlusOutline" label="Generar Factura" @click="openCreateInvoice"
            small />
        <div class="flex items-center gap-2 w-full md:w-auto">
            <FormControl v-model="searchTerm" placeholder="Búsqueda rápida..." />
            <BaseButton color="success" small :icon="mdiFilePdfBox" title="Exportar a PDF" @click="exportToPDF" />
            <BaseButton color="primary" small :icon="mdiFileDelimited" title="Exportar a CSV" @click="exportToCSV" />
            <BaseButton color="warning" small :icon="mdiFileExcel" title="Exportar a Excel" @click="exportToExcel" />
        </div>
    </div>

    <div class="overflow-x-auto shadow-md sm:rounded-lg px-4 md:px-0">
        <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
            <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                <tr>
                    <th scope="col" class="px-4 py-3 whitespace-nowrap">
                        ID
                        <BaseButton :icon="sortIcon" @click="toggleSortOrder" small class="ml-1 !p-1" />
                    </th>
                    <th scope="col" class="px-4 py-3">N° Factura</th>
                    <th scope="col" class="px-4 py-3">Cliente</th>
                    <th scope="col" class="px-4 py-3">Monto Total</th>
                    <th scope="col" class="px-4 py-3">Estado</th>
                    <th scope="col" class="px-4 py-3">Fecha Emisión</th>
                    <th scope="col" class="px-4 py-3 text-center">Acciones</th>
                </tr>
                <tr class="bg-gray-100 dark:bg-gray-700">
                    <td class="px-1 py-1 text-center">
                        <BaseButton :icon="mdiCloseCircleOutline" @click="clearAllFilters" small color="danger" outline
                            class="!p-1" title="Limpiar filtros" />
                    </td>
                    <td class="px-1 py-1">
                        <FormControl type="text" v-model.lazy="invoiceNumberFilter" placeholder="Filtrar..." />
                    </td>
                    <td class="px-1 py-1">
                        <FormControl type="text" v-model.lazy="customerNameFilter" placeholder="Filtrar..." />
                    </td>
                    <td class="px-1 py-1"></td>
                    <td class="px-1 py-1">
                        <select v-model="statusFilter"
                            class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs text-gray-900 dark:text-gray-100">
                            <option value="">Todos</option>
                            <option v-for="status in uniqueStatuses" :key="status" :value="status">{{ status }}</option>
                        </select>
                    </td>
                    <td class="px-1 py-1"></td>
                    <td class="px-1 py-1"></td>
                </tr>
            </thead>
            <tbody>
                <tr v-if="loading">
                    <td colspan="7" class="text-center py-4">Cargando facturas...</td>
                </tr>
                <tr v-else-if="itemsPaginated.length === 0">
                    <td colspan="7" class="text-center py-4">No se encontraron facturas.</td>
                </tr>
                <tr v-for="invoice in itemsPaginated" :key="invoice.id"
                    class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
                    <td data-label="ID" class="px-4 py-2">{{ invoice.id }}</td>
                    <td data-label="N° Factura" class="px-4 py-2 font-medium text-gray-900 dark:text-white">{{
                        invoice.invoice_number }}</td>
                    <td data-label="Cliente" class="px-4 py-2">{{ invoice.customer_name }}</td>
                    <td data-label="Monto Total" class="px-4 py-2 font-bold">${{ invoice.total_amount }}</td>
                    <td data-label="Estado" class="px-4 py-2">
                        <span :class="{
                            'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300': invoice.status === 'Emitida',
                            'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300': invoice.status === 'Pagada',
                            'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300': invoice.status === 'Anulada'
                        }" class="text-xs font-medium px-2.5 py-0.5 rounded-full">
                            {{ invoice.status }}
                        </span>
                    </td>
                    <td data-label="Fecha Emisión" class="px-4 py-2">{{ invoice.issue_date }}</td>
                    <td class="px-4 py-2 whitespace-nowrap text-center" data-label="Acciones">
                        <BaseButtons type="justify-center" no-wrap>
                            <BaseButton v-if="authStore.hasPermission('invoice.change_invoice')" color="info"
                                :icon="mdiPencil" small title="Editar Estado" @click="openEditStatusModal(invoice)" />
                            <BaseButton color="light" outline :icon="mdiFileEyeOutline" small title="Ver Detalles"
                                @click="openDetailModal(invoice)" />
                        </BaseButtons>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="p-3 lg:px-6 border-t border-gray-100 dark:border-slate-800" v-if="numPages > 0">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-3">
            <BaseButtons>
                <BaseButton v-for="page in pagesList" :key="page" :active="page === currentPage" :label="page + 1"
                    :color="page === currentPage ? 'lightDark' : 'whiteDark'" small @click="currentPage = page" />
            </BaseButtons>
            <small>Página {{ currentPageHuman }} de {{ numPages }} (Total: {{ filteredInvoices.length }}
                facturas)</small>
        </div>
    </div>
</template>