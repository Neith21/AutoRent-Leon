<script setup>
import { ref, watch, reactive, computed } from 'vue';
import axios from 'axios';
import { useMainStore } from '@/stores/main';
import BaseButton from '@/components/BaseButton.vue';
import { mdiClose } from '@mdi/js';

const mainStore = useMainStore();

// --- Props y Emits ---
const props = defineProps({
    show: {
        type: Boolean,
        default: false,
    },
    rental: {
        type: Object,
        default: null,
    },
});

const emit = defineEmits([
    'update:show',
    'close',
    'error',
    'rentalFinalized'
]);

// --- Constantes y Opciones de Configuración ---
const API_URL = import.meta.env.VITE_API_URL;
const FUEL_LEVEL_CHOICES = ['Vacio', '1/4', '1/2', '3/4', 'Lleno'];
const FUEL_COST_PER_LEVEL = 15.00;
const DEPOSIT_AMOUNT_FOREIGNER = 100.00; // Este es el monto del DEPÓSITO de garantía para extranjeros

// --- Estado Reactivo del Componente ---
const rentalDetails = ref(null);
const isLoading = ref(false);

const alertMessage = ref('');
const alertType = ref('');
const alertClasses = computed(() => {
    return {
        'bg-green-100 border border-green-400 text-green-700': alertType.value === 'success',
        'bg-red-100 border border-red-400 text-red-700': alertType.value === 'danger',
        'bg-yellow-100 border border-yellow-400 text-yellow-700': alertType.value === 'warning',
    };
});

const formData = reactive({
    actual_return_date: getFormattedCurrentDateTime(),
    fuel_level_return: 'Lleno',
    remarks: '',
    final_payment_amount: 0,
    final_payment_type: '',
    final_payment_reference: '',
    final_payment_concept: 'Pago Final', // ¡CORRECCIÓN: 'Pago Final' con F mayúscula!
});

// Computed para determinar si el cliente es extranjero
const isForeigner = computed(() => rentalDetails.value?.customer_type?.toLowerCase() === 'extranjero');

// Computed para determinar si el concepto de pago seleccionado es un reembolso
// Ahora solo verificamos si el concepto es 'Reembolso'
const isRefundConcept = computed(() => 
    formData.final_payment_concept === 'Reembolso'
);

// Computed para decidir si mostrar el formulario de pago/reembolso manual
const shouldShowPaymentForm = computed(() => {
    if (!rentalDetails.value) {
        return false;
    }
    return calculatedSummary.value.remaining_balance_required > 0 || calculatedSummary.value.total_refund_amount > 0;
});


// Observar cambios en el concepto de pago para ajustar el monto automáticamente
watch(() => formData.final_payment_concept, (newConcept) => {
    if (newConcept === 'Reembolso') { // ¡CORRECCIÓN: Solo verificar 'Reembolso'!
        formData.final_payment_amount = -calculatedSummary.value.total_refund_amount;
    } else if (newConcept === 'Pago Final') { // ¡CORRECCIÓN: 'Pago Final' con F mayúscula!
        formData.final_payment_amount = calculatedSummary.value.remaining_balance_required > 0 ? calculatedSummary.value.remaining_balance_required : 0;
    } else {
        formData.final_payment_amount = 0;
    }
});


const calculatedSummary = computed(() => {
    if (!rentalDetails.value) {
        return {
            fuel_charge: 0,
            overdue_charge: 0,
            days_overdue: 0,
            total_amount_to_cover: 0,
            total_paid_for_rental: 0,
            remaining_balance_required: 0,
            deposit_paid: 0,
            total_refund_amount: 0,
        };
    }

    const { total_price, end_date, fuel_level_pickup, vehicle_daily_price, customer_type, payments } = rentalDetails.value;
    const { actual_return_date, fuel_level_return } = formData;

    let currentFuelCharge = 0;
    let currentOverdueCharge = 0;
    let currentDaysOverdue = 0;
    let totalPaidForService = 0;
    let depositReceived = 0;

    (payments || []).forEach(p => {
        if (p.concept === 'Depósito') {
            depositReceived += parseFloat(p.amount);
        } else if (p.concept !== 'Reembolso') { // ¡CORRECCIÓN: Solo excluir 'Reembolso' si ya no tienes los otros conceptos largos!
            totalPaidForService += parseFloat(p.amount);
        }
    });

    if (isForeigner.value && depositReceived < DEPOSIT_AMOUNT_FOREIGNER) {
        depositReceived = DEPOSIT_AMOUNT_FOREIGNER;
        console.warn("FinalizeRentalModal: Cliente extranjero con depósito pagado menor a $100. Asumiendo $100 para cálculo de finalización.");
    }


    const parseDateForCalculation = (dateString) => {
        if (!dateString) return new Date(NaN);

        let date = new Date(dateString);
        if (isNaN(date.getTime())) {
            let match = dateString.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})(:\d{2})?$/);
            if (match) {
                const year = parseInt(match[1]);
                const month = parseInt(match[2]) - 1;
                const day = parseInt(match[3]);
                const hours = parseInt(match[4]);
                const minutes = parseInt(match[5]);
                const seconds = match[6] ? parseInt(match[6].substring(1)) : 0;
                date = new Date(year, month, day, hours, minutes, seconds);
            } else {
                match = dateString.match(/^(\d{2})-(\d{2})-(\d{4}) (\d{2}):(\d{2})(:\d{2})?$/);
                if (match) {
                    const day = parseInt(match[1]);
                    const month = parseInt(match[2]) - 1;
                    const year = parseInt(match[3]);
                    const hours = parseInt(match[4]);
                    const minutes = parseInt(match[5]);
                    const seconds = match[6] ? parseInt(match[6].substring(1)) : 0;
                    date = new Date(year, month, day, hours, minutes, seconds);
                } else {
                    return new Date(NaN);
                }
            }
        }
        return date;
    };


    const expectedReturnDate = parseDateForCalculation(end_date);
    const actualReturnDateObj = parseDateForCalculation(actual_return_date);

    if (isNaN(expectedReturnDate.getTime()) || isNaN(actualReturnDateObj.getTime())) {
        console.error('FinalizeRentalModal: Fechas inválidas para cálculo de retraso. Expected:', end_date, 'Actual:', actual_return_date);
        currentOverdueCharge = 0;
        currentDaysOverdue = 0;
    } else {
        const fuelLevelMap = new Map(FUEL_LEVEL_CHOICES.map((level, index) => [level, index]));
        const pickupLevel = fuelLevelMap.get(fuel_level_pickup);
        const returnLevel = fuelLevelMap.get(fuel_level_return);

        if (returnLevel < pickupLevel) {
            currentFuelCharge = (pickupLevel - returnLevel) * FUEL_COST_PER_LEVEL;
        }

        if (actualReturnDateObj.getTime() > expectedReturnDate.getTime()) {
            const diffMilliseconds = actualReturnDateObj.getTime() - expectedReturnDate.getTime();
            const diffHours = diffMilliseconds / (1000 * 60 * 60);
            let rawDaysOverdue = Math.ceil(diffHours / 24);

            if (rawDaysOverdue <= 0 && diffMilliseconds > 0) {
                rawDaysOverdue = 1;
            }
            
            const dailyPrice = parseFloat(vehicle_daily_price || 0); 
            
            if (rawDaysOverdue <= 3) {
                currentOverdueCharge = dailyPrice * rawDaysOverdue;
            } else if (rawDaysOverdue > 3 && rawDaysOverdue <= 7) {
                currentOverdueCharge = dailyPrice * rawDaysOverdue * 2;
            } else {
                currentOverdueCharge = dailyPrice * 7 * 2;
            }
            
            currentDaysOverdue = rawDaysOverdue;
        }
    }

    const totalOriginalRentalPriceFromBackend = parseFloat(total_price || 0);

    const totalAmountToCover = (totalOriginalRentalPriceFromBackend + currentOverdueCharge + currentFuelCharge);
    
    let remainingBalanceForService = totalAmountToCover - totalPaidForService;

    let totalRefundAmount = 0;

    if (remainingBalanceForService < 0) {
        totalRefundAmount += Math.abs(remainingBalanceForService);
        remainingBalanceForService = 0;
    }

    if (depositReceived > 0 && remainingBalanceForService <= 0) {
        totalRefundAmount += depositReceived;
    }
    
    return {
        fuel_charge: parseFloat(currentFuelCharge.toFixed(2)),
        overdue_charge: parseFloat(currentOverdueCharge.toFixed(2)),
        days_overdue: currentDaysOverdue,
        total_amount_to_cover: parseFloat(totalAmountToCover.toFixed(2)),
        total_paid_for_rental: parseFloat(totalPaidForService.toFixed(2)),
        remaining_balance_required: parseFloat(remainingBalanceForService.toFixed(2)),
        deposit_paid: parseFloat(depositReceived.toFixed(2)),
        total_refund_amount: parseFloat(totalRefundAmount.toFixed(2)),
    };
});


// --- Funciones Utilitarias Nativas ---

function getAuthHeaders() {
    const token = localStorage.getItem('autorent_leon_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

function formatCurrency(value) {
    if (value === null || value === undefined || isNaN(parseFloat(value))) return '$0.00';
    return `$${parseFloat(value).toFixed(2)}`;
}

function getFormattedCurrentDateTime() {
    const now = new Date();
    const year = now.getFullYear();
    const month = (now.getMonth() + 1).toString().padStart(2, '0');
    const day = now.getDate().toString().padStart(2, '0');
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

function formatDateTimeDisplay(dateString) {
    if (!dateString) return 'N/A';

    let date;
    date = new Date(dateString);

    if (isNaN(date.getTime())) {
        let match = dateString.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})(:\d{2})?$/);
        if (match) {
            const year = parseInt(match[1]);
            const month = parseInt(match[2]) - 1;
            const day = parseInt(match[3]);
            const hours = parseInt(match[4]);
            const minutes = parseInt(match[5]);
            const seconds = match[6] ? parseInt(match[6].substring(1)) : 0;
            date = new Date(year, month, day, hours, minutes, seconds);
        } else {
            match = dateString.match(/^(\d{2})-(\d{2})-(\d{4}) (\d{2}):(\d{2})(:\d{2})?$/);
            if (match) {
                const day = parseInt(match[1]);
                const month = parseInt(match[2]) - 1;
                const year = parseInt(match[3]);
                const hours = parseInt(match[4]);
                const minutes = parseInt(match[5]);
                const seconds = match[6] ? parseInt(match[6].substring(1)) : 0;
                date = new Date(year, month, day, hours, minutes, seconds);
            } else {
                return 'Fecha inválida';
            }
        }
    }

    if (isNaN(date.getTime())) {
        return 'Fecha inválida';
    }

    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${day}-${month}-${year} ${hours}:${minutes}`;
}


function showAlert(message, type = 'danger') {
    alertMessage.value = message;
    alertType.value = type;
    mainStore.notify({
        color: type === 'success' ? 'success' : 'danger',
        message: message,
    });
}

function clearAlert() {
    alertMessage.value = '';
    alertType.value = '';
}

// --- Funciones de API (Con Axios) ---

async function fetchRentalDetails(rentalId) {
    console.log(`[API Call] Intentando GET ${API_URL}rental/${rentalId}/`);
    try {
        const response = await axios.get(`${API_URL}rental/${rentalId}/`, {
            headers: getAuthHeaders()
        });
        console.log(`[API Success] Detalles de renta ${rentalId} obtenidos:`, response.data);
        return response.data;
    } catch (error) {
        console.error(`[API Error] Error al obtener detalles de la renta ${rentalId}:`, error.response?.data || error.message);
        console.error(`[API Error] URL intentada: ${API_URL}rental/${rentalId}/`);
        console.error(`[API Error] Headers enviados:`, getAuthHeaders());
        throw error;
    }
}

async function submitFinalization() {
    if (!rentalDetails.value?.id) {
        showAlert('No se pudo finalizar la renta. ID de renta no disponible.', 'danger');
        return;
    }

    isLoading.value = true;
    clearAlert();

    const payload = {
        actual_return_date: formData.actual_return_date,
        fuel_level_return: formData.fuel_level_return,
        remarks: formData.remarks,
    };

    let finalPaymentObject = null;

    if (shouldShowPaymentForm.value) { 
        if (formData.final_payment_amount === 0 && (calculatedSummary.value.remaining_balance_required > 0 || calculatedSummary.value.total_refund_amount > 0)) {
            let msg = 'Por favor, ingresa el monto para cubrir el saldo pendiente o realizar el reembolso.';
            if (calculatedSummary.value.remaining_balance_required > 0) {
                msg = `Existe un saldo pendiente de ${formatCurrency(calculatedSummary.value.remaining_balance_required)}. Por favor, ingresa el monto a pagar.`;
            } else if (calculatedSummary.value.total_refund_amount > 0) {
                msg = `Existe un monto a reembolsar de ${formatCurrency(calculatedSummary.value.total_refund_amount)}. Por favor, ingresa el monto del reembolso.`;
            }
            showAlert(msg, 'warning');
            isLoading.value = false;
            return;
        }

        if (!formData.final_payment_type) {
            showAlert('Por favor, selecciona un tipo de pago/reembolso.', 'warning');
            isLoading.value = false;
            return;
        }

        let amountToSend = parseFloat(formData.final_payment_amount);
        // ¡CORRECCIÓN: El concepto ahora siempre es 'Reembolso', el detalle va en reference!
        let conceptToSend = formData.final_payment_concept; 
        let referenceToSend = formData.final_payment_reference;

        if (isRefundConcept.value) { // Si el concepto en el formulario es 'Reembolso'
            amountToSend = -Math.abs(amountToSend); // Asegura que el monto sea negativo para reembolsos
            conceptToSend = 'Reembolso'; // El concepto enviado al backend es SOLO 'Reembolso'

            // Construir la referencia para el reembolso
            let refundDetail = '';
            if (calculatedSummary.value.deposit_paid > 0 && calculatedSummary.value.total_refund_amount >= calculatedSummary.value.deposit_paid) {
                if (calculatedSummary.value.total_refund_amount === calculatedSummary.value.deposit_paid) {
                    refundDetail = 'Depósito';
                } else if (isForeigner.value && calculatedSummary.value.deposit_paid === DEPOSIT_AMOUNT_FOREIGNER) {
                    refundDetail = 'Depósito Extranjero';
                } else {
                    refundDetail = 'Depósito y/o Sobrepago';
                }
            } else if (calculatedSummary.value.remaining_balance_required < 0) {
                refundDetail = 'Sobrepago del servicio';
            }
            referenceToSend = `Reembolso de ${refundDetail} Renta #${rentalDetails.value.id}`.trim();
            if (formData.final_payment_reference) { // Si el usuario añadió más detalle
                referenceToSend += ` (${formData.final_payment_reference})`;
            }

        } else { // Si no es un concepto de reembolso, se envía lo que el usuario puso
            amountToSend = Math.abs(amountToSend); // Asegura que el monto sea positivo para pagos
            conceptToSend = formData.final_payment_concept; // Usa el concepto del formulario (ej. 'Pago Final')
            referenceToSend = formData.final_payment_reference || `Pago Renta #${rentalDetails.value.id}`;
        }
        
        finalPaymentObject = {
            amount: amountToSend,
            payment_type: formData.final_payment_type,
            reference: referenceToSend, // ¡CORRECCIÓN: Aquí va el detalle del reembolso!
            concept: conceptToSend, // ¡CORRECCIÓN: Aquí va SOLO 'Reembolso' o 'Pago Final'!
        };
    }

    payload.final_payment = finalPaymentObject; 

    console.log('[API Call] Intentando finalizar renta con payload:', payload);

    try {
        const response = await axios.post(`${API_URL}rental/${rentalDetails.value.id}/finalize/`, payload, {
            headers: getAuthHeaders(),
        });
        console.log('[API Success] Renta finalizada:', response.data);
        showAlert('Renta finalizada exitosamente. Saldo ajustado.', 'success');
        emit('rentalFinalized');
        handleClose();

    } catch (error) {
        console.error('[API Error] Error al finalizar la renta:', error.response?.data || error.message);
        const errorData = error.response?.data;
        let errorMessage = 'Ocurrió un error al finalizar la renta.';

        if (errorData) {
            if (errorData.detail) {
                errorMessage = errorData.detail;
            } else if (errorData.non_field_errors) {
                errorMessage = errorData.non_field_errors.join(' ');
            } else if (errorData.final_payment) { 
                errorMessage = `Error en el pago/reembolso: ${Object.values(errorData.final_payment).flat().join(' ')}`;
            } else {
                errorMessage = Object.values(errorData).flat().join(' ');
            }
        }
        showAlert(errorMessage, 'danger');

    } finally {
        isLoading.value = false;
    }
}


async function loadRentalDetails(id) {
    isLoading.value = true;
    clearAlert();
    try {
        console.log('FinalizeRentalModal: Iniciando carga de detalles para ID:', id);
        const data = await fetchRentalDetails(id);
        rentalDetails.value = data;
        
        // Inicializar formData.final_payment_amount basado en el cálculo inicial
        if (calculatedSummary.value.total_refund_amount > 0) {
            // ¡CORRECCIÓN: El concepto para reembolso SIEMPRE es 'Reembolso'!
            formData.final_payment_concept = 'Reembolso'; 
            formData.final_payment_amount = -calculatedSummary.value.total_refund_amount;
        } else if (calculatedSummary.value.remaining_balance_required > 0) {
            formData.final_payment_concept = 'Pago Final'; // ¡CORRECCIÓN: 'Pago Final' con F mayúscula!
            formData.final_payment_amount = calculatedSummary.value.remaining_balance_required;
        } else {
            formData.final_payment_concept = 'Pago Final'; // ¡CORRECCIÓN: 'Pago Final' con F mayúscula!
            formData.final_payment_amount = 0;
        }

    } catch (err) {
        console.error("FinalizeRentalModal: Error general en loadRentalDetails:", err);
        showAlert('No se pudieron cargar los detalles de la renta. Inténtalo de nuevo.', 'danger');
        emit('error', 'Error al cargar detalles de la renta.');
    } finally {
        isLoading.value = false;
    }
}

function resetModalState() {
    rentalDetails.value = null;
    isLoading.value = false;
    formData.actual_return_date = getFormattedCurrentDateTime();
    formData.fuel_level_return = 'Lleno';
    formData.remarks = '';
    formData.final_payment_amount = 0;
    formData.final_payment_type = '';
    formData.final_payment_reference = '';
    formData.final_payment_concept = 'Pago Final';
    clearAlert();
    console.log('FinalizeRentalModal: Estado del modal reseteado.');
}

watch(() => props.show, async (newVal) => {
    console.log(`FinalizeRentalModal: 'show' prop cambió a ${newVal}.`);
    if (newVal) {
        if (props.rental?.id) {
            resetModalState();
            console.log('FinalizeRentalModal: Abriendo modal para renta con ID:', props.rental.id);
            await loadRentalDetails(props.rental.id);
        } else {
            console.warn('FinalizeRentalModal: Modal abierto, pero no se proporcionó un ID de renta válido. La carga de detalles no se realizará.');
            showAlert('No se pudo abrir la renta. No se proporcionó un ID válido.', 'danger');
            emit('error', 'ID de renta inválido.');
        }
    } else {
        resetModalState();
        console.log('FinalizeRentalModal: Cerrando modal de renta.');
    }
}, { immediate: true });


const handleClose = () => {
    emit('update:show', false);
    emit('close');
    console.log('FinalizeRentalModal: handleClose ejecutado. Emitiendo cierre.');
};
</script>

<template>
  <Transition name="fade">
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md"
      @click.self="handleClose"
      tabindex="-1"
      @keydown.esc="handleClose"
    >
      <div
        class="w-full max-w-4xl mx-4 bg-white rounded-2xl shadow-lg transition-all p-6"
        @click.stop
      >
        <div class="flex justify-between items-center pb-4 border-b border-gray-200">
          <h2 class="text-2xl font-semibold text-gray-800">
            Finalizar Renta #{{ rental ? rental.id : '' }} - {{ rentalDetails?.vehicle_plate || 'Cargando...' }}
          </h2>
          <button
            @click="handleClose"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg :width="24" :height="24" viewBox="0 0 24 24">
              <path :d="mdiClose" fill="currentColor" />
            </svg>
          </button>
        </div>

        <div class="mt-6 space-y-4 max-h-[70vh] overflow-y-auto pr-2">
            <div v-if="alertMessage" :class="['p-3 rounded-md flex items-center justify-between', alertClasses]" role="alert">
                <span>{{ alertMessage }}</span>
                <button type="button" class="text-white opacity-70 hover:opacity-100" @click="clearAlert">
                    <svg :width="16" :height="16" viewBox="0 0 24 24">
                        <path :d="mdiClose" fill="currentColor" />
                    </svg>
                </button>
            </div>

            <div v-if="isLoading" class="text-center text-gray-600 py-8">
              <div class="spinner-border text-blue-500 mb-2"></div>
              <p>Cargando detalles de la renta...</p>
            </div>

            <div v-else-if="rentalDetails">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 text-gray-700">
                <p><strong>Cliente:</strong> {{ rentalDetails.customer_name }} ({{ rentalDetails.customer_type }})</p>
                <p><strong>Vehículo:</strong> {{ rentalDetails.vehicle_make }} {{ rentalDetails.vehicle_model }} ({{ rentalDetails.vehicle_plate }})</p>
                <p><strong>Precio Diario del Vehículo:</strong> {{ formatCurrency(rentalDetails.vehicle_daily_price) }}</p>
                <p><strong>Precio Base de Alquiler:</strong> {{ formatCurrency(rentalDetails.total_price) }}</p>
                <p><strong>Fecha Inicio:</strong> {{ formatDateTimeDisplay(rentalDetails.start_date) }}</p>
                <p><strong>Fecha Fin (Esperada):</strong> {{ formatDateTimeDisplay(rentalDetails.end_date) }}</p>
                <p><strong>Nivel Combustible al Recoger:</strong> {{ rentalDetails.fuel_level_pickup }}</p>
                <p><strong>Total Pagado (Alquiler):</strong> {{ formatCurrency(calculatedSummary.total_paid_for_rental) }}</p>
              </div>

              <hr class="my-6 border-gray-200" />

              <h3 class="text-xl font-semibold text-gray-800 mb-4">Datos de Devolución</h3>
              <div class="space-y-4 mb-6">
                  <div>
                      <label for="actualReturnDate" class="block text-sm font-medium text-gray-700">Fecha y Hora de Devolución Real:</label>
                      <input
                          type="datetime-local"
                          id="actualReturnDate"
                          v-model="formData.actual_return_date"
                          :max="getFormattedCurrentDateTime()"
                          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                      />
                  </div>

                  <div>
                      <label for="fuelLevelReturn" class="block text-sm font-medium text-gray-700">Nivel de Combustible al Devolver:</label>
                      <select
                          id="fuelLevelReturn"
                          v-model="formData.fuel_level_return"
                          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                      >
                          <option v-for="level in FUEL_LEVEL_CHOICES" :key="level" :value="level">
                              {{ level }}
                          </option>
                      </select>
                  </div>
              </div>
              <hr class="my-6 border-gray-200" />


              <h3 class="text-xl font-semibold text-gray-800 mb-4">Resumen de Cargos y Saldo</h3>
              <ul class="space-y-2 text-gray-700">
                <li class="flex justify-between items-center bg-gray-50 p-3 rounded-md">
                  <span>Cargo por Combustible:</span>
                  <span class="font-semibold text-yellow-700">{{ formatCurrency(calculatedSummary.fuel_charge) }}</span>
                </li>
                <li class="flex justify-between items-center bg-gray-50 p-3 rounded-md">
                  <span>Cargo por Retraso ({{ calculatedSummary.days_overdue }} días):</span>
                  <span class="font-semibold text-yellow-700">{{ formatCurrency(calculatedSummary.overdue_charge) }}</span>
                </li>
                <li class="flex justify-between items-center bg-blue-50 p-3 rounded-md font-bold">
                  <span>Costo Total (Renta + Cargos):</span>
                  <span class="text-blue-700">{{ formatCurrency(calculatedSummary.total_amount_to_cover) }}</span>
                </li>
                <li class="flex justify-between items-center bg-green-50 p-3 rounded-md">
                  <span>Pagado (Alquiler):</span>
                  <span class="font-semibold text-green-700">{{ formatCurrency(calculatedSummary.total_paid_for_rental) }}</span>
                </li>
                <li v-if="calculatedSummary.deposit_paid > 0" class="flex justify-between items-center bg-blue-50 p-3 rounded-md">
                    <span>Depósito de Garantía Pagado:</span>
                    <span class="font-semibold text-blue-700">{{ formatCurrency(calculatedSummary.deposit_paid) }}</span>
                </li>
                <li class="flex justify-between items-center p-3 rounded-md font-bold"
                    :class="{ 'bg-red-50 text-red-700': calculatedSummary.remaining_balance_required > 0, 'bg-green-50 text-green-700': calculatedSummary.remaining_balance_required <= 0 }">
                  <span>Saldo Pendiente:</span>
                  <span>
                    {{ formatCurrency(calculatedSummary.remaining_balance_required - calculatedSummary.deposit_paid) }}
                  </span>
                </li>
                <li v-if="calculatedSummary.deposit_to_refund > 0"
                    class="flex justify-between items-center bg-yellow-50 p-3 rounded-md">
                  <span>Monto a Reembolsar (Depósito):</span>
                  <span class="font-semibold text-yellow-700">
                    {{ formatCurrency(calculatedSummary.deposit_to_refund) }}
                  </span>
                </li>
              </ul>

              <hr class="my-6 border-gray-200" />

              <h3 v-if="shouldShowPaymentForm" class="text-xl font-semibold text-gray-800 mb-4">Registro de Pago/Reembolso</h3>
              <form @submit.prevent="submitFinalization" class="space-y-4">
                  <div v-if="shouldShowPaymentForm" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                          <label for="finalPaymentConcept" class="block text-sm font-medium text-gray-700">Concepto de Pago:</label>
                          <select
                              id="finalPaymentConcept"
                              v-model="formData.final_payment_concept"
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                              required
                          >
                              <option value="Pago Final">Pago final</option>
                              <option value="Depósito">Depósito</option>
                              <option value="Cargo por Combustible">Cargo por Combustible</option>
                              <option value="Cargo por Retraso">Cargo por Retraso</option>
                              <option v-if="calculatedSummary.deposit_to_refund > 0" value="Reembolso de Depósito">Reembolso de Depósito</option>
                          </select>
                      </div>
                      <div>
                          <label for="finalPaymentAmount" class="block text-sm font-medium text-gray-700">Monto:</label>
                          <input
                              type="text"
                              id="finalPaymentAmount"
                              v-model.number="formData.final_payment_amount"
                              :min="0"
                              step="0.01"
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                              required
                          />
                      </div>
                  </div>
                  <div v-if="shouldShowPaymentForm" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                          <label for="finalPaymentType" class="block text-sm font-medium text-gray-700">Tipo de Pago:</label>
                          <select
                              id="finalPaymentType"
                              v-model="formData.final_payment_type"
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                              required
                          >
                              <option value="">Selecciona un tipo</option>
                              <option value="Efectivo">Efectivo</option>
                              <option value="Tarjeta de Crédito">Tarjeta de Crédito</option>
                              <option value="Transferencia">Transferencia Bancaria</option>
                          </select>
                      </div>
                      <div>
                          <label for="finalPaymentReference" class="block text-sm font-medium text-gray-700">Referencia (Opcional):</label>
                          <input
                              type="text"
                              id="finalPaymentReference"
                              v-model="formData.final_payment_reference"
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          />
                      </div>
                  </div>

                  <div class="mt-4">
                      <label for="remarks" class="block text-sm font-medium text-gray-700">Comentarios (Opcional):</label>
                      <textarea
                          id="remarks"
                          v-model="formData.remarks"
                          rows="3"
                          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      ></textarea>
                  </div>

                  <div class="flex justify-end gap-2 pt-4 border-t border-gray-200 mt-6">
                      <BaseButton
                          label="Cerrar"
                          color="white"
                          @click="handleClose"
                          type="button"
                      />
                      <BaseButton
                          label="Finalizar Renta"
                          color="blue"
                          type="submit"
                          :disabled="isLoading"
                      />
                  </div>
              </form>
            </div>
            <div v-else class="text-center text-red-500 py-8">
              <p>No se pudo cargar la información de la renta. Inténtalo de nuevo.</p>
            </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
/* Transición de entrada/salida para el modal */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Spinner básico para la carga de datos */
.spinner-border {
  display: inline-block;
  width: 3rem; /* Tamaño más grande */
  height: 3rem;
  vertical-align: -0.125em;
  border: 0.3em solid currentColor; /* Grosor del borde */
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>