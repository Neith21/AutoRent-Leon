<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter, onBeforeRouteLeave } from 'vue-router';
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
import ConfirmationModal from '@/components/ConfirmationModal.vue';

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
    start_date: '',
    end_date: '',
    fuel_level_pickup: null,
    remarks: '',
    status: 'Reservado', // Valor por defecto
    // --- Nuevos campos para el pago inicial ---
    initialPaymentAmount: 0.00,
    initialPaymentType: null,
    initialPaymentConcept: null,
    initialPaymentReference: '',
});

// Nombres de variables ajustados para coincidir con la respuesta del backend o ser más claros
const calculatedTotalPrice = ref('0.00'); // Corresponde a 'total_price' del backend
const calculatedRequiredInitialRentalPayment = ref('0.00'); // Corresponde a 'required_initial_rental_payment'
const calculatedDepositRequired = ref('0.00'); // Corresponde a 'deposit_required'
const calculatedTotalDueAtStart = ref('0.00'); // Corresponde a 'total_amount_due_at_start' - ¡Este es el que usamos!

// Estas variables no son retornadas directamente por el backend en calculate-price,
// pero puedes calcularlas en el frontend si es necesario o si las recibes de otro lado.
const estimatedDurationDays = ref(0);
const estimatedVehicleDailyRate = ref('0.00');
const estimatedPaymentPercentage = ref(0);

const showPriceDetails = ref(false);

const rentalCreatedId = ref(null);
const showConfirmationModal = ref(false);

const pageTitle = computed(() => 'Crear Nuevo Alquiler');
const API_URL = import.meta.env.VITE_API_URL;

const fuelLevelOptions = [
    { id: 'Vacio', label: 'Vacío' },
    { id: '1/4', label: '1/4' },
    { id: '1/2', label: '1/2' },
    { id: '3/4', label: '3/4' },
    { id: 'Lleno', label: 'Lleno' },
];

const rentalStatusOptions = [
    { id: 'Reservado', label: 'Reservado' },
    { id: 'Activo', label: 'Activo' },
];

const paymentTypeOptions = [
    { id: 'Efectivo', label: 'Efectivo' },
    { id: 'Tarjeta de Credito', label: 'Tarjeta de Crédito' },
    { id: 'Tarjeta de Debito', label: 'Tarjeta de Débito' },
    { id: 'Transferencia', label: 'Transferencia Bancaria' },
];

// Conceptos de pago ajustados para coincidir con los del backend y el max_length=20
const conceptOptions = [
    { id: 'Anticipo', label: 'Anticipo' }, // Usar 'Anticipo' (con A mayúscula)
    { id: 'Pago Final', label: 'Pago Final' },
    { id: 'Cargo Adicional', label: 'Cargo Adicional' },
    { id: 'Cargo por Retraso', label: 'Cargo por Retraso' },
    { id: 'Reembolso', label: 'Reembolso' },
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

const formatDateTimeForBackend = (isoDateTimeString) => {
    if (!isoDateTimeString) {
        return '';
    }
    const dateObj = new Date(isoDateTimeString);
    if (isNaN(dateObj.getTime())) {
        console.warn('Advertencia: Intento de formatear una fecha/hora inválida para el backend:', isoDateTimeString);
        return '';
    }

    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');
    const hours = String(dateObj.getHours()).padStart(2, '0');
    const minutes = String(dateObj.getMinutes()).padStart(2, '0');
    const seconds = String(dateObj.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};


const fetchCustomers = async () => {
    if (!token) return;
    loadingCustomers.value = true;
    try {
        const config = getAuthConfig();
        const response = await axios.get(`${API_URL}customer`, config);
        customers.value = response.data?.data?.map(cust => ({
            id: cust.id,
            label: `${cust.first_name} ${cust.last_name} - ${cust.customer_type}`,
            customer_type: cust.customer_type, // Asegúrate de que customer_type esté disponible
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
        vehicles.value = response.data?.data
            .filter(veh => veh.status === 'Disponible')
            .map(veh => ({
                id: veh.id,
                label: `${veh.brand} ${veh.vehiclemodel} (${veh.plate}) - ${veh.daily_price}$/día`,
                daily_price: veh.daily_price // Asegúrate de traer el daily_price
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

let priceCalcTimeout = null;

const calculateRentalPrice = async () => {
    if (priceCalcTimeout) {
        clearTimeout(priceCalcTimeout);
    }

    priceCalcTimeout = setTimeout(async () => {
        const { customer, vehicle, start_date, end_date } = form.value;

        // Resetear todos los valores si no hay datos suficientes para el cálculo
        if (!customer || !vehicle || !start_date || !end_date) {
            showPriceDetails.value = false;
            calculatedTotalPrice.value = '0.00';
            calculatedRequiredInitialRentalPayment.value = '0.00';
            calculatedDepositRequired.value = '0.00';
            calculatedTotalDueAtStart.value = '0.00';
            estimatedDurationDays.value = 0;
            estimatedVehicleDailyRate.value = '0.00';
            estimatedPaymentPercentage.value = 0;
            
            form.value.initialPaymentAmount = 0.00;
            form.value.initialPaymentType = null;
            form.value.initialPaymentConcept = null;
            form.value.initialPaymentReference = '';
            return;
        }

        loadingPriceCalc.value = true;
        showPriceDetails.value = false; // Ocultar detalles mientras se calcula

        try {
            const config = {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            };

            const payload = {
                customer: customer,
                vehicle: vehicle,
                start_date: formatDateTimeForBackend(start_date),
                end_date: formatDateTimeForBackend(end_date),
            };

            console.log('Enviando payload a calculate-price (formato corregido):', payload);

            const response = await axios.post(`${API_URL}rental/calculate-price/`, payload, config);
            const data = response.data; // Aquí está la respuesta del backend

            // Asignar los valores del backend
            calculatedTotalPrice.value = data.total_price;
            calculatedRequiredInitialRentalPayment.value = data.required_initial_rental_payment;
            calculatedDepositRequired.value = data.deposit_required;
            calculatedTotalDueAtStart.value = data.total_amount_due_at_start; // Este es el valor clave

            // Calcular y mostrar duración y tarifa diaria en el frontend
            const startDateObj = new Date(start_date);
            const endDateObj = new Date(end_date);
            const durationMs = endDateObj.getTime() - startDateObj.getTime();
            let days = Math.ceil(durationMs / (1000 * 60 * 60 * 24));
            if (days < 0) days = 0;
            estimatedDurationDays.value = days;

            const selectedVehicle = vehicles.value.find(veh => veh.id === form.value.vehicle);
            if (selectedVehicle) {
                estimatedVehicleDailyRate.value = selectedVehicle.daily_price;
            } else {
                estimatedVehicleDailyRate.value = '0.00';
            }

            // Calcular el porcentaje de pago inicial del alquiler
            const total = parseFloat(calculatedTotalPrice.value);
            const initialRentalPayment = parseFloat(calculatedRequiredInitialRentalPayment.value);
            if (total > 0) {
                estimatedPaymentPercentage.value = ((initialRentalPayment / total) * 100).toFixed(0);
            } else {
                estimatedPaymentPercentage.value = 0;
            }

            showPriceDetails.value = true;
            mainStore.notify({ color: 'info', message: 'Precio estimado y condiciones de pago actualizadas.' });

            // *** SUGERIR MONTO Y CONCEPTO PARA EL PAGO INICIAL ***
            // Usa directamente calculatedTotalDueAtStart que ya incluye anticipo + depósito
            const totalPaymentExpected = parseFloat(calculatedTotalDueAtStart.value);
            const depositAmount = parseFloat(calculatedDepositRequired.value);
            const requiredInitialRentalPayment = parseFloat(calculatedRequiredInitialRentalPayment.value);

            // Sugiere el monto total adeudado al inicio.
            // Es crucial que 'initialPaymentAmount' contenga la suma del anticipo del alquiler + el depósito.
            form.value.initialPaymentAmount = totalPaymentExpected; 

            // Establecer el concepto de pago a 'Anticipo' si hay un monto inicial requerido
            // o si el total a pagar al inicio es > 0.
            if (totalPaymentExpected > 0) {
                form.value.initialPaymentConcept = 'Anticipo'; 
            } else {
                form.value.initialPaymentConcept = null; // O dejarlo como null si no hay un pago requerido
            }

            // Lógica para la referencia:
            const selectedCustomer = customers.value.find(cust => cust.id === form.value.customer);
            const customerType = selectedCustomer ? selectedCustomer.customer_type.toLowerCase() : null;

            let referenceText = '';
            if (totalPaymentExpected > 0) {
                if (customerType === 'extranjero' && depositAmount > 0) {
                    if (requiredInitialRentalPayment > 0) {
                        referenceText = `Anticipo de renta y depósito de garantía ($${depositAmount.toFixed(2)})`;
                    } else {
                        // Solo depósito si el anticipo del alquiler es 0, pero hay depósito
                        referenceText = `Depósito de garantía ($${depositAmount.toFixed(2)})`;
                    }
                } else if (requiredInitialRentalPayment > 0) {
                    referenceText = 'Anticipo de renta';
                }
            } else {
                referenceText = 'No se requiere pago inicial';
            }
            form.value.initialPaymentReference = referenceText;

            // Por defecto, sugiere 'Efectivo' solo si hay un monto de pago inicial
            form.value.initialPaymentType = totalPaymentExpected > 0 ? 'Efectivo' : null;

        } catch (e) {
            console.error("Error calculating price:", e);
            // Resetear todos los valores en caso de error
            calculatedTotalPrice.value = '0.00';
            calculatedRequiredInitialRentalPayment.value = '0.00';
            calculatedDepositRequired.value = '0.00';
            calculatedTotalDueAtStart.value = '0.00';
            estimatedDurationDays.value = 0;
            estimatedVehicleDailyRate.value = '0.00';
            estimatedPaymentPercentage.value = 0;
            showPriceDetails.value = false;
            
            form.value.initialPaymentAmount = 0.00;
            form.value.initialPaymentType = null;
            form.value.initialPaymentConcept = null;
            form.value.initialPaymentReference = '';

            let errorMessage = 'Error al calcular precio: ';
            if (e.response && e.response.data) {
                const backendError = e.response.data;
                if (typeof backendError === 'string') {
                    errorMessage += backendError;
                } else if (backendError.message) {
                    errorMessage += backendError.message;
                } else if (backendError.detail) { // 'detail' puede ser string o array de strings
                    if (Array.isArray(backendError.detail)) {
                        errorMessage += backendError.detail.join('\n');
                    } else {
                        errorMessage += backendError.detail;
                    }
                } else if (backendError.errors && Array.isArray(backendError.errors)) {
                    backendError.errors.forEach(err => errorMessage += `${err}\n`);
                } else {
                    for (const field in backendError) {
                        if (Array.isArray(backendError[field])) {
                            backendError[field].forEach(msg => errorMessage += `${field}: ${msg}\n`);
                        } else {
                            errorMessage += `${field}: ${backendError[field]}\n`;
                        }
                    }
                }
            } else if (e.message) {
                errorMessage += e.message;
            }

            mainStore.notify({ color: 'danger', message: errorMessage.trim() });
        } finally {
            loadingPriceCalc.value = false;
        }
    }, 500);
};

watch([
    () => form.value.customer,
    () => form.value.vehicle,
    () => form.value.start_date,
    () => form.value.end_date
], calculateRentalPrice);

const canCreateRental = computed(() => {
    const rentalFieldsFilled = form.value.customer &&
                               form.value.vehicle &&
                               form.value.pickup_branch &&
                               form.value.return_branch &&
                               form.value.start_date &&
                               form.value.end_date &&
                               form.value.fuel_level_pickup &&
                               form.value.status;

    const priceCalculatedAndNotLoading = showPriceDetails.value && !loadingPriceCalc.value;

    const paymentAmount = parseFloat(form.value.initialPaymentAmount);
    const totalDueAtStart = parseFloat(calculatedTotalDueAtStart.value);

    // El pago es válido si el monto es mayor o igual al requerido por el backend
    // y si el tipo de pago y concepto están seleccionados, SOLO si se requiere un pago.
    let paymentFieldsValid = true;
    if (totalDueAtStart > 0) { // Solo requerir campos de pago si hay un monto a pagar
        paymentFieldsValid = paymentAmount >= totalDueAtStart &&
                             form.value.initialPaymentType !== null &&
                             form.value.initialPaymentConcept !== null;
    } else {
        // Si no se requiere pago, los campos de pago pueden ser nulos o 0.
        // Asegúrate de que el monto sea 0 si no se requiere pago.
        paymentFieldsValid = paymentAmount === 0;
    }
    
    return rentalFieldsFilled && priceCalculatedAndNotLoading && paymentFieldsValid && rentalCreatedId.value === null;
});


const validateRentalDetails = async () => {
    const requiredFields = {
        customer: 'Cliente',
        vehicle: 'Vehículo',
        pickup_branch: 'Sucursal de Recogida',
        return_branch: 'Sucursal de Devolución',
        start_date: 'Fecha de Inicio',
        end_date: 'Fecha de Fin',
        fuel_level_pickup: 'Nivel de Combustible al Recoger',
        status: 'Estado del Alquiler',
    };

    for (const fieldKey in requiredFields) {
        if (Object.hasOwnProperty.call(requiredFields, fieldKey)) {
            const value = form.value[fieldKey];
            if (value === null || value === '') {
                mainStore.notify({ color: 'danger', message: `El campo '${requiredFields[fieldKey]}' es requerido.` });
                return;
            }
        }
    }
    
    // Validaciones para los campos de pago
    const paymentAmount = parseFloat(form.value.initialPaymentAmount);
    const totalDueAtStart = parseFloat(calculatedTotalDueAtStart.value || '0.00');

    if (totalDueAtStart > 0) {
        if (isNaN(paymentAmount) || paymentAmount <= 0) {
            mainStore.notify({ color: 'danger', message: 'El monto del pago inicial debe ser mayor a 0.' });
            return;
        }
        if (paymentAmount < totalDueAtStart) {
            mainStore.notify({ color: 'danger', message: `El pago inicial debe ser al menos $${totalDueAtStart.toFixed(2)} (anticipo + depósito).` });
            return;
        }
        if (form.value.initialPaymentType === null) {
            mainStore.notify({ color: 'danger', message: 'El campo \'Método de Pago Inicial\' es requerido.' });
            return;
        }
        if (form.value.initialPaymentConcept === null) {
            mainStore.notify({ color: 'danger', message: 'El campo \'Concepto del Pago Inicial\' es requerido.' });
            return;
        }
    } else if (paymentAmount > 0) {
        // Si el backend dice que no se requiere pago (totalDueAtStart es 0), pero el usuario ingresó un monto
        mainStore.notify({ color: 'warning', message: 'No se requiere un pago inicial para esta renta.' });
        form.value.initialPaymentAmount = 0.00; // Resetearlo
        form.value.initialPaymentType = null;
        form.value.initialPaymentConcept = null;
        form.value.initialPaymentReference = 'No se requiere pago inicial';
        // Podrías permitir que continúe, o detener si quieres que el monto sea 0 obligatoriamente
        // return;
    }


    const startDate = new Date(form.value.start_date);
    const endDate = new Date(form.value.end_date);
    const now = new Date();

    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
        mainStore.notify({ color: 'danger', message: 'Formato de fecha u hora inválido. Por favor, asegúrese de seleccionar una fecha y hora válidas.' });
        return;
    }

    if (startDate.getTime() < (now.getTime() - 60000)) { // Un minuto de margen
        mainStore.notify({ color: 'danger', message: 'La fecha y hora de inicio no puede ser una fecha pasada.' });
        return;
    }
    if (endDate <= startDate) {
        mainStore.notify({ color: 'danger', message: 'La fecha y hora de fin debe ser posterior a la fecha de inicio.' });
        return;
    }
    
    showConfirmationModal.value = true;
};


const createRental = async () => {
    loading.value = true;
    showConfirmationModal.value = false;

    try {
        const payload = { 
            customer: form.value.customer,
            vehicle: form.value.vehicle,
            pickup_branch: form.value.pickup_branch,
            return_branch: form.value.return_branch,
            start_date: formatDateTimeForBackend(form.value.start_date),
            end_date: formatDateTimeForBackend(form.value.end_date),
            fuel_level_pickup: form.value.fuel_level_pickup,
            remarks: form.value.remarks,
            status: form.value.status,
            payments_input: [] // Inicializar array vacío para los pagos
        };

        const paymentAmount = parseFloat(form.value.initialPaymentAmount);
        const totalDueAtStart = parseFloat(calculatedTotalDueAtStart.value);

        // Solo agregar el pago si hay un monto a pagar (ya sea > 0 del frontend o requerido por backend)
        if (paymentAmount > 0 || totalDueAtStart > 0) {
            payload.payments_input.push({
                amount: paymentAmount, // Este monto debe ser el total (anticipo + depósito)
                payment_type: form.value.initialPaymentType,
                concept: form.value.initialPaymentConcept, 
                reference: form.value.initialPaymentReference || null 
            });
        }
        // Si totalDueAtStart es 0 y paymentAmount es 0, el array payments_input estará vacío,
        // lo cual es correcto si no se requiere ningún pago.

        const response = await axios.post(`${API_URL}rental/create-with-initial-payment/`, payload, getAuthConfigJson());

        rentalCreatedId.value = response.data.id || response.data.data?.id; 

        mainStore.notify({ color: 'success', message: `Alquiler #${rentalCreatedId.value} creado y pago inicial registrado exitosamente.` });
        
        router.push({ name: 'rentals' }); 

    } catch (e) {
        console.error('Error creando alquiler o registrando pago inicial:', e);
        let messagesToShow = [];
        const errorColor = 'danger';

        if (e.response && e.response.data) {
            const backendError = e.response.data;
            if (typeof backendError === 'string') {
                messagesToShow.push(backendError);
            } else if (backendError.message) {
                messagesToShow.push(backendError.message);
            } else if (backendError.detail) {
                if (Array.isArray(backendError.detail)) {
                    messagesToShow = messagesToShow.concat(backendError.detail);
                } else {
                    messagesToShow.push(backendError.detail);
                }
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
            messagesToShow.push('Ha ocurrido un error inesperado al crear la renta o registrar el pago inicial. Intente de nuevo.');
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

onBeforeRouteLeave(async (to, from, next) => {
    next();
});


onMounted(async () => {
    await Promise.all([
        fetchCustomers(),
        fetchVehicles(),
        fetchBranches(),
    ]);

    // Asegúrate de que los valores iniciales de form.value sean correctos para los select
    form.value = {
        customer: null,
        vehicle: null,
        pickup_branch: null,
        return_branch: null,
        start_date: '',
        end_date: '',
        fuel_level_pickup: null,
        remarks: '',
        status: 'Reservado', // Estado inicial
        initialPaymentAmount: 0.00,
        initialPaymentType: null,
        initialPaymentConcept: null,
        initialPaymentReference: '',
    };
    // Reinicia también los valores calculados al montar el componente
    calculatedTotalPrice.value = '0.00';
    calculatedRequiredInitialRentalPayment.value = '0.00';
    calculatedDepositRequired.value = '0.00';
    calculatedTotalDueAtStart.value = '0.00';
    estimatedDurationDays.value = 0;
    estimatedVehicleDailyRate.value = '0.00';
    estimatedPaymentPercentage.value = 0;
    showPriceDetails.value = false;
    rentalCreatedId.value = null;
});
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

        <ConfirmationModal
            :show="showConfirmationModal"
            title="Confirmar Creación de Renta y Pago Inicial"
            message="¿Está seguro de que desea crear esta renta y registrar su pago inicial? Esta acción creará la renta en el sistema."
            confirm-label="Sí, Crear Renta y Pagar"
            cancel-label="No, Cancelar"
            confirm-color="info"
            @confirm="createRental"
            @cancel="showConfirmationModal = false"
            @update:show="showConfirmationModal = $event"
        />

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
        <CardBox is-form @submit.prevent="validateRentalDetails" style="margin: 1rem;">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField label="Cliente" required>
                    <FormControl
                        v-model="form.customer"
                        id="customer"
                        :options="customers"
                        :disabled="loadingCustomers || loading"
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
                        :disabled="loadingVehicles || loading"
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
                        :disabled="loadingBranches || loading"
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
                        :disabled="loadingBranches || loading"
                        placeholder="Seleccione sucursal de devolución"
                        type="select"
                    />
                    <div v-if="loadingBranches" class="text-xs text-gray-500 mt-1">Cargando sucursales...</div>
                </FormField>

                <FormField label="Fecha y Hora de Inicio" required>
                    <FormControl
                        v-model="form.start_date"
                        id="start_date"
                        type="datetime-local"
                        placeholder="DD-MM-YYYY HH:MM"
                        :disabled="loading"
                    />
                </FormField>

                <FormField label="Fecha y Hora de Fin" required>
                    <FormControl
                        v-model="form.end_date"
                        id="end_date"
                        type="datetime-local"
                        placeholder="DD-MM-YYYY HH:MM"
                        :disabled="loading"
                    />
                </FormField>

                <FormField label="Nivel de Combustible (Recogida)" required>
                    <FormControl
                        v-model="form.fuel_level_pickup"
                        id="fuel_level_pickup"
                        :options="fuelLevelOptions"
                        placeholder="Seleccione nivel de combustible"
                        type="select"
                        :disabled="loading"
                    />
                </FormField>

                <FormField label="Estado del Alquiler" required>
                    <FormControl
                        v-model="form.status"
                        id="status"
                        :options="rentalStatusOptions"
                        placeholder="Seleccione el estado"
                        type="select"
                        :disabled="loading"
                    />
                </FormField>

                <FormField label="Observaciones" class="md:col-span-2">
                    <FormControl
                        v-model="form.remarks"
                        id="remarks"
                        type="textarea"
                        placeholder="Notas o comentarios adicionales sobre el alquiler..."
                        :disabled="loading"
                    />
                </FormField>
            </div>

            ---
            <div v-if="showPriceDetails" class="mt-6 p-4 border border-gray-200 rounded-md bg-gray-50">
                <h3 class="text-lg font-semibold mb-2">Detalles del Alquiler y Pagos Sugeridos:</h3>
                <p class="text-sm">
                    <span class="font-medium">Duración:</span> {{ estimatedDurationDays }} día(s)
                    <span v-if="estimatedDurationDays > 0"> (Tarifa Diaria: ${{ parseFloat(estimatedVehicleDailyRate).toFixed(2) }})</span>
                </p>
                <p class="text-sm font-bold mt-1">
                    <span class="font-medium">Precio Total Estimado:</span> ${{ parseFloat(calculatedTotalPrice).toFixed(2) }}
                </p>
                <p class="text-sm mt-1">
                    <span class="font-medium">Pago Inicial Sugerido ({{ estimatedPaymentPercentage }}%):</span> ${{ parseFloat(calculatedRequiredInitialPayment).toFixed(2) }}
                </p>
                <p v-if="parseFloat(calculatedDepositRequired) > 0" class="text-sm mt-1">
                    <span class="font-medium">Depósito de Garantía Sugerido:</span> ${{ parseFloat(calculatedDepositRequired).toFixed(2) }} (para clientes extranjeros)
                </p>
                <p class="text-sm mt-1">
                    <span class="font-medium">Monto Total a Pagar al Inicio:</span> ${{ parseFloat(calculatedTotalDueAtStart).toFixed(2) }}
                </p>
                <p class="text-sm mt-1">
                    <span class="font-medium">Alquileres Activos del Cliente:</span> {{ estimatedCustomerActiveRentals }}
                </p>
                <div v-if="loadingPriceCalc" class="text-xs text-gray-500 mt-2">Recalculando precio y validaciones...</div>

                <hr class="my-4"/>
                <h4 class="text-md font-semibold mb-3">Información del Primer Pago Obligatorio:</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField label="Monto del Pago Inicial" required>
                        <FormControl
                            v-model.number="form.initialPaymentAmount"
                            id="initial_payment_amount"
                            type="text"
                            step="0,01"
                            :min="0" :disabled="loading || loadingPriceCalc"
                        />
                        <p class="text-xs text-gray-500 mt-1">
                            Sugerido: ${{ parseFloat(calculatedTotalDueAtStart).toFixed(2) }}
                        </p>
                    </FormField>

                    <FormField label="Método de Pago Inicial" required>
                        <FormControl
                            v-model="form.initialPaymentType"
                            id="initial_payment_type"
                            :options="paymentTypeOptions"
                            placeholder="Seleccione método de pago"
                            type="select"
                            :disabled="loading || loadingPriceCalc"
                        />
                    </FormField>

                    <FormField label="Concepto del Pago Inicial" required>
                        <FormControl
                            v-model="form.initialPaymentConcept"
                            id="initial_payment_concept"
                            :options="conceptOptions"
                            placeholder="Seleccione concepto"
                            type="select"
                            :disabled="loading || loadingPriceCalc"
                        />
                    </FormField>

                    <FormField label="Referencia del Pago Inicial (Opcional)">
                        <FormControl
                            v-model="form.initialPaymentReference"
                            id="initial_payment_reference"
                            type="textarea"
                            placeholder="Ej: Depósito de seguridad, 50% anticipo, etc."
                            :disabled="loading || loadingPriceCalc"
                        />
                    </FormField>
                </div>
            </div>
            <div v-else-if="form.customer && form.vehicle && form.start_date && form.end_date" class="mt-6 p-4 text-center text-gray-500">
                Ingresa las fechas y selecciona Cliente/Vehículo para calcular el precio estimado.
            </div>
            <div v-else class="mt-6 p-4 text-center text-gray-500">
                Complete los campos de Cliente, Vehículo y Fechas para ver el cálculo de precio.
            </div>
            ---

            <template #footer>
                <BaseButtons>
                    <BaseButton
                        color="info"
                        type="submit"
                        :disabled="loading || loadingPriceCalc || !canCreateRental"
                        :label="loading ? 'Creando Renta...' : 'Crear Renta y Registrar Pago Inicial'"
                        :icon="mdiPlus"
                    />
                    <BaseButton
                        color="whiteDark"
                        label="Cancelar"
                        @click="cancelForm"
                        outline
                        :disabled="loading"
                    />
                </BaseButtons>
            </template>
        </CardBox>
    </LayoutAuthenticated>
</template>