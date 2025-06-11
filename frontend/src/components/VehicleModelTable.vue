<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import {
  mdiTrashCan, mdiPencil, mdiPlus, mdiMagnify, mdiFilePdfBox, mdiFileExcel,
  mdiFileDelimited, mdiEye, mdiFilterVariant, mdiSortAscending, mdiSortDescending, mdiCloseCircleOutline
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

const API_URL = import.meta.env.VITE_API_URL;

const vehicleModels = ref([])
const loading = ref(false)

// Estados para filtros y orden
const searchTerm = ref('')
const nameFilter = ref('')
const brandNameFilter = ref('')
const sortDescending = ref(false)

// Estados para modales
const isModalActive = ref(false)
const isDeleteModalActive = ref(false)
const isDetailModalActive = ref(false)
const modalTitle = ref('')
const currentVehicleModel = ref({})
const selectedVehicleModelForView = ref({})

const form = ref({
  id: null,
  name: '',
  brand_id: null,
})

// brandsForSelect: Para el <select> en el modal de Crear/Editar
const brandsForSelect = ref([])

const fetchBrandsForModal = async () => {
  if (!authStore.authToken) return;
  try {
    const config = { headers: { Authorization: `Bearer ${authStore.authToken}` } };
    const response = await axios.get(`${API_URL}brand`, config);
    const activeBrands = response.data?.data?.filter(b => b.active !== false) || [];
    
    brandsForSelect.value = activeBrands.map(brand => ({
      id: brand.id,
      label: brand.name || 'Marca Desconocida'
    }));
  } catch (e) {
    console.error("Error fetching brands for modal select:", e);
    mainStore.notify({ color: 'danger', message: 'Error cargando marcas para el formulario.' });
  }
};

const uniqueBrandNamesForTableFilter = computed(() => {
  if (!vehicleModels.value || vehicleModels.value.length === 0) return [];
  return [...new Set(vehicleModels.value.map(model => model.brand).filter(Boolean))].sort();
});


const perPage = ref(5)
const currentPage = ref(0)

const restrictedSearchFields = [
  'created_by', 'created_by_name', 'created_at',
  'modified_by', 'modified_by_name', 'updated_at', 'brand_id'
];

const filteredVehicleModels = computed(() => {
  let filtered = [...vehicleModels.value];
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter(model => 
      authStore.isSuperuser ?
      Object.values(model).some(val => val?.toString().toLowerCase().includes(term)) :
      Object.entries(model).some(([key, val]) => 
        !restrictedSearchFields.includes(key) && val?.toString().toLowerCase().includes(term)
      )
    );
  }
  if (nameFilter.value) {
    filtered = filtered.filter(m => m.name && m.name.toLowerCase().includes(nameFilter.value.toLowerCase()));
  }
  if (brandNameFilter.value) {
    filtered = filtered.filter(m => m.brand && m.brand.toLowerCase().includes(brandNameFilter.value.toLowerCase()));
  }
  filtered.sort((a, b) => {
    const valA = a.id; const valB = b.id;
    if (valA === null || valA === undefined) return 1; if (valB === null || valB === undefined) return -1;
    return sortDescending.value ? (valB < valA ? -1 : (valB > valA ? 1 : 0)) : (valA < valB ? -1 : (valA > valB ? 1 : 0));
  });
  return filtered;
});

const itemsPaginated = computed(() =>
  filteredVehicleModels.value.slice(perPage.value * currentPage.value, perPage.value * (currentPage.value + 1))
)
const numPages = computed(() => Math.ceil(filteredVehicleModels.value.length / perPage.value))
const currentPageHuman = computed(() => currentPage.value + 1)
const pagesList = computed(() => Array.from({ length: numPages.value }, (_, i) => i))

watch([searchTerm, nameFilter, brandNameFilter, sortDescending], () => {
  currentPage.value = 0;
});

const toggleSortOrder = () => sortDescending.value = !sortDescending.value;
const sortIcon = computed(() => sortDescending.value ? mdiSortDescending : mdiSortAscending);

const clearColumnFilters = () => {
  nameFilter.value = '';
  brandNameFilter.value = ''; // Limpiar el filtro de nombre de marca
};
const clearAllFilters = () => {
  searchTerm.value = '';
  clearColumnFilters();
};

const fetchVehicleModels = async () => {
  if (!authStore.authToken) return; loading.value = true;
  try {
    const configAxios = { headers: { 'Authorization': `Bearer ${authStore.authToken}` } }
    const response = await axios.get(`${API_URL}vehiclemodel`, configAxios)
    vehicleModels.value = response.data?.data || []
  } catch (e) {
    console.error('Error obteniendo modelos:', e);
    mainStore.notify({ color: 'danger', message: `Error obteniendo modelos: ${e.response?.data?.message || e.message}` });
  } finally { loading.value = false; }
}

onMounted(async () => {
  if (authStore.checkLoggedIn()) {
    await authStore.fetchUserPermissions();
  }
  await fetchBrandsForModal();
  await fetchVehicleModels();
})

const openCreate = () => {
  modalTitle.value = 'Crear Modelo de Vehículo';
  form.value = { id: null, name: '', brand_id: null };
  isModalActive.value = true;
}

const openEdit = (model) => {
  modalTitle.value = 'Editar Modelo de Vehículo';
  form.value.id = model.id;
  form.value.name = model.name;
  form.value.brand_id = model.brand_id || null; 
  if (model.brand_id === undefined && model.brand) {
     console.warn(`'brand_id' no encontrado en el objeto modelo. Intentando buscar ID basado en nombre de marca: ${model.brand}`);
     const brandObj = brandsForSelect.value.find(b => b.label === model.brand);
     form.value.brand_id = brandObj ? brandObj.id : null;
     if (!form.value.brand_id && model.brand) {
        mainStore.notify({color: 'warning', message: `No se pudo preseleccionar la marca "${model.brand}" para edición. Verifique que la marca exista en el selector.`});
     }
  }
  isModalActive.value = true;
}

const openDelete = (model) => { currentVehicleModel.value = model; isDeleteModalActive.value = true; }
const openDetailModal = (model) => { selectedVehicleModelForView.value = model; isDetailModalActive.value = true; };

const axiosBaseConfig = () => ({
    headers: { 
        'Content-Type': 'application/json', 
        'Authorization': `Bearer ${authStore.authToken}` 
    } 
});

const handleSubmit = async () => {
  loading.value = true;
  let url = `${API_URL}vehiclemodel`;
  let method = 'post';
  if (!form.value.name || form.value.brand_id === null) {
    mainStore.notify({ color: 'danger', message: 'Nombre del modelo y Marca son requeridos.' });
    loading.value = false; return;
  }
  const payload = { name: form.value.name, brand_id: form.value.brand_id };
  if (form.value.id) { url += `/${form.value.id}`; method = 'put'; }
  try {
    method === 'put' ? await axios.put(url, payload, axiosBaseConfig()) : await axios.post(url, payload, axiosBaseConfig());
    mainStore.notify({ color: 'success', message: `Modelo ${form.value.id ? 'actualizado' : 'creado'} correctamente.` });
    isModalActive.value = false; await fetchVehicleModels();
  } catch (e) {
    console.error(`Error ${method === 'put' ? 'actualizando' : 'creando'} modelo:`, e.response || e);
    mainStore.notify({ color: 'danger', message: `Error: ${e.response?.data?.message || e.message}` });
  } finally { loading.value = false; }
}

const confirmDelete = async () => {
  loading.value = true;
  try {
    await axios.put(`${API_URL}vehiclemodel/delete/${currentVehicleModel.value.id}`, {}, axiosBaseConfig());
    mainStore.notify({ color: 'success', message: 'Modelo desactivado correctamente.' });
    isDeleteModalActive.value = false; await fetchVehicleModels();
  } catch (e) {
    console.error('Error desactivando modelo:', e.response || e);
    mainStore.notify({ color: 'danger', message: `Error al desactivar: ${e.response?.data?.message || e.message}` });
  } finally { loading.value = false; }
}

const getTableHeadersForExport = () => {
  const headers = ["ID", "Nombre Modelo", "Marca", "Activo"];
  if (authStore.isSuperuser) {
    headers.push("Creado por (Nombre)", "Fecha Creación", "Modificado por (Nombre)", "Fecha Modificación");
  }
  return headers;
};
const getVehicleModelDataForExport = (model) => {
  const data = [
    model.id || '', 
    model.name || '', 
    model.brand || '',
    model.active ? 'Sí' : 'No'
  ];
  if (authStore.isSuperuser) {
    data.push(
      model.created_by_name || 'N/A', 
      model.created_at || 'N/A', 
      model.modified_by_name || 'N/A', 
      model.updated_at || 'N/A'
    );
  }
  return data;
};

const exportToPDF = () => {
  try {
    const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
    doc.setFontSize(18); doc.text('Reporte de Modelos de Vehículo', 14, 22);
    doc.setFontSize(11); doc.text(`Fecha: ${new Date().toLocaleDateString()}`, 14, 30);
    const tableColumn = getTableHeadersForExport();
    const tableRows = filteredVehicleModels.value.map(getVehicleModelDataForExport);
    autoTable(doc, { head: [tableColumn], body: tableRows, startY: 35, theme: 'grid', styles: { fontSize: tableColumn.length > 6 ? 7 : 8, cellPadding: 1.5 }, headStyles: { fillColor: [41, 128, 185], textColor: [255, 255, 255], fontStyle: 'bold' }, alternateRowStyles: { fillColor: [245, 245, 245] }, margin: { left: 10, right: 10 } });
    doc.save('modelos_vehiculo.pdf');
    mainStore.notify({ color: 'success', message: 'Exportado a PDF con éxito.' });
  } catch (error) { mainStore.notify({ color: 'danger', message: 'Error al generar PDF: ' + error.message }); }
}
const exportToCSV = () => {
  try {
    const headers = getTableHeadersForExport();
    let csvContent = "\uFEFF" + headers.join(',') + '\n';
    filteredVehicleModels.value.forEach(model => {
      const row = getVehicleModelDataForExport(model);
      csvContent += row.map(cell => { if (cell === null || cell === undefined) return ''; cell = cell.toString(); return (cell.includes(',') || cell.includes('"') || cell.includes('\n')) ? `"${cell.replace(/"/g, '""')}"` : cell; }).join(',') + '\n';
    });
    saveAs(new Blob([csvContent], { type: 'text/csv;charset=utf-8;' }), 'modelos_vehiculo.csv');
    mainStore.notify({ color: 'success', message: 'Exportado a CSV con éxito.' });
  } catch (error) { mainStore.notify({ color: 'danger', message: 'Error al generar CSV: ' + error.message }); }
}
const exportToExcel = () => {
 try {
    const headers = getTableHeadersForExport();
    const dataForSheet = filteredVehicleModels.value.map(getVehicleModelDataForExport);
    const wsData = [headers, ...dataForSheet];
    const ws = XLSX.utils.aoa_to_sheet(wsData);
    const columnWidths = headers.map(header => {
        let maxLength = header.length;
        dataForSheet.forEach(row => {
            const cellValue = row[headers.indexOf(header)];
            if (cellValue && cellValue.toString().length > maxLength) { maxLength = cellValue.toString().length; }
        });
        return { wch: Math.min(Math.max(maxLength, 10), 50) };
    });
    ws['!cols'] = columnWidths;
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "ModelosVehiculo");
    XLSX.writeFile(wb, 'modelos_vehiculo.xlsx');
    mainStore.notify({ color: 'success', message: 'Exportado a Excel con éxito.' });
  } catch (error) { mainStore.notify({ color: 'danger', message: 'Error al generar Excel: ' + error.message }); }
}

</script>

<template>
  <div v-if="mainStore.notification && mainStore.notification.show" class="fixed top-4 right-4 z-[100] w-auto max-w-md">
    <NotificationBar
      v-model="mainStore.notification.show"
      :color="mainStore.notification.color"
      :icon="mainStore.notification.icon"
      @dismiss="mainStore.dismissNotification()"
      class="shadow-lg"
    >
      <span v-html="mainStore.notification.message?.replace(/\n/g, '<br>')"></span>
    </NotificationBar>
  </div>

  <CardBoxModal v-model="isModalActive" :title="modalTitle">
    <form @submit.prevent="handleSubmit">
      <div class="space-y-4 px-4 py-2">
        <div>
          <label for="brand_id_form_modal_html" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Marca del Modelo <span class="text-red-500">*</span>
          </label>
          <select 
            v-model="form.brand_id" 
            id="brand_id_form_modal_html" 
            name="brand_id_form_modal_html" 
            required 
            class="mt-1 block w-full py-2 px-3 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-gray-900 dark:text-gray-100"
          >
            <option :value="null" disabled>Seleccione una marca</option>
            <option v-for="brand in brandsForSelect" :key="brand.id" :value="brand.id">
              {{ brand.label }}
            </option>
          </select>
        </div>
        <div>
          <label for="name_form_modal_html" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Nombre del Modelo <span class="text-red-500">*</span>
          </label>
          <input 
            v-model="form.name" 
            id="name_form_modal_html" 
            type="text" 
            name="name_form_modal_html" 
            required 
            placeholder="Ej: Corolla, Hilux"
            class="mt-1 block w-full py-2 px-3 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-gray-900 dark:text-gray-100"
          />
        </div>
      </div>
      <div class="mt-6 px-4 py-3 flex justify-end space-x-2">
        <BaseButton 
          label="Cancelar" 
          color="whiteDark" 
          @click="isModalActive = false" 
          :disabled="loading" 
        />
        <BaseButton 
          :label="form.id ? (loading ? 'Actualizando...' : 'Actualizar Modelo') : (loading ? 'Creando...' : 'Crear Modelo')" 
          color="info" 
          type="submit" 
          :disabled="loading || !form.name || form.brand_id === null" 
        />
      </div>
    </form>
  </CardBoxModal>

  <CardBoxModal v-model="isDeleteModalActive" title="Confirmar Desactivación">
    <p>¿Está seguro que desea desactivar el modelo de vehículo <strong>{{ currentVehicleModel.name }} ({{ currentVehicleModel.brand }})</strong>?</p>
    <p class="text-sm text-red-500 mt-2">Atención: Esta acción no se podrá realizar si el modelo tiene vehículos asociados.</p>
     <div class="mt-6 flex justify-end space-x-2">
        <BaseButton 
            label="Cancelar" 
            color="whiteDark" 
            outline
            @click="isDeleteModalActive = false" 
            :disabled="loading" 
        />
        <BaseButton 
            :label="loading ? 'Desactivando...' : 'Eliminar'"
            color="danger" 
            @click="confirmDelete" 
            :disabled="loading" 
        />
    </div>
  </CardBoxModal>

  <CardBoxModal v-model="isDetailModalActive">
    <template #title>
      Detalles: {{ selectedVehicleModelForView.name }} (<strong class="font-semibold">{{ selectedVehicleModelForView.brand }}</strong>)
    </template>
    <div v-if="selectedVehicleModelForView.id" class="space-y-2 text-sm p-4">
      <p><strong>ID:</strong> {{ selectedVehicleModelForView.id }}</p>
      <p><strong>Nombre del Modelo:</strong> {{ selectedVehicleModelForView.name }}</p>
      <p><strong>Marca:</strong> <strong class="font-semibold">{{ selectedVehicleModelForView.brand }}</strong> (ID Marca: {{ selectedVehicleModelForView.brand_id }})</p>
      <p><strong>Activo:</strong> <span :class="selectedVehicleModelForView.active ? 'text-green-600' : 'text-red-600'">{{ selectedVehicleModelForView.active ? 'Sí' : 'No' }}</span></p>
      <div v-if="authStore.isSuperuser" class="pt-2 mt-2 border-t border-gray-200 dark:border-gray-700">
        <h3 class="text-md font-semibold mb-1 mt-2 text-gray-800 dark:text-gray-200">Información de Auditoría:</h3>
        <p><strong>Creado por:</strong> {{ selectedVehicleModelForView.created_by_name || 'N/A' }} <span v-if="selectedVehicleModelForView.created_by">(ID: {{ selectedVehicleModelForView.created_by }})</span></p>
        <p><strong>Fecha de Creación:</strong> {{ selectedVehicleModelForView.created_at }}</p>
        <p><strong>Modificado por:</strong> {{ selectedVehicleModelForView.modified_by_name || 'N/A' }} <span v-if="selectedVehicleModelForView.modified_by">(ID: {{ selectedVehicleModelForView.modified_by }})</span></p>
        <p><strong>Fecha de Modificación:</strong> {{ selectedVehicleModelForView.updated_at }}</p>
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
        v-if="authStore.hasPermission('vehiclemodel.add_vehiclemodel')"
        color="info" 
        :icon="mdiPlus" 
        label="Crear Modelo" 
        @click="openCreate" 
        small 
    />
    <div class="flex items-center gap-2 w-full md:w-auto">
      <div class="relative flex-grow md:flex-grow-0">
        <FormControl v-model="searchTerm" placeholder="Búsqueda rápida..." :icon="mdiMagnify" />
      </div>
      <BaseButton
              :icon="mdiFilterVariant"
              @click="clearAllFilters"
              small
              color="info" 
              outline
              class="!p-1"
              title="Limpiar búsqueda global y todos los filtros de columna"
            />
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
          <th scope="col" class="px-4 py-3">Nombre Modelo</th>
          <th scope="col" class="px-4 py-3">Marca</th>
          <th scope="col" class="px-4 py-3 text-center">Activo</th>
          <th v-if="authStore.isSuperuser" scope="col" class="px-4 py-3">Creado por</th>
          <th v-if="authStore.isSuperuser" scope="col" class="px-4 py-3">F. Creación</th>
          <th scope="col" class="px-4 py-3 text-center">Acciones</th>
        </tr>
        <tr class="bg-gray-100 dark:bg-gray-700">
          <td class="px-1 py-1 text-center">
            <BaseButton
              :icon="mdiCloseCircleOutline"
              @click="clearColumnFilters"
              small
              color="danger"
              outline
              class="!p-1"
              title="Limpiar filtros de columna (Nombre, Marca)"
            />
          </td>
          <td class="px-1 py-1">
            <FormControl type="text" v-model.lazy="nameFilter" placeholder="Filtrar nombre..." class="text-xs min-w-[150px]" />
          </td>
          <td class="px-1 py-1">
             <input list="brand-filter-datalist-vehiclemodel" v-model.lazy="brandNameFilter" placeholder="Filtrar marca..." class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs min-w-[150px] text-gray-900 dark:text-gray-100" />
            <datalist id="brand-filter-datalist-vehiclemodel"> {/* ID único para el datalist */}
              <option v-for="brandNameItem in uniqueBrandNamesForTableFilter" :key="brandNameItem" :value="brandNameItem"></option>
            </datalist>
          </td>
          <td class="px-1 py-1"></td>
          <td v-if="authStore.isSuperuser" class="px-1 py-1"></td>
          <td v-if="authStore.isSuperuser" class="px-1 py-1"></td>
          <td class="px-1 py-1 text-center"></td>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading && itemsPaginated.length === 0">
          <td :colspan="authStore.isSuperuser ? 7 : 5" class="text-center py-4">Cargando modelos...</td>
        </tr>
        <tr v-else-if="itemsPaginated.length === 0">
          <td :colspan="authStore.isSuperuser ? 7 : 5" class="text-center py-4">No se encontraron modelos que coincidan.</td>
        </tr>
        <tr v-for="model in itemsPaginated" :key="model.id" class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
          <td data-label="ID" class="px-4 py-2 font-medium text-gray-900 whitespace-nowrap dark:text-white">{{ model.id }}</td>
          <td data-label="Nombre Modelo" class="px-4 py-2">
            <span class="px-4 py-2 font-medium text-gray-900 whitespace-nowrap dark:text-white cursor-pointer hover:underline" @click="openDetailModal(model)">
                {{ model.name }}
            </span>
          </td>
          <td data-label="Marca" class="px-4 py-2">
            <strong class="font-semibold">
                {{ model.brand }}
            </strong>
          </td>
          <td data-label="Activo" class="px-4 py-2 text-center">
            <span :class="model.active ? 'bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full dark:bg-green-900 dark:text-green-300' : 'bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-full dark:bg-red-900 dark:text-red-300'">
              {{ model.active ? 'Activo' : 'Inactivo' }}
            </span>
          </td>
          <td v-if="authStore.isSuperuser" data-label="Creado por" class="px-4 py-2">{{ model.created_by_name || 'N/A' }}</td>
          <td v-if="authStore.isSuperuser" data-label="F. Creación" class="px-4 py-2">{{ model.created_at }}</td>
          <td class="px-4 py-2 whitespace-nowrap text-center" data-label="Acciones">
            <BaseButtons type="justify-center" no-wrap>
              <BaseButton 
                v-if="authStore.hasPermission('vehiclemodel.change_vehiclemodel')"
                color="info" 
                :icon="mdiPencil" 
                small 
                title="Editar" 
                @click="openEdit(model)" 
              />
              <BaseButton 
                v-if="model.active && authStore.hasPermission('vehiclemodel.delete_vehiclemodel')" 
                color="danger" 
                :icon="mdiTrashCan" 
                small 
                title="Desactivar" 
                @click="openDelete(model)" 
              />
              <BaseButton 
                color="light"  outline
                :icon="mdiEye" 
                small 
                title="Ver Detalles" 
                @click="openDetailModal(model)" 
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
      <small>Página {{ currentPageHuman }} de {{ numPages }} (Total: {{ filteredVehicleModels.length }} modelos)</small>
    </div>
  </div>
</template>

<style scoped>
/* Estilos para los inputs de filtro en la cabecera */
thead .px-1 { padding-left: 0.25rem; padding-right: 0.25rem; }
thead .py-1 { padding-top: 0.25rem; padding-bottom: 0.25rem; }
thead input[type="text"], thead input[list], thead select {
  padding: 0.3rem 0.5rem; font-size: 0.75rem; border-radius: 0.375rem;
  border: 1px solid #D1D5DB; 
  background-color: #FFF; 
  color: #111827; 
}
.dark thead input[type="text"], .dark thead input[list], .dark thead select {
  background-color: #374151; 
  border-color: #4B5563; 
  color: #F3F4F6; 
}
.dark thead input[type="text"]::placeholder, .dark thead input[list]::placeholder {
  color: #9CA3AF;
}
/* Estilos responsivos para la tabla */
@media (max-width: 768px) {
  table thead { display: none; }
  table tr { margin-bottom: 1rem; display: block; border: 1px solid #ddd; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 0.5rem; }
  table td { display: flex; justify-content: space-between; text-align: right; padding: 0.75rem 0.5rem; border-bottom: 1px dotted #eee; }
  table td:last-child { border-bottom: 0; }
  table td::before { content: attr(data-label); float: left; font-weight: bold; text-transform: uppercase; padding-right: 0.5rem; text-align: left;}
}
</style>