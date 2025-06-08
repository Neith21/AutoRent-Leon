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

const vehicles = ref([])
const loading = ref(false)

// --- Estados para filtros y orden ---
const searchTerm = ref('')
const plateFilter = ref('')
const brandFilter = ref('')
const modelFilter = ref('')
const yearFilter = ref('')
const statusFilter = ref('')
const branchFilter = ref('')
const sortDescending = ref(false)

const perPage = ref(10)
const currentPage = ref(0)

const restrictedSearchFields = [
  'created_by', 'created_by_name', 'created_at', 
  'modified_by', 'modified_by_name', 'updated_at'
];

const uniqueBrands = computed(() => {
  if (!vehicles.value) return [];
  return [...new Set(vehicles.value.map(v => v.brand).filter(Boolean))].sort();
});

const uniqueModels = computed(() => {
  if (!vehicles.value) return [];
  return [...new Set(vehicles.value.map(v => v.vehiclemodel).filter(Boolean))].sort();
});

const uniqueBranches = computed(() => {
  if (!vehicles.value) return [];
  return [...new Set(vehicles.value.map(v => v.branch).filter(Boolean))].sort();
});

const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear();
  const years = [];
  for (let y = currentYear + 1; y >= 1986; y--) {
    years.push(y);
  }
  return years;
});

const statusOptions = ref(['Disponible', 'En mantenimiento', 'En reparacion', 'Reservado', 'Alquilado']);


// --- Logica de filtrado y paginación actualizada ---
const filteredVehicles = computed(() => {
  let filtered = [...vehicles.value];

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter(vehicle => {
      if (authStore.isSuperuser) { // Usar getter del store
        return Object.values(vehicle).some(val => val && val.toString().toLowerCase().includes(term));
      } else {
        return Object.entries(vehicle).some(([key, val]) => {
          if (restrictedSearchFields.includes(key)) return false;
          return val && val.toString().toLowerCase().includes(term);
        });
      }
    });
  }

  if (plateFilter.value) {
    const term = plateFilter.value.toLowerCase();
    filtered = filtered.filter(v => v.plate && v.plate.toLowerCase().includes(term));
  }
  if (brandFilter.value) {
    const term = brandFilter.value.toLowerCase();
    filtered = filtered.filter(v => v.brand && v.brand.toLowerCase().includes(term));
  }
  if (modelFilter.value) {
    const term = modelFilter.value.toLowerCase();
    filtered = filtered.filter(v => v.vehiclemodel && v.vehiclemodel.toLowerCase().includes(term));
  }
  if (yearFilter.value) {
    filtered = filtered.filter(v => v.year && v.year.toString() === yearFilter.value.toString());
  }
  if (statusFilter.value) {
    filtered = filtered.filter(v => v.status && v.status === statusFilter.value);
  }
  if (branchFilter.value) {
    const term = branchFilter.value.toLowerCase();
    filtered = filtered.filter(v => v.branch && v.branch.toLowerCase().includes(term));
  }

  filtered.sort((a, b) => {
    if (sortDescending.value) { return b.id - a.id; }
    return a.id - b.id;
  });
  return filtered;
});

const itemsPaginated = computed(() =>
  filteredVehicles.value.slice(perPage.value * currentPage.value, perPage.value * (currentPage.value + 1))
)
const numPages = computed(() => Math.ceil(filteredVehicles.value.length / perPage.value))
const currentPageHuman = computed(() => currentPage.value + 1)
const pagesList = computed(() => Array.from({ length: numPages.value }, (_, i) => i))

watch([searchTerm, plateFilter, brandFilter, modelFilter, yearFilter, statusFilter, branchFilter, sortDescending], () => {
  currentPage.value = 0;
});

const toggleSortOrder = () => sortDescending.value = !sortDescending.value;
const sortIcon = computed(() => sortDescending.value ? mdiSortDescending : mdiSortAscending);

const clearAllFilters = () => {
  searchTerm.value = ''; plateFilter.value = ''; brandFilter.value = '';
  modelFilter.value = ''; yearFilter.value = ''; statusFilter.value = '';
  branchFilter.value = '';
};

const isDeleteModalActive = ref(false)
const isDetailModalActive = ref(false)
const isImageGalleryModalActive = ref(false)
const currentVehicle = ref({})
const selectedVehicleForView = ref({})

const API_URL = import.meta.env.VITE_API_URL

const fetchVehicles = async () => {
  if (!authStore.authToken) return; // Usar token del store
  loading.value = true;
  try {
    const config = { headers: { 'Authorization': `Bearer ${authStore.authToken}` } }
    const response = await axios.get(`${API_URL}vehicle`, config)
    vehicles.value = response.data?.data || []
  } catch (e) {
    console.error('Error obteniendo vehículos:', e)
    mainStore.notify({ color: 'danger', message: 'Error obteniendo vehículos: ' + (e.response?.data?.message || e.message) })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (authStore.checkLoggedIn()) {
      await authStore.fetchUserPermissions();
  }
  await fetchVehicles();
})

const openCreate = () => router.push({ name: 'vehicleCreate' });
const openEdit = (vehicle) => router.push({ name: 'vehicleEdit', params: { id: vehicle.id } });

const openDelete = (vehicle) => { currentVehicle.value = vehicle; isDeleteModalActive.value = true; };
const openDetailModal = (vehicle) => { selectedVehicleForView.value = vehicle; isDetailModalActive.value = true; };
const openImageGalleryModal = (vehicle) => { selectedVehicleForView.value = vehicle; isImageGalleryModalActive.value = true; };

const getAuthConfig = () => ({ headers: { 'Authorization': `Bearer ${authStore.authToken}` } });

const confirmDelete = async () => {
  loading.value = true;
  try {
    await axios.put(`${API_URL}vehicle/delete/${currentVehicle.value.id}`, {}, getAuthConfig());
    mainStore.notify({ color: 'success', message: 'Vehículo desactivado exitosamente.' })
    await fetchVehicles()
  } catch (e) {
    console.error('Error desactivando vehículo:', e)
    mainStore.notify({ color: 'danger', message: 'Error desactivando vehículo: ' + (e.response?.data?.message || e.message) })
  } finally {
    isDeleteModalActive.value = false; loading.value = false;
  }
};

const getTableHeaders = () => {
  const headers = ["ID", "Placa", "Marca", "Modelo", "Categoría", "Sucursal", "Color", "Año", "Motor (C.C.)", "Tipo Motor", "N° Motor", "VIN", "Asientos", "Precio Diario ($)", "Descripción", "Estado", "Primera Imagen (URL)"];
  if (authStore.isSuperuser) { // Usar getter del store
    headers.push("Creado por", "Fecha Creación", "Modificado por", "Fecha Modificación");
  }
  return headers;
};
const getVehicleDataForExport = (vehicle) => {
  const data = [
    vehicle.id || '', vehicle.plate || '', vehicle.brand || '', vehicle.vehiclemodel || '',
    vehicle.vehiclecategory || '', vehicle.branch || '',  vehicle.color || '', vehicle.year || '', vehicle.engine || '',
    vehicle.engine_type || '', vehicle.engine_number || '', vehicle.vin || '', vehicle.seat_count || '',
    vehicle.daily_price !== null && vehicle.daily_price !== undefined ? vehicle.daily_price : '',
    vehicle.description || '', vehicle.status || '', (vehicle.images && vehicle.images.length > 0) ? vehicle.images[0] : ''
  ];
  if (authStore.isSuperuser) { // Usar getter del store
    data.push(
      vehicle.created_by_name || '', vehicle.created_at || '',
      vehicle.modified_by_name || '', vehicle.updated_at || ''
    );
  }
  return data;
};

const exportToPDF = () => {
  try {
    const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
    doc.setFontSize(18); doc.text('Reporte de Vehículos', 14, 22);
    doc.setFontSize(11); doc.text(`Fecha: ${new Date().toLocaleDateString()}`, 14, 30);
    const tableColumn = getTableHeaders(); const tableRows = filteredVehicles.value.map(getVehicleDataForExport); 
    autoTable(doc, { head: [tableColumn], body: tableRows, startY: 35, theme: 'grid', styles: { fontSize: tableColumn.length > 15 ? 6 : 7, cellPadding: 1.5 }, headStyles: { fillColor: [41, 128, 185], textColor: [255, 255, 255], fontStyle: 'bold' }, alternateRowStyles: { fillColor: [245, 245, 245] }, margin: { left: 10, right: 10 } });
    doc.save('vehiculos.pdf');
    mainStore.notify({ color: 'success', message: 'Exportado a PDF con éxito.' })
  } catch (error) { console.error('Error al generar PDF:', error); mainStore.notify({ color: 'danger', message: 'Error al generar PDF: ' + error.message }) }
};
const exportToCSV = () => {
  try {
    const headers = getTableHeaders(); let csvContent = "\uFEFF" + headers.join(',') + '\n'; // BOM para Excel
    filteredVehicles.value.forEach(vehicle => {
      const row = getVehicleDataForExport(vehicle); 
      const formattedRow = row.map(cell => { if (cell === null || cell === undefined) return ''; cell = cell.toString(); if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) { return `"${cell.replace(/"/g, '""')}"`; } return cell; });
      csvContent += formattedRow.join(',') + '\n';
    });
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' }); saveAs(blob, 'vehiculos.csv');
    mainStore.notify({ color: 'success', message: 'Exportado a CSV con éxito.' })
  } catch (error) { console.error('Error al generar CSV:', error); mainStore.notify({ color: 'danger', message: 'Error al generar CSV: ' + error.message }) }
};
const exportToExcel = () => {
  try {
    const headers = getTableHeaders(); const data = filteredVehicles.value.map(getVehicleDataForExport); data.unshift(headers);
    const ws = XLSX.utils.aoa_to_sheet(data);
    const columnWidths = headers.map((headerText, i) => { let width = 15; if (headerText === "ID") width = 5; if (headerText === "Primera Imagen (URL)") width = 30; if (headerText === "Descripción") width = 25; return { wch: width }; });
    ws['!cols'] = columnWidths;
    const wb = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb, ws, "Vehiculos"); XLSX.writeFile(wb, 'vehiculos.xlsx');
    mainStore.notify({ color: 'success', message: 'Exportado a Excel con éxito.' })
  } catch (error) { console.error('Error al generar Excel:', error); mainStore.notify({ color: 'danger', message: 'Error al generar Excel: ' + error.message }) }
};

</script>

<template>
  <div v-if="mainStore && mainStore.notification && mainStore.notification.show" class="sticky top-0 z-50 px-4 md:px-6">
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
    <p>¿Está seguro que desea desactivar el vehículo con placa <strong>{{ currentVehicle.plate }}</strong>?</p>
    <p>Esta acción solo marcará el vehículo como inactivo.</p>
    <div class="mt-6 flex justify-end space-x-2">
      <BaseButton color="whiteDark" label="Cancelar" @click="isDeleteModalActive = false" :disabled="loading" />
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
        Detalles Vehículo: {{ selectedVehicleForView.plate }}
    </template>
    <div v-if="selectedVehicleForView.id" class="space-y-2 text-sm p-4">
      <p><strong>ID:</strong> {{ selectedVehicleForView.id }}</p>
      <p><strong>Placa:</strong> {{ selectedVehicleForView.plate }}</p>
      <p><strong>Marca:</strong> {{ selectedVehicleForView.brand }}</p>
      <p><strong>Modelo:</strong> {{ selectedVehicleForView.vehiclemodel }}</p>
      <p><strong>Categoría:</strong> {{ selectedVehicleForView.vehiclecategory }}</p>
      <p><strong>Sucursal:</strong> {{ selectedVehicleForView.branch || 'N/A' }}</p>
      <p><strong>Año:</strong> {{ selectedVehicleForView.year }}</p>
      <p><strong>Color:</strong> {{ selectedVehicleForView.color }}</p>
      <p><strong>Motor (C.C.):</strong> {{ selectedVehicleForView.engine }}</p>
      <p><strong>Tipo Motor:</strong> {{ selectedVehicleForView.engine_type }}</p>
      <p><strong>N° Motor:</strong> {{ selectedVehicleForView.engine_number }}</p>
      <p><strong>VIN:</strong> {{ selectedVehicleForView.vin }}</p>
      <p><strong>Asientos:</strong> {{ selectedVehicleForView.seat_count }}</p>
      <p><strong>Precio Diario:</strong> ${{ Number(selectedVehicleForView.daily_price || 0).toFixed(2) }}</p>
      <p><strong>Descripción:</strong> <span class="whitespace-pre-wrap">{{ selectedVehicleForView.description || 'N/A' }}</span></p>
      <p><strong>Estado:</strong> {{ selectedVehicleForView.status }}</p>
      <p><strong>Activo:</strong> <span :class="selectedVehicleForView.active ? 'text-green-600' : 'text-red-600'">{{ selectedVehicleForView.active ? 'Sí' : 'No' }}</span></p>

      <div v-if="authStore.isSuperuser" class="pt-2 mt-2 border-t border-gray-200 dark:border-gray-700">
        <h3 class="text-md font-semibold mb-1 mt-2 text-gray-800 dark:text-gray-200">Información de Auditoría:</h3>
        <p><strong>Creado por:</strong> {{ selectedVehicleForView.created_by_name || 'N/A' }} <span v-if="selectedVehicleForView.created_by">(ID: {{ selectedVehicleForView.created_by }})</span></p>
        <p><strong>Fecha de Creación:</strong> {{ selectedVehicleForView.created_at }}</p>
        <p><strong>Modificado por:</strong> {{ selectedVehicleForView.modified_by_name || 'N/A' }} <span v-if="selectedVehicleForView.modified_by">(ID: {{ selectedVehicleForView.modified_by }})</span></p>
        <p><strong>Fecha de Modificación:</strong> {{ selectedVehicleForView.updated_at }}</p>
      </div>
    </div>
    <template #footer>
      <BaseButtons>
        <BaseButton label="Cerrar" color="info" @click="isDetailModalActive = false" />
      </BaseButtons>
    </template>
  </CardBoxModal>

  <CardBoxModal v-model="isImageGalleryModalActive" :title="`Imágenes de: ${selectedVehicleForView.plate}`">
    <div v-if="selectedVehicleForView.images && selectedVehicleForView.images.length > 0">
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 max-h-[70vh] overflow-y-auto p-1">
        <div v-for="(imgUrl, index) in selectedVehicleForView.images" :key="index"
          class="border dark:border-gray-700 rounded-lg overflow-hidden aspect-video bg-gray-100 dark:bg-gray-800"> 
          <img :src="imgUrl" :alt="`Imagen ${index + 1} de ${selectedVehicleForView.plate}`"
            class="w-full h-full object-contain">
        </div>
      </div>
    </div>
    <p v-else class="text-gray-500 dark:text-gray-400 text-center py-4">No hay imágenes disponibles para este vehículo.</p>
    <template #footer>
      <BaseButtons>
        <BaseButton label="Cerrar" color="info" @click="isImageGalleryModalActive = false" />
      </BaseButtons>
    </template>
  </CardBoxModal>

  <div class="mb-6 flex flex-col md:flex-row items-center justify-between gap-4 px-4 md:px-0">
    <BaseButton 
      v-if="authStore.hasPermission('vehicle.add_vehicle')"
      color="info" 
      :icon="mdiPlus" 
      label="Crear Vehículo" 
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
          <th scope="col" class="px-2 py-3 text-center">
            <BaseButton 
              :icon="sortIcon" 
              @click="toggleSortOrder" 
              small 
              :class="['ml-1 !p-1 text-current hover:text-blue-600 dark:hover:text-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-300 dark:focus:ring-blue-500 rounded']"
              :title="sortDescending ? 'Orden Descendente (ID)' : 'Orden Ascendente (ID)'"
            />
          </th> 
          <th scope="col" class="px-4 py-3">Placa</th>
          <th scope="col" class="px-4 py-3">Marca</th>
          <th scope="col" class="px-4 py-3">Modelo</th>
          <th scope="col" class="px-4 py-3">Sucursal</th>
          <th scope="col" class="px-4 py-3">Año</th>
          <th scope="col" class="px-4 py-3">Color</th>
          <th scope="col" class="px-4 py-3">Precio Diario</th>
          <th scope="col" class="px-4 py-3">Estado</th>
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
              title="Limpiar todos los filtros de columna y búsqueda global"
            />
          </td>
          <td class="px-1 py-1">
            <FormControl type="text" v-model.lazy="plateFilter" placeholder="Filtrar..." class="text-xs min-w-[100px]" />
          </td>
          <td class="px-1 py-1">
            <input list="brand-datalist" v-model.lazy="brandFilter" placeholder="Filtrar..." class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs min-w-[100px] text-gray-900 dark:text-gray-100" />
            <datalist id="brand-datalist">
              <option v-for="brand in uniqueBrands" :key="brand" :value="brand"></option>
            </datalist>
          </td>
          <td class="px-1 py-1">
            <input list="model-datalist" v-model.lazy="modelFilter" placeholder="Filtrar..." class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs min-w-[100px] text-gray-900 dark:text-gray-100" />
            <datalist id="model-datalist">
              <option v-for="modelItem in uniqueModels" :key="modelItem" :value="modelItem"></option>
            </datalist>
          </td>
          <td class="px-1 py-1">
             <input list="branch-datalist" v-model.lazy="branchFilter" placeholder="Filtrar..." class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs min-w-[120px] text-gray-900 dark:text-gray-100" />
            <datalist id="branch-datalist">
              <option v-for="branch in uniqueBranches" :key="branch" :value="branch"></option>
            </datalist>
          </td>
          <td class="px-1 py-1">
            <select v-model="yearFilter" class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs min-w-[80px] text-gray-900 dark:text-gray-100">
              <option value="">Todos</option>
              <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}</option>
            </select>
          </td>
          <td class="px-1 py-1"></td>
          <td class="px-1 py-1"></td>
          <td class="px-1 py-1">
            <select v-model="statusFilter" class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs min-w-[120px] text-gray-900 dark:text-gray-100">
              <option value="">Todos</option>
              <option v-for="status in statusOptions" :key="status" :value="status">{{ status }}</option>
            </select>
          </td>
          <td class="px-1 py-1"></td>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading && itemsPaginated.length === 0">
          <td colspan="8" class="text-center py-4">Cargando vehículos...</td>
        </tr>
        <tr v-else-if="itemsPaginated.length === 0">
          <td colspan="8" class="text-center py-4">No se encontraron vehículos que coincidan con los filtros aplicados.</td>
        </tr>
        <tr v-for="vehicle in itemsPaginated" :key="vehicle.id"
          class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
          <td class="px-2 py-2 w-20">
            <img v-if="vehicle.images && vehicle.images.length > 0" :src="vehicle.images[0]"
              :alt="`Imagen de ${vehicle.plate}`" class="w-16 h-10 object-cover rounded cursor-pointer"
              @click="openImageGalleryModal(vehicle)" loading="lazy" />
            <div v-else
              class="w-16 h-10 bg-gray-200 dark:bg-gray-700 rounded flex items-center justify-center text-xs text-gray-400 dark:text-gray-500 cursor-pointer"
              @click="openImageGalleryModal(vehicle)">
              S/Img
            </div>
          </td>
          <td data-label="Placa" class="px-4 py-2 font-medium text-gray-900 whitespace-nowrap dark:text-white">
            <span class="cursor-pointer hover:underline" @click="openDetailModal(vehicle)">{{ vehicle.plate }}</span>
          </td>
          <td data-label="Marca" class="px-4 py-2">{{ vehicle.brand }}</td>
          <td data-label="Modelo" class="px-4 py-2">{{ vehicle.vehiclemodel }}</td>
          <td data-label="Sucursal" class="px-4 py-2">{{ vehicle.branch }}</td>
          <td data-label="Año" class="px-4 py-2">{{ vehicle.year }}</td>
          <td data-label="Color" class="px-4 py-2">{{ vehicle.color }}</td>
          <td data-label="Precio Diario" class="px-4 py-2">${{ Number(vehicle.daily_price || 0).toFixed(2) }}</td>
          <td data-label="Estado" class="px-4 py-2">
            <span :class="{
              'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300': vehicle.status === 'Disponible',
              'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300': vehicle.status === 'Alquilado' || vehicle.status === 'Reservado',
              'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300': vehicle.status === 'En mantenimiento',
              'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300': vehicle.status === 'En reparacion' || vehicle.status === 'Fuera de servicio'
            }" class="text-xs font-medium px-2.5 py-0.5 rounded-full whitespace-nowrap">
              {{ vehicle.status }}
            </span>
          </td>
          <td class="px-4 py-2 whitespace-nowrap text-center" data-label="Acciones">
            <BaseButtons type="justify-center" no-wrap>
              <BaseButton 
                v-if="authStore.hasPermission('vehicle.change_vehicle')"
                color="info" :icon="mdiPencil" small title="Editar" @click="openEdit(vehicle)" 
              />
              <BaseButton 
                v-if="vehicle.active && authStore.hasPermission('vehicle.delete_vehicle')"
                color="danger" :icon="mdiTrashCan" small title="Desactivar" @click="openDelete(vehicle)" 
              />
              <BaseButton 
                color="light" outline :icon="mdiEye" small title="Ver Detalles" @click="openDetailModal(vehicle)" 
              />
            </BaseButtons>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="p-3 lg:px-6 border-t border-gray-100 dark:border-slate-800" v-if="numPages > 1">
    <div class="flex flex-col sm:flex-row items-center justify-between gap-3">
      <BaseButtons>
        <BaseButton v-for="page in pagesList" :key="page" :active="page === currentPage" :label="page + 1"
          :color="page === currentPage ? 'lightDark' : 'whiteDark'" small @click="currentPage = page" />
      </BaseButtons>
      <small>Página {{ currentPageHuman }} de {{ numPages }} (Total: {{ filteredVehicles.length }} vehículos)</small>
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
  table:not(.keep-desktop-layout) td::before { content: attr(data-label); float: left; font-weight: bold; text-transform: uppercase; }
}
</style>