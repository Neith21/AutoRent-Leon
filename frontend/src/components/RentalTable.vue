<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  mdiTrashCan, mdiPencil, mdiPlus, mdiMagnify, mdiFilePdfBox, mdiFileExcel,
  mdiFileDelimited, mdiEye, mdiFilterVariant, mdiSortAscending, mdiSortDescending, mdiCloseCircleOutline,
  mdiCashMultiple, mdiInformationOutline, mdiCheck,
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
import { useMainStore } from '@/stores/main'
import { useAuthStore } from '@/stores/authStore'
import NotificationBar from '@/components/NotificationBar.vue'

const mainStore = useMainStore()
const authStore = useAuthStore()
const router = useRouter()

// --- Estados reactivos ---
const rentals = ref([])
const loading = ref(false)

// --- Filtros y Orden ---
const searchTerm = ref('')
const customerFilter = ref('')
const vehicleFilter = ref('')
const statusFilter = ref('')
const pickupBranchFilter = ref('')
const returnBranchFilter = ref('')
const sortDescending = ref(true) // Ordenar por ID descendente por defecto

const perPage = ref(10)
const currentPage = ref(0)

const restrictedSearchFields = [
  'created_by', 'created_by_name', 'created_at',
  'modified_by', 'modified_by_name', 'updated_at'
]

const rentalStatusChoices = [
  'Reservado', 'Activo', 'Finalizado', 'Retrasado', 'Cancelado'
]

// --- Nuevas opciones para el nivel de combustible (de acuerdo a la base de datos) ---
const fuelLevelChoices = [
  'Vacio',
  '1/4',
  '1/2',
  '3/4',
  'Lleno',
];

// --- Computed properties para filtros y paginación ---
const uniquePickupBranches = computed(() => {
  if (!rentals.value) return []
  return [...new Set(rentals.value.map(r => r.pickup_branch_name).filter(Boolean))].sort()
})

const uniqueReturnBranches = computed(() => {
  if (!rentals.value) return []
  return [...new Set(rentals.value.map(r => r.return_branch_name).filter(Boolean))].sort()
})

const filteredRentals = computed(() => {
  let filtered = [...rentals.value]

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase()
    filtered = filtered.filter(rental => {
      if (authStore.isSuperuser) {
        return Object.values(rental).some(val => val && val.toString().toLowerCase().includes(term))
      } else {
        return Object.entries(rental).some(([key, val]) => {
          if (restrictedSearchFields.includes(key)) return false
          return val && val.toString().toLowerCase().includes(term)
        })
      }
    })
  }

  if (customerFilter.value) {
    const term = customerFilter.value.toLowerCase()
    filtered = filtered.filter(r => r.customer_name && r.customer_name.toLowerCase().includes(term))
  }
  if (vehicleFilter.value) {
    const term = vehicleFilter.value.toLowerCase()
    filtered = filtered.filter(r => r.vehicle_plate && r.vehicle_plate.toLowerCase().includes(term))
  }
  if (statusFilter.value) {
    const term = statusFilter.value.toLowerCase()
    filtered = filtered.filter(r => r.status && r.status.toLowerCase().includes(term))
  }
  if (pickupBranchFilter.value) {
    const term = pickupBranchFilter.value.toLowerCase()
    filtered = filtered.filter(r => r.pickup_branch_name && r.pickup_branch_name.toLowerCase().includes(term))
  }
  if (returnBranchFilter.value) {
    const term = returnBranchFilter.value.toLowerCase()
    filtered = filtered.filter(r => r.return_branch_name && r.return_branch_name.toLowerCase().includes(term))
  }

  filtered.sort((a, b) => {
    return sortDescending.value ? (b.id - a.id) : (a.id - b.id)
  })
  return filtered
})

const itemsPaginated = computed(() =>
  filteredRentals.value.slice(perPage.value * currentPage.value, perPage.value * (currentPage.value + 1))
)
const numPages = computed(() => Math.ceil(filteredRentals.value.length / perPage.value))
const currentPageHuman = computed(() => currentPage.value + 1)
const pagesList = computed(() => Array.from({ length: numPages.value }, (_, i) => i))

// --- Watchers ---
watch([searchTerm, customerFilter, vehicleFilter, statusFilter, pickupBranchFilter, returnBranchFilter, sortDescending], () => {
  currentPage.value = 0
})

// --- Control de UI y Modales ---
const toggleSortOrder = () => { sortDescending.value = !sortDescending.value }
const sortIcon = computed(() => sortDescending.value ? mdiSortDescending : mdiSortAscending)
const clearAllFilters = () => {
  searchTerm.value = ''; customerFilter.value = ''; vehicleFilter.value = '';
  statusFilter.value = ''; pickupBranchFilter.value = ''; returnBranchFilter.value = '';
}

const isCancelModalActive = ref(false)
const isDetailModalActive = ref(false)
const currentRental = ref({})
const selectedRentalForView = ref({})

// --- ESTADOS Y LÓGICA PARA EL NUEVO MODAL DE FINALIZACIÓN ---
const isFinalizeModalActive = ref(false)
const rentalToFinalize = ref({}) // Almacena el alquiler completo a finalizar
const finalizeFormData = ref({ // Datos del formulario del modal de finalización
  actual_return_date: '',
  fuel_level_return: '', // Cambiado a string vacío, ya no null
  remarks: '',
})
const modalErrorMessage = ref('') // Mensajes de error dentro del modal de finalización

const API_URL = import.meta.env.VITE_API_URL

// --- Funciones para interactuar con la API ---
const fetchRentals = async () => {
  if (!authStore.authToken) return
  loading.value = true
  try {
    const config = { headers: { 'Authorization': `Bearer ${authStore.authToken}` } }
    const response = await axios.get(`${API_URL}rental/`, config)
    rentals.value = response.data?.data || []
  } catch (e) {
    console.error('Error obteniendo alquileres:', e)
    mainStore.notify({ color: 'danger', message: 'Error obteniendo alquileres: ' + (e.response?.data?.message || e.message) })
  } finally {
    loading.value = false
  }
}

const getAuthConfig = () => ({ headers: { 'Authorization': `Bearer ${authStore.authToken}` } })

// --- Manejo de Modales y Navegación ---
const openCreate = () => router.push({ name: 'rentalCreate' })
const openEdit = (rental) => router.push({ name: 'rentalEdit', params: { id: rental.id } })
const openAddPayment = (rental) => router.push({ name: 'rentalAddPayment', params: { id: rental.id } })

const openCancel = (rental) => { currentRental.value = rental; isCancelModalActive.value = true }
const openDetailModal = (rental) => { selectedRentalForView.value = rental; isDetailModalActive.value = true }

// Nueva función: Prepara el modal de finalización con datos y fecha actual
const prepareFinalize = (rental) => {
  rentalToFinalize.value = { ...rental } // Copia el objeto para evitar mutaciones directas

  // Establece la fecha y hora de devolución actual como la fecha/hora actual del sistema
  // y la formatea para el input type="datetime-local" (YYYY-MM-DDTHH:MM)
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0') // Meses son 0-indexados
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  finalizeFormData.value.actual_return_date = `${year}-${month}-${day}T${hours}:${minutes}`

  // Inicializar a string vacío para forzar selección de una de las opciones válidas
  finalizeFormData.value.fuel_level_return = ''
  finalizeFormData.value.remarks = '' // Reiniciar observaciones
  modalErrorMessage.value = '' // Limpiar mensajes de error previos del modal
  isFinalizeModalActive.value = true
}

const closeFinalizeModal = () => {
  isFinalizeModalActive.value = false
  rentalToFinalize.value = {}
  // También se inicializa a string vacío al cerrar
  finalizeFormData.value = { actual_return_date: '', fuel_level_return: '', remarks: '' }
  modalErrorMessage.value = ''
}

// Lógica para confirmar la cancelación (existente)
const confirmCancel = async () => {
  loading.value = true
  try {
    await axios.delete(`${API_URL}rentals/${currentRental.value.id}/`, getAuthConfig());
    mainStore.notify({ color: 'success', message: 'Alquiler cancelado exitosamente.' })
    await fetchRentals()
  } catch (e) {
    console.error('Error cancelando alquiler:', e)
    mainStore.notify({ color: 'danger', message: 'Error cancelando alquiler: ' + (e.response?.data?.message || e.message) })
  } finally {
    isCancelModalActive.value = false; loading.value = false
  }
}

// Nueva función: Confirmar finalización con los datos del formulario
const confirmFinalizeWithData = async () => {
  modalErrorMessage.value = '' // Limpiar errores del modal antes de enviar

  if (!rentalToFinalize.value.id) {
    modalErrorMessage.value = "No se ha seleccionado ningún alquiler para finalizar."
    return
  }

  // Validaciones básicas del lado del cliente
  // Ahora esperamos un string de fuelLevelChoices, no un número.
  // La validación `required` del select y esta comprobación de string vacío
  // son suficientes para el frontend.
  if (!finalizeFormData.value.actual_return_date || !finalizeFormData.value.fuel_level_return) {
    modalErrorMessage.value = "Por favor, complete la fecha y hora de devolución y el nivel de combustible."
    return
  }

  // **** REVERSIÓN AQUÍ: Restaurando el formato de fecha que ya tenías y funcionaba ****
  // Si el input datetime-local no está enviando el formato correcto y ya tenías una solución
  // que funcionaba, volvemos a usar esa lógica para formatear la fecha a un string ISO 8601 completo.
  const actualReturnDate = new Date(finalizeFormData.value.actual_return_date);
  const actualReturnDateToSend = actualReturnDate.toISOString(); // Convierte a formato ISO 8601 completo
  // ***********************************************************************************


  const payload = {
    actual_return_date: actualReturnDateToSend, // Usa el valor formateado
    fuel_level_return: finalizeFormData.value.fuel_level_return, // Envía el string seleccionado directamente
    remarks: finalizeFormData.value.remarks,
  }

  loading.value = true
  try {
    const response = await axios.post(
      `${API_URL}rental/${rentalToFinalize.value.id}/finalize/`,
      payload,
      getAuthConfig()
    )

    mainStore.notify({ color: 'success', message: 'Alquiler finalizado exitosamente.' })
    closeFinalizeModal() // Cierra el modal y limpia el formulario
    await fetchRentals() // Refresca la lista para mostrar el estado actualizado
  } catch (e) {
    console.error('Error finalizando alquiler:', e)
    if (e.response && e.response.data) {
      let errorMessages = []
      for (const key in e.response.data) {
        if (Object.hasOwnProperty.call(e.response.data, key)) {
          if (Array.isArray(e.response.data[key])) {
            errorMessages.push(`${key}: ${e.response.data[key].join(', ')}`)
          } else {
            errorMessages.push(`${key}: ${e.response.data[key]}`)
          }
        }
      }
      modalErrorMessage.value = "Errores de validación: " + errorMessages.join('; ')
    } else {
      modalErrorMessage.value = "Error de red o desconocido: " + e.message
    }
    mainStore.notify({ color: 'danger', message: 'Error finalizando alquiler: ' + (e.response?.data?.message || e.message) })
  } finally {
    loading.value = false
  }
}

// --- Funciones de Exportación (Mantienen la misma lógica) ---
const getTableHeaders = () => {
  const headers = [
    "ID", "Cliente", "Vehículo (Placa)", "Sucursal Recogida", "Sucursal Devolución",
    "Fecha Inicio", "Fecha Fin", "Fecha Devolución Real", "Estado", "Precio Total",
    "Combustible Recogida", "Combustible Devolución", "Observaciones"
  ]
  if (authStore.isSuperuser) {
    headers.push("Creado por", "Fecha Creación", "Modificado por", "Fecha Modificación")
  }
  return headers
}

const getRentalDataForExport = (rental) => {
  const data = [
    rental.id || '',
    rental.customer_name || '',
    rental.vehicle_plate || '',
    rental.pickup_branch_name || '',
    rental.return_branch_name || '',
    rental.start_date || '',
    rental.end_date || '',
    rental.actual_return_date || '',
    rental.status || '',
    rental.total_price ? `$${parseFloat(rental.total_price).toFixed(2)}` : '',
    rental.fuel_level_pickup || '',
    rental.fuel_level_return || '',
    rental.remarks || ''
  ]
  if (authStore.isSuperuser) {
    data.push(
      rental.created_by_name || '', rental.created_at || '',
      rental.modified_by_name || '', rental.updated_at || ''
    )
  }
  return data
}

const exportToPDF = () => {
  try {
    const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
    doc.setFontSize(18); doc.text('Reporte de Alquileres', 14, 22)
    doc.setFontSize(11); doc.text(`Fecha: ${new Date().toLocaleDateString()}`, 14, 30)
    const tableColumn = getTableHeaders(); const tableRows = filteredRentals.value.map(getRentalDataForExport)
    autoTable(doc, {
      head: [tableColumn], body: tableRows, startY: 35, theme: 'grid',
      styles: { fontSize: tableColumn.length > 12 ? 6 : 7, cellPadding: 1 },
      headStyles: { fillColor: [41, 128, 185], textColor: [255, 255, 255], fontStyle: 'bold' },
      alternateRowStyles: { fillColor: [245, 245, 245] }, margin: { left: 5, right: 5 }
    })
    doc.save('alquileres.pdf')
    mainStore.notify({ color: 'success', message: 'Exportado a PDF con éxito.' })
  } catch (error) { console.error('Error al generar PDF:', error); mainStore.notify({ color: 'danger', message: 'Error al generar PDF: ' + error.message }) }
}

const exportToCSV = () => {
  try {
    const headers = getTableHeaders(); let csvContent = "\uFEFF" + headers.join(',') + '\n'
    filteredRentals.value.forEach(rental => {
      const row = getRentalDataForExport(rental)
      const formattedRow = row.map(cell => { if (cell === null || cell === undefined) return ''; cell = cell.toString(); if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) { return `"${cell.replace(/"/g, '""')}"`; } return cell; })
      csvContent += formattedRow.join(',') + '\n'
    })
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' }); saveAs(blob, 'alquileres.csv')
    mainStore.notify({ color: 'success', message: 'Exportado a CSV con éxito.' })
  } catch (error) { console.error('Error al generar CSV:', error); mainStore.notify({ color: 'danger', message: 'Error al generar CSV: ' + error.message }) }
}

const exportToExcel = () => {
  try {
    const headers = getTableHeaders(); const data = filteredRentals.value.map(getRentalDataForExport); data.unshift(headers)
    const ws = XLSX.utils.aoa_to_sheet(data)
    const columnWidths = headers.map((headerText) => {
      let width = 15
      if (headerText === "ID") width = 5
      if (headerText === "Cliente") width = 20
      if (headerText === "Vehículo (Placa)") width = 18
      if (headerText.includes("Fecha") || headerText.includes("Precio")) width = 20
      if (headerText === "Observaciones") width = 30
      return { wch: width }
    })
    ws['!cols'] = columnWidths
    const wb = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb, ws, "Alquileres"); XLSX.writeFile(wb, 'alquileres.xlsx')
    mainStore.notify({ color: 'success', message: 'Exportado a Excel con éxito.' })
  } catch (error) { console.error('Error al generar Excel:', error); mainStore.notify({ color: 'danger', message: 'Error al generar Excel: ' + error.message }) }
}

// --- Ciclo de vida ---
onMounted(async () => {
  if (authStore.checkLoggedIn()) {
    await authStore.fetchUserPermissions()
  }
  await fetchRentals()
})
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

  <CardBoxModal v-model="isCancelModalActive" title="Confirmar Cancelación de Alquiler">
    <p>¿Está seguro que desea **cancelar** el alquiler <strong>#{{ currentRental.id }}</strong> (Vehículo: {{ currentRental.vehicle_plate }})?</p>
    <p>Esta acción marcará el alquiler como "Cancelado" y liberará el vehículo si no ha sido devuelto.</p>
    <div class="mt-6 flex justify-end space-x-2">
      <BaseButton color="whiteDark" label="No" @click="isCancelModalActive = false" :disabled="loading"/>
      <BaseButton
        color="danger"
        :label="loading ? 'Cancelando...' : 'Sí, Cancelar'"
        :disabled="loading"
        @click="confirmCancel"
      />
    </div>
  </CardBoxModal>

  <CardBoxModal v-model="isDetailModalActive">
    <template #title>
      <div class="flex items-center gap-2">
        <mdi :path="mdiInformationOutline" size="24" /> Detalles Alquiler: {{ selectedRentalForView.id }}
      </div>
    </template>
    <div v-if="selectedRentalForView.id" class="space-y-2 text-sm p-4">
      <p><strong>ID:</strong> {{ selectedRentalForView.id }}</p>
      <p><strong>Cliente:</strong> {{ selectedRentalForView.customer_name }} <span v-if="selectedRentalForView.customer">(ID: {{ selectedRentalForView.customer }})</span></p>
      <p><strong>Vehículo:</strong> {{ selectedRentalForView.vehicle_plate }} <span v-if="selectedRentalForView.vehicle">(ID: {{ selectedRentalForView.vehicle }})</span></p>
      <p><strong>Sucursal de Recogida:</strong> {{ selectedRentalForView.pickup_branch_name }} <span v-if="selectedRentalForView.pickup_branch">(ID: {{ selectedRentalForView.pickup_branch }})</span></p>
      <p><strong>Sucursal de Devolución:</strong> {{ selectedRentalForView.return_branch_name }} <span v-if="selectedRentalForView.return_branch">(ID: {{ selectedRentalForView.return_branch }})</span></p>
      <p><strong>Fecha y Hora de Inicio:</strong> {{ selectedRentalForView.start_date }}</p>
      <p><strong>Fecha y Hora de Fin Estimada:</strong> {{ selectedRentalForView.end_date }}</p>
      <p><strong>Fecha y Hora de Devolución Real:</strong> {{ selectedRentalForView.actual_return_date || 'N/A' }}</p>
      <p><strong>Estado:</strong>
        <span :class="{
          'text-green-600': selectedRentalForView.status === 'Activo' || selectedRentalForView.status === 'Finalizado',
          'text-blue-600': selectedRentalForView.status === 'Reservado',
          'text-yellow-600': selectedRentalForView.status === 'Retrasado',
          'text-red-600': selectedRentalForView.status === 'Cancelado'
        }">
          {{ selectedRentalForView.status }}
        </span>
      </p>
      <p><strong>Precio Total Calculado:</strong> ${{ selectedRentalForView.total_price }}</p>
      <p><strong>Nivel de Combustible (Recogida):</strong> {{ selectedRentalForView.fuel_level_pickup }}</p>
      <p><strong>Nivel de Combustible (Devolución):</strong> {{ selectedRentalForView.fuel_level_return || 'N/A' }}</p>
      <p><strong>Observaciones:</strong> <span class="whitespace-pre-wrap">{{ selectedRentalForView.remarks || 'Ninguna' }}</span></p>
      <p><strong>Activo:</strong> <span :class="selectedRentalForView.active ? 'text-green-600' : 'text-red-600'">{{ selectedRentalForView.active ? 'Sí' : 'No' }}</span></p>

      <div v-if="authStore.isSuperuser" class="pt-2 mt-2 border-t border-gray-200 dark:border-gray-700">
        <h3 class="text-md font-semibold mb-1 mt-2 text-gray-800 dark:text-gray-200">Información de Auditoría:</h3>
        <p><strong>Creado por:</strong> {{ selectedRentalForView.created_by_name || 'N/A' }} <span v-if="selectedRentalForView.created_by">(ID: {{ selectedRentalForView.created_by }})</span></p>
        <p><strong>Fecha de Creación:</strong> {{ selectedRentalForView.created_at }}</p>
        <p><strong>Modificado por:</strong> {{ selectedRentalForView.modified_by_name || 'N/A' }} <span v-if="selectedRentalForView.modified_by">(ID: {{ selectedRentalForView.modified_by }})</span></p>
        <p><strong>Fecha de Modificación:</strong> {{ selectedRentalForView.updated_at }}</p>
      </div>
    </div>
    <template #footer>
      <BaseButtons>
        <BaseButton label="Cerrar" color="info" @click="isDetailModalActive = false" />
      </BaseButtons>
    </template>
  </CardBoxModal>

  <CardBoxModal v-model="isFinalizeModalActive" title="Finalizar Alquiler">
    <div v-if="rentalToFinalize.id" class="space-y-4 p-4">
      <p class="text-md text-gray-700 dark:text-gray-300">Por favor, ingrese los detalles para finalizar el alquiler <strong>#{{ rentalToFinalize.id }}</strong>:</p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label for="actualReturnDate" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha y Hora de Devolución Actual:</label>
          <FormControl
            v-model="finalizeFormData.actual_return_date"
            type="datetime-local"
            id="actualReturnDate"
            required
            :min="rentalToFinalize.start_date ? rentalToFinalize.start_date.substring(0, 16) : null"
            :max="new Date().toISOString().substring(0, 16)"
          />
          <small class="text-xs text-gray-500 dark:text-gray-400">Debe ser posterior a la fecha de inicio y no futura.</small>
        </div>
        <div>
          <label for="fuelLevelReturn" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nivel de Combustible al Devolver:</label>
          <select
            v-model="finalizeFormData.fuel_level_return"
            id="fuelLevelReturn"
            required
            class="w-full p-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm text-gray-900 dark:text-gray-100"
          >
            <option value="" disabled>Seleccione un nivel</option> <option v-for="level in fuelLevelChoices" :key="level" :value="level">{{ level }}</option>
          </select>
          </div>
      </div>

      <div>
        <label for="remarks" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Observaciones:</label>
        <FormControl
          v-model="finalizeFormData.remarks"
          type="textarea"
          id="remarks"
          placeholder="Añadir observaciones sobre la devolución..."
          rows="3"
        />
      </div>
      <div v-if="modalErrorMessage" class="text-red-500 text-sm mt-2">{{ modalErrorMessage }}</div>
    </div>

    <div class="mt-6 flex justify-end space-x-2 p-4 pt-0">
      <BaseButton color="whiteDark" label="Cancelar" @click="closeFinalizeModal" :disabled="loading"/>
      <BaseButton
        color="success"
        :label="loading ? 'Finalizando...' : 'Confirmar Finalización'"
        :disabled="loading"
        @click="confirmFinalizeWithData"
      />
    </div>
  </CardBoxModal>


  <div class="mb-6 flex flex-col md:flex-row items-center justify-between gap-4 px-4 md:px-0">
    <BaseButton
      v-if="authStore.hasPermission('rental.add_rental')"
      color="info"
      :icon="mdiPlus"
      label="Crear Alquiler"
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
          <th scope="col" class="px-4 py-3">Cliente</th>
          <th scope="col" class="px-4 py-3">Vehículo (Placa)</th>
          <th scope="col" class="px-4 py-3">F. Inicio</th>
          <th scope="col" class="px-4 py-3">F. Fin Estimada</th>
          <th scope="col" class="px-4 py-3">Estado</th>
          <th scope="col" class="px-4 py-3">Precio Total</th>
          <th scope="col" class="px-4 py-3">Sucursal Recogida</th>
          <th scope="col" class="px-4 py-3">Sucursal Devolución</th>
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
            <FormControl type="text" v-model.lazy="customerFilter" placeholder="Filtrar..." class="text-xs min-w-[120px]" />
          </td>
          <td class="px-1 py-1">
            <FormControl type="text" v-model.lazy="vehicleFilter" placeholder="Filtrar..." class="text-xs min-w-[120px]" />
          </td>
          <td class="px-1 py-1">
            </td>
          <td class="px-1 py-1">
            </td>
          <td class="px-1 py-1">
            <select v-model.lazy="statusFilter"
                    class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs min-w-[100px] text-gray-900 dark:text-gray-100">
              <option value="">Todos</option>
              <option v-for="status in rentalStatusChoices" :key="status" :value="status">{{ status }}</option>
            </select>
          </td>
          <td class="px-1 py-1">
            </td>
          <td class="px-1 py-1">
            <input list="pickup-branch-datalist-rental" v-model.lazy="pickupBranchFilter" placeholder="Filtrar..." class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs min-w-[100px] text-gray-900 dark:text-gray-100" />
            <datalist id="pickup-branch-datalist-rental">
              <option v-for="branchName in uniquePickupBranches" :key="branchName" :value="branchName"></option>
            </datalist>
          </td>
          <td class="px-1 py-1">
            <input list="return-branch-datalist-rental" v-model.lazy="returnBranchFilter" placeholder="Filtrar..." class="w-full p-1 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs min-w-[100px] text-gray-900 dark:text-gray-100" />
            <datalist id="return-branch-datalist-rental">
              <option v-for="branchName in uniqueReturnBranches" :key="branchName" :value="branchName"></option>
            </datalist>
          </td>
          <td class="px-1 py-1 text-center"></td>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading && itemsPaginated.length === 0">
          <td colspan="10" class="text-center py-4">Cargando alquileres...</td>
        </tr>
        <tr v-else-if="itemsPaginated.length === 0">
          <td colspan="10" class="text-center py-4">No se encontraron alquileres que coincidan.</td>
        </tr>
        <tr v-for="rental in itemsPaginated" :key="rental.id"
          class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
          <td data-label="ID" class="px-4 py-2 font-medium text-gray-900 whitespace-nowrap dark:text-white">{{ rental.id }}</td>
          <td data-label="Cliente" class="px-4 py-2">{{ rental.customer_name }}</td>
          <td data-label="Vehículo" class="px-4 py-2">{{ rental.vehicle_plate }}</td>
          <td data-label="F. Inicio" class="px-4 py-2">{{ rental.start_date }}</td>
          <td data-label="F. Fin Estimada" class="px-4 py-2">{{ rental.end_date }}</td>
          <td data-label="Estado" class="px-4 py-2">
            <span :class="{
              'text-green-600': rental.status === 'Activo' || rental.status === 'Finalizado',
              'text-blue-600': rental.status === 'Reservado',
              'text-yellow-600': rental.status === 'Retrasado',
              'text-red-600': rental.status === 'Cancelado'
            }">
              {{ rental.status }}
            </span>
          </td>
          <td data-label="Precio Total" class="px-4 py-2">${{ parseFloat(rental.total_price).toFixed(2) }}</td>
          <td data-label="Sucursal Recogida" class="px-4 py-2">{{ rental.pickup_branch_name }}</td>
          <td data-label="Sucursal Devolución" class="px-4 py-2">{{ rental.return_branch_name }}</td>
          <td class="px-4 py-2 whitespace-nowrap text-center" data-label="Acciones">
            <BaseButtons type="justify-start lg:justify-end" no-wrap>
              <BaseButton
                v-if="authStore.hasPermission('rental.change_rental')"
                color="info"
                :icon="mdiPencil"
                small
                @click="openEdit(rental)"
                title="Editar Alquiler"
              />
              <BaseButton
                v-if="rental.active && rental.status !== 'Finalizado' && rental.status !== 'Cancelado' && authStore.hasPermission('rental.change_rental')"
                :icon="mdiCheck"
                color="success"
                small
                @click="prepareFinalize(rental)"
                title="Finalizar Alquiler"
              />
              <BaseButton
                v-if="rental.active && rental.status !== 'Finalizado' && rental.status !== 'Cancelado' && authStore.hasPermission('rental.add_payment')"
                :icon="mdiCashMultiple"
                color="warning"
                small
                @click="openAddPayment(rental)"
                title="Registrar Pago"
              />
              <BaseButton
                v-if="rental.active && rental.status !== 'Finalizado' && rental.status !== 'Cancelado' && authStore.hasPermission('rental.delete_rental')"
                :icon="mdiTrashCan"
                color="danger"
                small
                @click="openCancel(rental)"
                title="Cancelar Alquiler"
              />
              <BaseButton
                :icon="mdiEye"
                color="contrast"
                small
                @click="openDetailModal(rental)"
                title="Ver Detalles"
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
      <small>Página {{ currentPageHuman }} de {{ numPages }} (Total: {{ filteredRentals.length }} alquileres)</small>
    </div>
  </div>
</template>

<style scoped>
/* Estilos para los inputs de filtro en la cabecera (igual que tu ejemplo) */
thead .px-1 { padding-left: 0.25rem; padding-right: 0.25rem; }
thead .py-1 { padding-top: 0.25rem; padding-bottom: 0.25rem; }
thead input[type="text"], thead select, thead input[list] {
  padding: 0.3rem 0.5rem; font-size: 0.75rem; border-radius: 0.375rem;
  border: 1px solid #D1D5DB;
  background-color: #FFF;
  color: #111827;
}
.dark thead input[type="text"], .dark thead select, .dark th { 
  background-color: #374151; color: #E5E7EB; border-color: #4B5563;
}
</style>