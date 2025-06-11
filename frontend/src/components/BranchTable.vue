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

const branches = ref([])
const loading = ref(false)

// Estados para filtros y orden
const searchTerm = ref('')
const nameFilter = ref('')
const departmentFilter = ref('')
const municipalityFilter = ref('')
const districtFilter = ref('')
const emailFilter = ref('')
const sortDescending = ref(false)

const perPage = ref(10)
const currentPage = ref(0)

const restrictedSearchFields = [
  'created_by', 'created_by_name', 'created_at',
  'modified_by', 'modified_by_name', 'updated_at'
];

const uniqueDepartments = computed(() => {
  if (!branches.value) return [];
  return [...new Set(branches.value.map(b => b.department).filter(Boolean))].sort();
});

const uniqueMunicipalities = computed(() => {
  if (!branches.value) return [];
  return [...new Set(branches.value.map(b => b.municipality).filter(Boolean))].sort();
});

const uniqueDistricts = computed(() => {
  if (!branches.value) return [];
  return [...new Set(branches.value.map(b => b.district).filter(Boolean))].sort();
});

const filteredBranches = computed(() => {
  let filtered = [...branches.value];
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter(branch => {
      if (authStore.isSuperuser) { // Usar authStore.isSuperuser
        return Object.values(branch).some(val => val && val.toString().toLowerCase().includes(term));
      } else {
        return Object.entries(branch).some(([key, val]) => {
          if (restrictedSearchFields.includes(key)) return false;
          return val && val.toString().toLowerCase().includes(term);
        });
      }
    });
  }
  if (nameFilter.value) {
    const term = nameFilter.value.toLowerCase();
    filtered = filtered.filter(b => b.name && b.name.toLowerCase().includes(term));
  }
  if (departmentFilter.value) {
    const term = departmentFilter.value.toLowerCase();
    filtered = filtered.filter(b => b.department && b.department.toLowerCase().includes(term));
  }
  if (municipalityFilter.value) {
    const term = municipalityFilter.value.toLowerCase();
    filtered = filtered.filter(b => b.municipality && b.municipality.toLowerCase().includes(term));
  }
  if (districtFilter.value) {
    const term = districtFilter.value.toLowerCase();
    filtered = filtered.filter(b => b.district && b.district.toLowerCase().includes(term));
  }
  if (emailFilter.value) {
    const term = emailFilter.value.toLowerCase();
    filtered = filtered.filter(b => b.email && b.email.toLowerCase().includes(term));
  }
  filtered.sort((a, b) => {
    return sortDescending.value ? (b.id - a.id) : (a.id - b.id);
  });
  return filtered;
});

const itemsPaginated = computed(() =>
  filteredBranches.value.slice(perPage.value * currentPage.value, perPage.value * (currentPage.value + 1))
)
const numPages = computed(() => Math.ceil(filteredBranches.value.length / perPage.value))
const currentPageHuman = computed(() => currentPage.value + 1)
const pagesList = computed(() => Array.from({ length: numPages.value }, (_, i) => i))

watch([searchTerm, nameFilter, departmentFilter, municipalityFilter, districtFilter, emailFilter, sortDescending], () => {
  currentPage.value = 0;
});

const toggleSortOrder = () => sortDescending.value = !sortDescending.value;
const sortIcon = computed(() => sortDescending.value ? mdiSortDescending : mdiSortAscending);

const clearAllFilters = () => {
  searchTerm.value = ''; nameFilter.value = ''; departmentFilter.value = '';
  municipalityFilter.value = ''; districtFilter.value = ''; emailFilter.value = '';
};

const isDeleteModalActive = ref(false)
const isDetailModalActive = ref(false)
const currentBranch = ref({})
const selectedBranchForView = ref({})

const API_URL = import.meta.env.VITE_API_URL

const fetchBranches = async () => {
  if (!authStore.authToken) return; // Usar token del store
  loading.value = true;
  try {
    const config = { headers: { 'Authorization': `Bearer ${authStore.authToken}` } }
    const response = await axios.get(`${API_URL}branch`, config)
    branches.value = response.data?.data || []
  } catch (e) {
    console.error('Error obteniendo sucursales:', e)
    mainStore.notify({ color: 'danger', message: 'Error obteniendo sucursales: ' + (e.response?.data?.message || e.message) })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if(authStore.checkLoggedIn()){
    await authStore.fetchUserPermissions();
  }
  await fetchBranches();
})

const openCreate = () => router.push({ name: 'branchCreate' });
const openEdit = (branch) => router.push({ name: 'branchEdit', params: { id: branch.id } });

const openDelete = (branch) => { currentBranch.value = branch; isDeleteModalActive.value = true; };
const openDetailModal = (branch) => { selectedBranchForView.value = branch; isDetailModalActive.value = true; };

const getAuthConfig = () => ({ headers: { 'Authorization': `Bearer ${authStore.authToken}` } })

const confirmDelete = async () => {
  loading.value = true;
  try {
    await axios.put(`${API_URL}branch/delete/${currentBranch.value.id}`, {}, getAuthConfig());
    mainStore.notify({ color: 'success', message: 'Sucursal desactivada exitosamente.' });
    await fetchBranches();
  } catch (e) {
    console.error('Error desactivando sucursal:', e);
    mainStore.notify({ color: 'danger', message: 'Error desactivando sucursal: ' + (e.response?.data?.message || e.message) });
  } finally {
    isDeleteModalActive.value = false; loading.value = false;
  }
};

const getTableHeaders = () => {
  const headers = ["ID", "Nombre", "Teléfono", "Dirección", "Email", "Distrito", "Municipio", "Departamento"];
  if (authStore.isSuperuser) {
    headers.push("Creado por", "Fecha Creación", "Modificado por", "Fecha Modificación");
  }
  return headers;
};
const getBranchDataForExport = (branch) => {
  const data = [
    branch.id || '', branch.name || '', branch.phone || '', branch.address || '',
    branch.email || '', branch.district || '', branch.municipality || '', branch.department || ''
  ];
  if (authStore.isSuperuser) {
    data.push(
      branch.created_by_name || '', branch.created_at || '',
      branch.modified_by_name || '', branch.updated_at || ''
    );
  }
  return data;
};

const exportToPDF = () => {
  try {
    const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
    doc.setFontSize(18); doc.text('Reporte de Sucursales', 14, 22);
    doc.setFontSize(11); doc.text(`Fecha: ${new Date().toLocaleDateString()}`, 14, 30);
    const tableColumn = getTableHeaders(); const tableRows = filteredBranches.value.map(getBranchDataForExport);
    autoTable(doc, { head: [tableColumn], body: tableRows, startY: 35, theme: 'grid', styles: { fontSize: tableColumn.length > 12 ? 7 : 8, cellPadding: 1.5 }, headStyles: { fillColor: [41, 128, 185], textColor: [255, 255, 255], fontStyle: 'bold' }, alternateRowStyles: { fillColor: [245, 245, 245] }, margin: { left: 10, right: 10 } });
    doc.save('sucursales.pdf');
    mainStore.notify({ color: 'success', message: 'Exportado a PDF con éxito.' })
  } catch (error) { console.error('Error al generar PDF:', error); mainStore.notify({ color: 'danger', message: 'Error al generar PDF: ' + error.message }) }
};
const exportToCSV = () => {
  try {
    const headers = getTableHeaders(); let csvContent = "\uFEFF" + headers.join(',') + '\n'; // BOM para Excel
    filteredBranches.value.forEach(branch => {
      const row = getBranchDataForExport(branch);
      const formattedRow = row.map(cell => { if (cell === null || cell === undefined) return ''; cell = cell.toString(); if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) { return `"${cell.replace(/"/g, '""')}"`; } return cell; });
      csvContent += formattedRow.join(',') + '\n';
    });
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' }); saveAs(blob, 'sucursales.csv');
    mainStore.notify({ color: 'success', message: 'Exportado a CSV con éxito.' })
  } catch (error) { console.error('Error al generar CSV:', error); mainStore.notify({ color: 'danger', message: 'Error al generar CSV: ' + error.message }) }
};
const exportToExcel = () => {
  try {
    const headers = getTableHeaders(); const data = filteredBranches.value.map(getBranchDataForExport); data.unshift(headers);
    const ws = XLSX.utils.aoa_to_sheet(data);
    const columnWidths = headers.map((headerText) => { let width = 18; if (headerText === "ID") width = 5; if (headerText === "Dirección") width = 30; if (headerText === "Email") width = 25; return { wch: width }; });
    ws['!cols'] = columnWidths;
    const wb = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb, ws, "Sucursales"); XLSX.writeFile(wb, 'sucursales.xlsx');
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
    <p>¿Está seguro que desea desactivar la sucursal <strong>{{ currentBranch.name }}</strong>?</p>
    <p>Esta acción solo marcará la sucursal como inactiva.</p>
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
        Detalles Sucursal: {{ selectedBranchForView.name }}
    </template>
    <div v-if="selectedBranchForView.id" class="space-y-2 text-sm p-4">
      <p><strong>ID:</strong> {{ selectedBranchForView.id }}</p>
      <p><strong>Nombre:</strong> {{ selectedBranchForView.name }}</p>
      <p><strong>Teléfono:</strong> {{ selectedBranchForView.phone }}</p>
      <p><strong>Dirección:</strong> <span class="whitespace-pre-wrap">{{ selectedBranchForView.address }}</span></p>
      <p><strong>Email:</strong> {{ selectedBranchForView.email }}</p>
      <p><strong>Distrito:</strong> {{ selectedBranchForView.district }}</p>
      <p><strong>Municipio:</strong> {{ selectedBranchForView.municipality }}</p>
      <p><strong>Departamento:</strong> {{ selectedBranchForView.department }}</p>
      <p><strong>Activo:</strong> <span :class="selectedBranchForView.active ? 'text-green-600' : 'text-red-600'">{{ selectedBranchForView.active ? 'Sí' : 'No' }}</span></p>

      <div v-if="authStore.isSuperuser" class="pt-2 mt-2 border-t border-gray-200 dark:border-gray-700">
        <h3 class="text-md font-semibold mb-1 mt-2 text-gray-800 dark:text-gray-200">Información de Auditoría:</h3>
        <p><strong>Creado por:</strong> {{ selectedBranchForView.created_by_name || 'N/A' }} <span v-if="selectedBranchForView.created_by">(ID: {{ selectedBranchForView.created_by }})</span></p>
        <p><strong>Fecha de Creación:</strong> {{ selectedBranchForView.created_at }}</p>
        <p><strong>Modificado por:</strong> {{ selectedBranchForView.modified_by_name || 'N/A' }} <span v-if="selectedBranchForView.modified_by">(ID: {{ selectedBranchForView.modified_by }})</span></p>
        <p><strong>Fecha de Modificación:</strong> {{ selectedBranchForView.updated_at }}</p>
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
      v-if="authStore.hasPermission('branch.add_branch')"
      color="info" 
      :icon="mdiPlus" 
      label="Crear Sucursal" 
      @click="openCreate" 
      small 
    />
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
          <th scope="col" class="px-4 py-3 whitespace-nowrap text-gray-700 dark:text-gray-400">
            ID
            <BaseButton 
              :icon="sortIcon" 
              @click="toggleSortOrder" 
              small 
              class="ml-1 !p-1"
              :title="sortDescending ? 'Orden Descendente por ID' : 'Orden Ascendente por ID'" 
            />
          </th>
          <th scope="col" class="px-4 py-3">Nombre</th>
          <th scope="col" class="px-4 py-3">Teléfono</th>
          <th scope="col" class="px-4 py-3">Email</th>
          <th scope="col" class="px-4 py-3">Distrito</th>
          <th scope="col" class="px-4 py-3">Municipio</th>
          <th scope="col" class="px-4 py-3">Departamento</th>
          <th scope="col" class="px-4 py-3 text-center">Acciones</th>
        </tr>
        <tr class="bg-gray-100 dark:bg-gray-700">
          <td class="px-1 py-1 text-center">
             <BaseButton 
              :icon="mdiCloseCircleOutline" 
              @click="clearAllFilters"
              small 
              color="danger"
              outline
              class="!p-1"
              title="Limpiar filtros de columna"
            />
          </td>
          <td class="px-1 py-1">
            <FormControl type="text" v-model.lazy="nameFilter" placeholder="Filtrar..." class="text-xs min-w-[120px]" />
          </td>
          <td class="px-1 py-1"></td>
          <td class="px-1 py-1">
            <FormControl type="text" v-model.lazy="emailFilter" placeholder="Filtrar..." class="text-xs min-w-[120px]" />
          </td>
          <td class="px-1 py-1">
            <input list="district-datalist-branch" v-model.lazy="districtFilter" placeholder="Filtrar..." class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs min-w-[100px] text-gray-900 dark:text-gray-100" />
            <datalist id="district-datalist-branch">
              <option v-for="dist in uniqueDistricts" :key="dist" :value="dist"></option>
            </datalist>
          </td>
          <td class="px-1 py-1">
            <input list="municipality-datalist-branch" v-model.lazy="municipalityFilter" placeholder="Filtrar..." class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs min-w-[100px] text-gray-900 dark:text-gray-100" />
            <datalist id="municipality-datalist-branch">
              <option v-for="mun in uniqueMunicipalities" :key="mun" :value="mun"></option>
            </datalist>
          </td>
          <td class="px-1 py-1">
            <input list="department-datalist-branch" v-model.lazy="departmentFilter" placeholder="Filtrar..." class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs min-w-[100px] text-gray-900 dark:text-gray-100" />
            <datalist id="department-datalist-branch">
              <option v-for="dep in uniqueDepartments" :key="dep" :value="dep"></option>
            </datalist>
          </td>
          <td class="px-1 py-1 text-center">
          </td>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading && itemsPaginated.length === 0">
          <td colspan="8" class="text-center py-4">Cargando sucursales...</td>
        </tr>
        <tr v-else-if="itemsPaginated.length === 0">
          <td colspan="8" class="text-center py-4">No se encontraron sucursales que coincidan.</td>
        </tr>
        <tr v-for="branch in itemsPaginated" :key="branch.id"
          class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
          <td data-label="ID" class="px-4 py-2 font-medium text-gray-900 whitespace-nowrap dark:text-white">{{ branch.id }}</td>
          <td data-label="Nombre" class="px-4 py-2 font-medium text-gray-900 whitespace-nowrap dark:text-white">
            <span class="cursor-pointer hover:underline" @click="openDetailModal(branch)">{{ branch.name }}</span>
          </td>
          <td data-label="Teléfono" class="px-4 py-2">{{ branch.phone }}</td>
          <td data-label="Email" class="px-4 py-2">{{ branch.email }}</td>
          <td data-label="Distrito" class="px-4 py-2">{{ branch.district }}</td>
          <td data-label="Municipio" class="px-4 py-2">{{ branch.municipality }}</td>
          <td data-label="Departamento" class="px-4 py-2">{{ branch.department }}</td>
          <td class="px-4 py-2 whitespace-nowrap text-center" data-label="Acciones">
            <BaseButtons type="justify-center" no-wrap>
              <BaseButton 
                v-if="authStore.hasPermission('branch.change_branch')"
                color="info" :icon="mdiPencil" small title="Editar" @click="openEdit(branch)" 
              />
              <BaseButton 
                v-if="branch.active && authStore.hasPermission('branch.delete_branch')"
                color="danger" :icon="mdiTrashCan" small title="Desactivar" @click="openDelete(branch)" 
              />
              <BaseButton 
                color="light" outline :icon="mdiEye" small title="Ver Detalles" @click="openDetailModal(branch)" 
              />
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
      <small>Página {{ currentPageHuman }} de {{ numPages }} (Total: {{ filteredBranches.length }} sucursales)</small>
    </div>
  </div>
</template>

<style scoped>
/* Estilos para los inputs de filtro en la cabecera */
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