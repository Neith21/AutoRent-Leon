<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { mdiArrowLeftCircle, mdiPlus } from '@mdi/js';
import axios from 'axios';
import FormField from '@/components/FormField.vue';
import FormControl from '@/components/FormControl.vue';
import BaseButton from '@/components/BaseButton.vue';
import BaseButtons from '@/components/BaseButtons.vue';
import CardBox from '@/components/CardBox.vue';
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue';
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue';
import { useMainStore } from '@/stores/main';
import NotificationBar from '@/components/NotificationBar.vue';

const router = useRouter();
const mainStore = useMainStore();
const token = localStorage.getItem('autorent_leon_token');

const loading = ref(false);
const loadingCustomers = ref(false);
const loadingVehicles = ref(false);
const loadingBranches = ref(false);
const loadingPriceCalc = ref(false);

const customers = ref([]);
const vehicles = ref([]);
const branches = ref([]);

const form = ref({
  customer: null,
  vehicle: null,
  pickup_branch: null,
  return_branch: null,
  start_date: '', // datetime-local lo llenará como YYYY-MM-DDTHH:mm
  end_date: '',   // datetime-local lo llenará como YYYY-MM-DDTHH:mm
  fuel_level_pickup: null,
  remarks: '',
});

const estimatedPrice = ref('0.00');
const requiredInitialPayment = ref('0.00');
const paymentPercentage = ref(0);
const depositRequired = ref('0.00');
const customerActiveRentals = ref(0);
const durationDays = ref(0);
const vehicleDailyRate = ref('0.00');
const showPriceDetails = ref(false);

const pageTitle = computed(() => 'Crear Nuevo Alquiler');
const API_URL = import.meta.env.VITE_API_URL;

const fuelLevelOptions = [
  { id: 'Vacio', label: 'Vacío' },
  { id: '1/4', label: '1/4' },
  { id: '1/2', label: '1/2' },
  { id: '3/4', label: '3/4' },
  { id: 'Lleno', label: 'Lleno' },
];

const getAuthConfig = () => ({
  headers: {
    Authorization: `Bearer ${token}`,
  },
});

const getAuthConfigJson = () => ({
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

// --- Función utilitaria para formatear fecha y hora a DD-MM-YYYY HH:MM ---
const getFormattedDateTime = (isoDateTimeString) => {
  if (!isoDateTimeString) {
    return '';
  }
  
  const dateObj = new Date(isoDateTimeString);

  if (isNaN(dateObj.getTime())) {
    console.warn('Advertencia: Intento de formatear una fecha/hora inválida:', isoDateTimeString);
    return ''; 
  }

  const day = String(dateObj.getDate()).padStart(2, '0');
  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  const year = dateObj.getFullYear();
  const hours = String(dateObj.getHours()).padStart(2, '0');
  const minutes = String(dateObj.getMinutes()).padStart(2, '0');

  return `${day}-${month}-${year} ${hours}:${minutes}`;
};


// --- Funciones para cargar datos de dropdowns ---

const fetchCustomers = async () => {
  if (!token) return;
  loadingCustomers.value = true;
  try {
    const config = getAuthConfig();
    const response = await axios.get(`${API_URL}customer`, config);
    customers.value = response.data?.data?.map(cust => ({
      id: cust.id,
      label: `${cust.first_name} ${cust.last_name} - ${cust.customer_type}`
    })) || [];
  } catch (e) {
    console.error("Error fetching customers:", e);
    mainStore.notify({ color: 'danger', message: 'Error cargando clientes: ' + (e.response?.data?.message || e.message) });
  } finally {
    loadingCustomers.value = false;
  }
};

const fetchVehicles = async () => {
  if (!token) return;
  loadingVehicles.value = true;
  try {
    const config = getAuthConfig();
    const response = await axios.get(`${API_URL}vehicle`, config);
    vehicles.value = response.data?.data?.map(veh => ({
      id: veh.id,
      label: `${veh.brand} ${veh.vehiclemodel} (${veh.plate}) - ${veh.daily_price}$/día`
    })) || [];
  } catch (e) {
    console.error("Error fetching vehicles:", e);
    mainStore.notify({ color: 'danger', message: 'Error cargando vehículos: ' + (e.response?.data?.message || e.message) });
  } finally {
    loadingVehicles.value = false;
  }
};

const fetchBranches = async () => {
  if (!token) return;
  loadingBranches.value = true;
  try {
    const config = getAuthConfig();
    const response = await axios.get(`${API_URL}branch`, config);
    branches.value = response.data?.data?.map(br => ({
      id: br.id,
      label: br.name || 'Sucursal Desconocida'
    })) || [];
  } catch (e) {
    console.error("Error fetching branches:", e);
    mainStore.notify({ color: 'danger', message: 'Error cargando sucursales: ' + (e.response?.data?.message || e.message) });
  } finally {
    loadingBranches.value = false;
  }
};

// --- Watchers para cálculos y validaciones dinámicas ---
let priceCalcTimeout = null;

const calculateRentalPrice = async () => {
  if (priceCalcTimeout) {
    clearTimeout(priceCalcTimeout);
  }

  priceCalcTimeout = setTimeout(async () => {
    const { customer, vehicle, start_date, end_date } = form.value;

    if (!customer || !vehicle || !start_date || !end_date) {
      showPriceDetails.value = false;
      estimatedPrice.value = '0.00';
      requiredInitialPayment.value = '0.00';
      depositRequired.value = '0.00';
      customerActiveRentals.value = 0;
      durationDays.value = 0;
      vehicleDailyRate.value = '0.00';
      return;
    }

    loadingPriceCalc.value = true;
    showPriceDetails.value = false;

    try {
      const config = {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      };
      
      // *** APLICAR getFormattedDateTime AQUI ANTES DE ENVIAR LA DATA ***
      const payload = {
        customer: customer,
        vehicle: vehicle,
        start_date: getFormattedDateTime(start_date), // <-- ¡Cambio aquí!
        end_date: getFormattedDateTime(end_date),     // <-- ¡Cambio aquí!
      };
      
      const response = await axios.post(`${API_URL}rental/calculate-price/`, payload, config);
      const data = response.data;

      estimatedPrice.value = data.total_price_estimated;
      requiredInitialPayment.value = data.required_initial_payment;
      paymentPercentage.value = data.payment_percentage;
      depositRequired.value = data.deposit_required;
      customerActiveRentals.value = data.customer_active_rentals;
      durationDays.value = data.duration_days;
      vehicleDailyRate.value = data.vehicle_daily_rate;
      showPriceDetails.value = true;
      mainStore.notify({ color: 'info', message: 'Precio estimado y condiciones de pago actualizadas.' });

    } catch (e) {
      console.error("Error calculating price:", e);
      estimatedPrice.value = '0.00';
      requiredInitialPayment.value = '0.00';
      paymentPercentage.value = 0;
      depositRequired.value = '0.00';
      customerActiveRentals.value = 0;
      durationDays.value = 0;
      vehicleDailyRate.value = '0.00';
      showPriceDetails.value = false;
      let errorMessage = 'Error al calcular precio: ';
      if (e.response && e.response.data) {
        if (typeof e.response.data === 'string') {
          errorMessage += e.response.data;
        } else if (e.response.data.message) {
          errorMessage += e.response.data.message;
        } else if (e.response.data.detail) {
          errorMessage += e.response.data.detail;
        } else if (e.response.data.errors && Array.isArray(e.response.data.errors)) {
          errorMessage += e.response.data.errors.join('\n');
        } else {
          for (const field in e.response.data) {
            if (Array.isArray(e.response.data[field])) {
              e.response.data[field].forEach(msg => errorMessage += `${field}: ${msg}\n`);
            } else {
              errorMessage += `${field}: ${e.response.data[field]}\n`;
            }
          }
        }
      } else {
        errorMessage += e.message;
      }
      mainStore.notify({ color: 'danger', message: errorMessage.trim() });
    } finally {
      loadingPriceCalc.value = false;
    }
  }, 500);
};

watch([() => form.value.customer, () => form.value.vehicle, () => form.value.start_date, () => form.value.end_date], calculateRentalPrice);


onMounted(async () => {
  await Promise.all([
    fetchCustomers(),
    fetchVehicles(),
    fetchBranches(),
  ]);

  // Restablecer el formulario y los detalles del precio al montar
  form.value = {
    customer: null,
    vehicle: null,
    pickup_branch: null,
    return_branch: null,
    start_date: '',
    end_date: '',
    fuel_level_pickup: null,
    remarks: '',
  };
  estimatedPrice.value = '0.00';
  requiredInitialPayment.value = '0.00';
  paymentPercentage.value = 0;
  depositRequired.value = '0.00';
  customerActiveRentals.value = 0;
  durationDays.value = 0;
  vehicleDailyRate.value = '0.00';
  showPriceDetails.value = false;
});

const handleSubmit = async () => {
  loading.value = true;

  const requiredFields = {
    customer: 'Cliente',
    vehicle: 'Vehículo',
    pickup_branch: 'Sucursal de Recogida',
    return_branch: 'Sucursal de Devolución',
    start_date: 'Fecha de Inicio',
    end_date: 'Fecha de Fin',
    fuel_level_pickup: 'Nivel de Combustible al Recoger',
  };

  for (const fieldKey in requiredFields) {
    if (!form.value[fieldKey]) {
      mainStore.notify({ color: 'danger', message: `El campo '${requiredFields[fieldKey]}' es requerido.` });
      loading.value = false;
      return;
    }
  }

  const startDate = new Date(form.value.start_date);
  const endDate = new Date(form.value.end_date);
  const now = new Date();

  // Validar si las fechas son válidas (parseadas correctamente)
  if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
    mainStore.notify({ color: 'danger', message: 'Formato de fecha u hora inválido. Por favor, asegúrese de seleccionar una fecha y hora válidas.' });
    loading.value = false;
    return;
  }

  // Asegurarse de que la fecha de inicio no sea pasada (con 1 minuto de holgura)
  if (startDate.getTime() < (now.getTime() - 60000)) { 
    mainStore.notify({ color: 'danger', message: 'La fecha y hora de inicio no puede ser una fecha pasada.' });
    loading.value = false;
    return;
  }
  if (endDate <= startDate) {
    mainStore.notify({ color: 'danger', message: 'La fecha y hora de fin debe ser posterior a la fecha de inicio.' });
    loading.value = false;
    return;
  }
  if (form.value.pickup_branch === form.value.return_branch) {
    mainStore.notify({ color: 'warning', message: 'La sucursal de recogida y devolución son la misma. Esto es permitido, pero se notifica.' });
  }

  try {
    const payload = { ...form.value };
    // *** APLICAR getFormattedDateTime AQUI ANTES DE ENVIAR LA DATA FINAL ***
    payload.start_date = getFormattedDateTime(form.value.start_date); // Aplicando el formato para el envío final
    payload.end_date = getFormattedDateTime(form.value.end_date);     // Aplicando el formato para el envío final
    
    await axios.post(`${API_URL}rental/`, payload, getAuthConfigJson()); 
    mainStore.notify({ color: 'success', message: 'Alquiler creado exitosamente.' });
    router.push({ name: 'rentals' }); 
  } catch (e) {
    console.error('Error creando alquiler:', e);
    let messagesToShow = [];
    const errorColor = 'danger';

    if (e.response && e.response.data) {
      const backendError = e.response.data;
      if (typeof backendError === 'string') {
        messagesToShow.push(backendError);
      } else if (backendError.message) {
        messagesToShow.push(backendError.message);
      } else if (backendError.detail) {
        messagesToShow.push(backendError.detail);
      } else if (backendError.errors && Array.isArray(backendError.errors)) {
        backendError.errors.forEach(err => messagesToShow.push(err));
      } else {
        for (const field in backendError) {
          if (Array.isArray(backendError[field])) {
            backendError[field].forEach(msg => messagesToShow.push(`${field}: ${msg}`));
          } else {
            messagesToShow.push(`${field}: ${backendError[field]}`);
          }
        }
      }
    } else if (e.message) {
      messagesToShow.push(e.message);
    }

    if (messagesToShow.length === 0) {
      messagesToShow.push('Ha ocurrido un error inesperado. Intente de nuevo.');
    }
    mainStore.notify({
      color: errorColor,
      message: messagesToShow.join('\n'),
    });
  } finally {
    loading.value = false;
  }
};

const cancelForm = () => {
  router.push({ name: 'rentals' });
};
</script>

<template>
  <LayoutAuthenticated>
    <div v-if="mainStore && mainStore.notification" class="sticky top-0 z-40 px-4 md:px-6">
      <NotificationBar
        v-model="mainStore.notification.show"
        :color="mainStore.notification.color"
        :icon="mainStore.notification.icon"
        class="mt-2"
      >
        <pre class="whitespace-pre-wrap">{{ mainStore.notification.message }}</pre>
      </NotificationBar>
    </div>

    <SectionTitleLineWithButton :icon="mdiPlus" :title="pageTitle" main style="margin: 1rem;">
      <BaseButton
        :to="{ name: 'rentals' }"
        :icon="mdiArrowLeftCircle"
        label="Volver a la lista"
        color="contrast"
        rounded-full
        small
      />
    </SectionTitleLineWithButton>
    <CardBox is-form @submit.prevent="handleSubmit" style="margin: 1rem;">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField label="Cliente" required>
          <FormControl
            v-model="form.customer"
            id="customer"
            :options="customers"
            :disabled="loadingCustomers"
            placeholder="Seleccione un cliente"
            type="select"
          />
          <div v-if="loadingCustomers" class="text-xs text-gray-500 mt-1">Cargando clientes...</div>
        </FormField>

        <FormField label="Vehículo" required>
          <FormControl
            v-model="form.vehicle"
            id="vehicle"
            :options="vehicles"
            :disabled="loadingVehicles"
            placeholder="Seleccione un vehículo"
            type="select"
          />
          <div v-if="loadingVehicles" class="text-xs text-gray-500 mt-1">Cargando vehículos...</div>
        </FormField>

        <FormField label="Sucursal de Recogida" required>
          <FormControl
            v-model="form.pickup_branch"
            id="pickup_branch"
            :options="branches"
            :disabled="loadingBranches"
            placeholder="Seleccione sucursal de recogida"
            type="select"
          />
          <div v-if="loadingBranches" class="text-xs text-gray-500 mt-1">Cargando sucursales...</div>
        </FormField>

        <FormField label="Sucursal de Devolución" required>
          <FormControl
            v-model="form.return_branch"
            id="return_branch"
            :options="branches"
            :disabled="loadingBranches"
            placeholder="Seleccione sucursal de devolución"
          />
          <div v-if="loadingBranches" class="text-xs text-gray-500 mt-1">Cargando sucursales...</div>
        </FormField>

        <FormField label="Fecha y Hora de Inicio" required>
          <FormControl
            v-model="form.start_date"
            id="start_date"
            type="datetime-local"
            placeholder="DD-MM-YYYY HH:MM"
          />
        </FormField>

        <FormField label="Fecha y Hora de Fin" required>
          <FormControl
            v-model="form.end_date"
            id="end_date"
            type="datetime-local"
            placeholder="DD-MM-YYYY HH:MM"
          />
        </FormField>

        <FormField label="Nivel de Combustible (Recogida)" required>
          <FormControl
            v-model="form.fuel_level_pickup"
            id="fuel_level_pickup"
            :options="fuelLevelOptions"
            placeholder="Seleccione nivel de combustible"
            type="select"
          />
        </FormField>

        <FormField label="Observaciones" class="md:col-span-2">
          <FormControl
            v-model="form.remarks"
            id="remarks"
            type="textarea"
            placeholder="Notas o comentarios adicionales sobre el alquiler..."
          />
        </FormField>
      </div>

      ---
      <div v-if="showPriceDetails" class="mt-6 p-4 border border-gray-200 rounded-md bg-gray-50">
        <h3 class="text-lg font-semibold mb-2">Detalles del Alquiler y Pagos:</h3>
        <p class="text-sm">
          <span class="font-medium">Duración:</span> {{ durationDays }} día(s)
          <span v-if="durationDays > 0"> (Tarifa Diaria: ${{ parseFloat(vehicleDailyRate).toFixed(2) }})</span>
        </p>
        <p class="text-sm font-bold mt-1">
          <span class="font-medium">Precio Total Estimado:</span> ${{ parseFloat(estimatedPrice).toFixed(2) }}
        </p>
        <p class="text-sm mt-1">
          <span class="font-medium">Pago Inicial Requerido ({{ paymentPercentage }}%):</span> ${{ parseFloat(requiredInitialPayment).toFixed(2) }}
        </p>
        <p v-if="parseFloat(depositRequired) > 0" class="text-sm mt-1">
          <span class="font-medium">Depósito de Garantía Requerido:</span> ${{ parseFloat(depositRequired).toFixed(2) }} (para clientes extranjeros)
        </p>
        <p class="text-sm mt-1">
          <span class="font-medium">Alquileres Activos del Cliente:</span> {{ customerActiveRentals }}
        </p>
        <div v-if="loadingPriceCalc" class="text-xs text-gray-500 mt-2">Recalculando precio y validaciones...</div>
      </div>
      <div v-else-if="form.customer && form.vehicle && form.start_date && form.end_date" class="mt-6 p-4 text-center text-gray-500">
        Ingresa las fechas y selecciona Cliente/Vehículo para calcular el precio estimado.
      </div>
      ---

      <template #footer>
        <BaseButtons>
          <BaseButton
            color="info"
            type="submit"
            :disabled="loading || loadingPriceCalc"
            :label="loading ? 'Creando...' : 'Crear Alquiler'"
            :icon="mdiPlus"
          />
          <BaseButton color="whiteDark" label="Cancelar" @click="cancelForm" outline />
        </BaseButtons>
      </template>
    </CardBox>
  </LayoutAuthenticated>
</template>