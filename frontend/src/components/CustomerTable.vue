<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  mdiTrashCan, mdiPencil, mdiPlus, mdiMagnify, mdiFilePdfBox, mdiFileExcel,
  mdiFileDelimited, mdiEye, mdiFilterVariant, mdiSortAscending, mdiSortDescending, mdiCloseCircleOutline
} from '@mdi/js'
import CardBoxModal from '@/components/CardBoxModal.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseButton from '@/components/BaseButton.vue'
import FormControl from '@/components/FormControl.vue'
import axios from 'axios'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import { saveAs } from 'file-saver'
import * as XLSX from 'xlsx'
import { useMainStore } from '@/stores/main';
import { useAuthStore } from '@/stores/authStore';
import NotificationBar from '@/components/NotificationBar.vue';

const mainStore = useMainStore()
const authStore = useAuthStore()
const router = useRouter()
const customers = ref([])
const loading = ref(false)
const searchTerm = ref('')
const firstNameFilter = ref('')
const lastNameFilter = ref('')
const documentNumberFilter = ref('')
const emailFilter = ref('')
const customerTypeFilter = ref('')
const sortDescending = ref(false)
const perPage = ref(10)
const currentPage = ref(0)

const restrictedSearchFields = [
  'created_by', 'created_by_name', 'created_at',
  'modified_by', 'modified_by_name', 'updated_at'
];

const uniqueCustomerTypes = computed(() => {
  if (!customers.value) return [];
  return [...new Set(customers.value.map(c => c.customer_type).filter(Boolean))].sort();
});

const filteredCustomers = computed(() => {
  let filtered = [...customers.value];

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter(customer => {
      const searchFields = authStore.isSuperuser
        ? Object.values(customer)
        : Object.entries(customer)
            .filter(([key]) => !restrictedSearchFields.includes(key))
            .map(([, val]) => val);
      return searchFields.some(val => val && val.toString().toLowerCase().includes(term));
    });
  }

  if (firstNameFilter.value) {
    filtered = filtered.filter(c => c.first_name && c.first_name.toLowerCase().includes(firstNameFilter.value.toLowerCase()));
  }
  if (lastNameFilter.value) {
    filtered = filtered.filter(c => c.last_name && c.last_name.toLowerCase().includes(lastNameFilter.value.toLowerCase()));
  }
  if (documentNumberFilter.value) {
    filtered = filtered.filter(c => c.document_number && c.document_number.toLowerCase().includes(documentNumberFilter.value.toLowerCase()));
  }
  if (emailFilter.value) {
    filtered = filtered.filter(c => c.email && c.email.toLowerCase().includes(emailFilter.value.toLowerCase()));
  }
  if (customerTypeFilter.value) {
    filtered = filtered.filter(c => c.customer_type && c.customer_type.toLowerCase().includes(customerTypeFilter.value.toLowerCase()));
  }

  filtered.sort((a, b) => {
    return sortDescending.value ? (b.id - a.id) : (a.id - b.id);
  });
  return filtered;
});

const itemsPaginated = computed(() =>
  filteredCustomers.value.slice(perPage.value * currentPage.value, perPage.value * (currentPage.value + 1))
)
const numPages = computed(() => Math.ceil(filteredCustomers.value.length / perPage.value))
const currentPageHuman = computed(() => currentPage.value + 1)
const pagesList = computed(() => Array.from({ length: numPages.value }, (_, i) => i))

watch([searchTerm, firstNameFilter, lastNameFilter, documentNumberFilter, emailFilter, customerTypeFilter, sortDescending], () => {
  currentPage.value = 0;
});

const toggleSortOrder = () => sortDescending.value = !sortDescending.value;
const sortIcon = computed(() => sortDescending.value ? mdiSortDescending : mdiSortAscending);

const clearAllFilters = () => {
  searchTerm.value = ''; firstNameFilter.value = ''; lastNameFilter.value = ''; documentNumberFilter.value = '';
  emailFilter.value = ''; customerTypeFilter.value = '';
};

const isDeleteModalActive = ref(false)
const isDetailModalActive = ref(false)
const currentCustomer = ref({})
const selectedCustomerForView = ref({})

const API_URL = import.meta.env.VITE_API_URL

const fetchCustomers = async () => {
  if (!authStore.authToken) return;
  loading.value = true;
  try {
    const config = { headers: { 'Authorization': `Bearer ${authStore.authToken}` } }
    const response = await axios.get(`${API_URL}customer`, config) 

    customers.value = response.data?.data || []
  } catch (e) {
    console.error('Error obteniendo clientes:', e)
    mainStore.notify({ color: 'danger', message: 'Error obteniendo clientes: ' + (e.response?.data?.message || e.message) })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if(authStore.checkLoggedIn()){
    await authStore.fetchUserPermissions();
  }
  await fetchCustomers();
})

const openCreate = () => router.push({ name: 'customerCreate' });
const openEdit = (customer) => router.push({ name: 'customerEdit', params: { id: customer.id } });

const openDelete = (customer) => { currentCustomer.value = customer; isDeleteModalActive.value = true; };
const openDetailModal = (customer) => { selectedCustomerForView.value = customer; isDetailModalActive.value = true; };

const getAuthConfig = () => ({ headers: { 'Authorization': `Bearer ${authStore.authToken}` } })

const confirmDelete = async () => {
  loading.value = true;
  try {
    await axios.put(`${API_URL}customer/delete/${currentCustomer.value.id}`, {}, getAuthConfig());

    mainStore.notify({ color: 'success', message: 'Cliente desactivado exitosamente.' });
    await fetchCustomers();
  } catch (e) {
    console.error('Error desactivando cliente:', e);
    mainStore.notify({ color: 'danger', message: 'Error desactivando cliente: ' + (e.response?.data?.message || e.message) });
  } finally {
    isDeleteModalActive.value = false; loading.value = false;
  }
};

const getTableHeaders = () => {
  const headers = ["ID", "Nombres", "Apellidos", "Tipo Doc.", "N° Documento", "Teléfono", "Email", "Tipo Cliente", "Estado"];
  if (authStore.isSuperuser) {
    headers.push("Creado por", "Fecha Creación", "Modificado por", "Fecha Modificación");
  }
  return headers;
};
const getCustomerDataForExport = (customer) => {
  const data = [
    customer.id || '', customer.first_name || '', customer.last_name || '', customer.document_type || '',
    customer.document_number || '', customer.phone || '', customer.email || '', customer.customer_type || '',
    customer.status || ''
  ];
  if (authStore.isSuperuser) {
    data.push(
      customer.created_by_name || '', customer.created_at || '',
      customer.modified_by_name || '', customer.updated_at || ''
    );
  }
  return data;
};

const exportToPDF = () => {
  try {
    const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
    doc.setFontSize(18); doc.text('Reporte de Clientes', 14, 22);
    doc.setFontSize(11); doc.text(`Fecha: ${new Date().toLocaleDateString()}`, 14, 30);
    const tableColumn = getTableHeaders(); const tableRows = filteredCustomers.value.map(getCustomerDataForExport);
    autoTable(doc, { head: [tableColumn], body: tableRows, startY: 35, theme: 'grid', styles: { fontSize: 8, cellPadding: 1.5 }, headStyles: { fillColor: [41, 128, 185], textColor: [255, 255, 255], fontStyle: 'bold' } });
    doc.save('clientes.pdf');
    mainStore.notify({ color: 'success', message: 'Exportado a PDF con éxito.' })
  } catch (error) { console.error('Error al generar PDF:', error); mainStore.notify({ color: 'danger', message: 'Error al generar PDF: ' + error.message }) }
};
const exportToCSV = () => {
  try {
    const headers = getTableHeaders(); let csvContent = "\uFEFF" + headers.join(',') + '\n';
    filteredCustomers.value.forEach(customer => {
      const row = getCustomerDataForExport(customer);
      const formattedRow = row.map(cell => { if (cell === null || cell === undefined) return ''; cell = cell.toString(); if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) { return `"${cell.replace(/"/g, '""')}"`; } return cell; });
      csvContent += formattedRow.join(',') + '\n';
    });
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' }); saveAs(blob, 'clientes.csv');
    mainStore.notify({ color: 'success', message: 'Exportado a CSV con éxito.' })
  } catch (error) { console.error('Error al generar CSV:', error); mainStore.notify({ color: 'danger', message: 'Error al generar CSV: ' + error.message }) }
};
const exportToExcel = () => {
  try {
    const headers = getTableHeaders(); const data = filteredCustomers.value.map(getCustomerDataForExport); data.unshift(headers);
    const ws = XLSX.utils.aoa_to_sheet(data);
    ws['!cols'] = [ {wch: 5}, {wch: 20}, {wch: 20}, {wch: 10}, {wch: 15}, {wch: 15}, {wch: 25}, {wch: 12}, {wch: 10} ];
    const wb = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb, ws, "Clientes"); XLSX.writeFile(wb, 'clientes.xlsx');
    mainStore.notify({ color: 'success', message: 'Exportado a Excel con éxito.' })
  } catch (error) { console.error('Error al generar Excel:', error); mainStore.notify({ color: 'danger', message: 'Error al generar Excel: ' + error.message }) }
};

</script>

<template>
  <div v-if="mainStore && mainStore.notification && mainStore.notification.show" class="sticky top-0 z-[51] px-4 md:px-6">
    <NotificationBar
      v-model="mainStore.notification.show"
      :color="mainStore.notification.color"
      :icon="mainStore.notification.icon"
      @dismiss="mainStore.dismissNotification()"
      class="mt-2 shadow-lg">
      <span v-html="mainStore.notification.message?.replace(/\n/g, '<br>')"></span>
    </NotificationBar>
  </div>

  <CardBoxModal v-model="isDeleteModalActive" title="Confirmar Desactivación">
    <p>¿Está seguro que desea desactivar al cliente <strong>{{ currentCustomer.first_name }} {{ currentCustomer.last_name }}</strong>?</p>
    <p>Esta acción solo marcará al cliente como inactivo.</p>
    <div class="mt-6 flex justify-end space-x-2">
      <BaseButton color="whiteDark" label="Cancelar" @click="isDeleteModalActive = false" :disabled="loading"/>
      <BaseButton
        color="danger"
        :label="loading ? 'Desactivando...' : 'Desactivar'"
        :disabled="loading"
        @click="confirmDelete"
      />
    </div>
  </CardBoxModal>

  <CardBoxModal v-model="isDetailModalActive">
    <template #title>
      Detalles Cliente: {{ selectedCustomerForView.first_name }} {{ selectedCustomerForView.last_name }}
    </template>
    <div v-if="selectedCustomerForView.id" class="space-y-2 text-sm p-4">
      <p><strong>ID:</strong> {{ selectedCustomerForView.id }}</p>
      <p><strong>Nombres:</strong> {{ selectedCustomerForView.first_name }}</p>
      <p><strong>Apellidos:</strong> {{ selectedCustomerForView.last_name }}</p>
      <p><strong>Tipo Documento:</strong> {{ selectedCustomerForView.document_type }}</p>
      <p><strong>N° Documento:</strong> {{ selectedCustomerForView.document_number }}</p>
      <p><strong>Teléfono:</strong> {{ selectedCustomerForView.phone }}</p>
      <p><strong>Email:</strong> {{ selectedCustomerForView.email }}</p>
      <p><strong>Dirección:</strong> <span class="whitespace-pre-wrap">{{ selectedCustomerForView.address }}</span></p>
      <p><strong>Fecha de Nacimiento:</strong> {{ selectedCustomerForView.birth_date }}</p>
      <p><strong>Tipo Cliente:</strong> {{ selectedCustomerForView.customer_type }}</p>
      <p><strong>Estado:</strong> {{ selectedCustomerForView.status }}</p>
      <p><strong>Referencia:</strong> {{ selectedCustomerForView.reference || 'N/A' }}</p>
      <p><strong>Notas:</strong> <span class="whitespace-pre-wrap">{{ selectedCustomerForView.notes || 'N/A' }}</span></p>
      <p><strong>Activo:</strong> <span :class="selectedCustomerForView.active ? 'text-green-600' : 'text-red-600'">{{ selectedCustomerForView.active ? 'Sí' : 'No' }}</span></p>
      
      <div v-if="authStore.isSuperuser" class="pt-2 mt-2 border-t border-gray-200 dark:border-gray-700">
        <h3 class="text-md font-semibold mb-1 mt-2 text-gray-800 dark:text-gray-200">Información de Auditoría:</h3>
        <p><strong>Creado por:</strong> {{ selectedCustomerForView.created_by_name || 'N/A' }}</p>
        <p><strong>Fecha de Creación:</strong> {{ selectedCustomerForView.created_at }}</p>
        <p><strong>Modificado por:</strong> {{ selectedCustomerForView.modified_by_name || 'N/A' }}</p>
        <p><strong>Fecha de Modificación:</strong> {{ selectedCustomerForView.updated_at }}</p>
      </div>
    </div>
    <template #footer>
      <BaseButtons>
        <BaseButton label="Cerrar" color="info" @click="isDetailModalActive = false" />
      </BaseButtons>
    </template>
  </CardBoxModal>

  <div class="mb-6 flex flex-col md:flex-row items-center justify-between gap-4 px-4 md:px-0" style="margin: 1rem;">
    <BaseButton 
      v-if="authStore.hasPermission('customer.add_customer')"
      color="info" :icon="mdiPlus" label="Crear Cliente" @click="openCreate" small />
    <div class="flex items-center gap-2 w-full md:w-auto">
      <div class="relative flex-grow md:flex-grow-0">
        <FormControl v-model="searchTerm" placeholder="Búsqueda rápida..." :icon="mdiMagnify" />
      </div>
      <BaseButton color="info" outline small :icon="mdiFilterVariant" title="Limpiar todos los filtros" @click="clearAllFilters" />
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
            <BaseButton :icon="sortIcon" @click="toggleSortOrder" small class="ml-1 !p-1" :title="sortDescending ? 'Orden Descendente' : 'Orden Ascendente'" />
          </th>
          <th scope="col" class="px-4 py-3">Nombres</th>
          <th scope="col" class="px-4 py-3">Apellidos</th>
          <th scope="col" class="px-4 py-3">N° Documento</th>
          <th scope="col" class="px-4 py-3">Email</th>
          <th scope="col" class="px-4 py-3">Tipo Cliente</th>
          <th scope="col" class="px-4 py-3 text-center">Acciones</th>
        </tr>
        <tr class="bg-gray-100 dark:bg-gray-700">
          <td class="px-1 py-1 text-center">
            <BaseButton :icon="mdiCloseCircleOutline" @click="clearAllFilters" small color="danger" outline class="!p-1" title="Limpiar filtros" />
          </td>
          <td class="px-1 py-1"><FormControl type="text" v-model.lazy="firstNameFilter" placeholder="Filtrar..." class="text-xs min-w-[120px]" /></td>
          <td class="px-1 py-1"><FormControl type="text" v-model.lazy="lastNameFilter" placeholder="Filtrar..." class="text-xs min-w-[120px]" /></td>
          <td class="px-1 py-1"><FormControl type="text" v-model.lazy="documentNumberFilter" placeholder="Filtrar..." class="text-xs min-w-[120px]" /></td>
          <td class="px-1 py-1"><FormControl type="text" v-model.lazy="emailFilter" placeholder="Filtrar..." class="text-xs min-w-[120px]" /></td>
          <td class="px-1 py-1">
            <input list="customer-type-datalist" v-model.lazy="customerTypeFilter" placeholder="Filtrar..." class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs min-w-[100px] text-gray-900 dark:text-gray-100" />
            <datalist id="customer-type-datalist">
              <option v-for="ctype in uniqueCustomerTypes" :key="ctype" :value="ctype"></option>
            </datalist>
          </td>
          <td class="px-1 py-1"></td>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading && itemsPaginated.length === 0"><td colspan="8" class="text-center py-4">Cargando clientes...</td></tr>
        <tr v-else-if="itemsPaginated.length === 0"><td colspan="8" class="text-center py-4">No se encontraron clientes que coincidan.</td></tr>
        <tr v-for="customer in itemsPaginated" :key="customer.id" class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
          <td data-label="ID" class="px-4 py-2">{{ customer.id }}</td>
          <td data-label="Nombres" class="px-4 py-2 font-medium text-gray-900 whitespace-nowrap dark:text-white">
            <span class="cursor-pointer hover:underline" @click="openDetailModal(customer)">{{ customer.first_name }}</span>
          </td>
          <td data-label="Apellidos" class="px-4 py-2">{{ customer.last_name }}</td>
          <td data-label="N° Documento" class="px-4 py-2">{{ customer.document_number }}</td>
          <td data-label="Email" class="px-4 py-2">{{ customer.email }}</td>
          <td data-label="Tipo Cliente" class="px-4 py-2">{{ customer.customer_type }}</td>
          <td class="px-4 py-2 whitespace-nowrap text-center" data-label="Acciones">
            <BaseButtons type="justify-center" no-wrap>
              <BaseButton v-if="authStore.hasPermission('customer.change_customer')" color="info" :icon="mdiPencil" small title="Editar" @click="openEdit(customer)" />
              <BaseButton v-if="customer.active && authStore.hasPermission('customer.delete_customer')" color="danger" :icon="mdiTrashCan" small title="Desactivar" @click="openDelete(customer)" />
              <BaseButton color="light" outline :icon="mdiEye" small title="Ver Detalles" @click="openDetailModal(customer)" />
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
      <small>Página {{ currentPageHuman }} de {{ numPages }} (Total: {{ filteredCustomers.length }} clientes)</small>
    </div>
  </div>
</template>

<style scoped>
thead .px-1 { padding-left: 0.25rem; padding-right: 0.25rem; }
thead .py-1 { padding-top: 0.25rem; padding-bottom: 0.25rem; }
thead input[type="text"], thead select, thead input[list] {
  padding: 0.3rem 0.5rem; font-size: 0.75rem; border-radius: 0.375rem;
  border: 1px solid #D1D5DB; 
  background-color: #FFF;
  color: #111827;
}
.dark thead input[type="text"], .dark thead select, .dark thead input[list] {
  background-color: #374151; border-color: #4B5563; color: #F3F4F6; 
}
.dark thead input[type="text"]::placeholder, .dark thead input[list]::placeholder {
  color: #9CA3AF;
}

@media (max-width: 768px) {
  table:not(.keep-desktop-layout) thead tr:nth-child(2) { display: none; }
  table:not(.keep-desktop-layout) { border: 0; }
  table:not(.keep-desktop-layout) thead tr:first-child { display: none; }
  table:not(.keep-desktop-layout) tr { margin-bottom: 1rem; display: block; border-bottom: 2px solid #ddd; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); padding: 0.5rem; }
  table:not(.keep-desktop-layout) td { display: flex; justify-content: space-between; text-align: right; padding: 0.5rem; border-bottom: 1px dotted #eee; }
  table:not(.keep-desktop-layout) td:last-child { border-bottom: 0; }
  table:not(.keep-desktop-layout) td::before { content: attr(data-label); float: left; font-weight: bold; text-transform: uppercase; padding-right: 0.5rem; }
}
</style>