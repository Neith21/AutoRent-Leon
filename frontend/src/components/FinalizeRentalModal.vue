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
                    {{ formatCurrency(calculatedSummary.remaining_balance_required) }}
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
                              <option value="Pago final">Pago final</option>
                              <option value="Depósito">Depósito</option>
                              <option value="Cargo por Combustible">Cargo por Combustible</option>
                              <option value="Cargo por Retraso">Cargo por Retraso</option>
                              <option v-if="calculatedSummary.deposit_to_refund > 0" value="Reembolso de Depósito">Reembolso de Depósito</option>
                          </select>
                      </div>
                      <div>
                          <label for="finalPaymentAmount" class="block text-sm font-medium text-gray-700">Monto:</label>
                          <input
                              type="number"
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
                              <option value="Transferencia Bancaria">Transferencia Bancaria</option>
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
    final_payment_concept: 'Pago final', // Valor por defecto
});

// Computed para determinar si el cliente es extranjero
const isForeigner = computed(() => rentalDetails.value?.customer_type?.toLowerCase() === 'extranjero');

// Computed para determinar si el concepto de pago seleccionado es un reembolso
const isRefundConcept = computed(() => 
    formData.final_payment_concept === 'Reembolso de Depósito' || 
    formData.final_payment_concept === 'Reembolso de Depósito Extranjero'
);

// Computed para decidir si mostrar el formulario de pago/reembolso manual
const shouldShowPaymentForm = computed(() => {
    if (!rentalDetails.value) {
        return false;
    }
    // El formulario de pago/reembolso SÓLO se mostrará si hay un saldo pendiente > 0.
    // Si el saldo es 0 o negativo (lo que implica un reembolso o que no se debe nada),
    // el formulario se ocultará y la lógica de submitFinalization manejará los reembolsos.
    return calculatedSummary.value.remaining_balance_required > 0 ||
           (calculatedSummary.value.deposit_to_refund > 0 && calculatedSummary.value.deposit_to_refund !== DEPOSIT_AMOUNT_FOREIGNER);
});


// Observar cambios en el concepto de pago para ajustar el monto automáticamente
watch(() => formData.final_payment_concept, (newConcept) => {
  if (isRefundConcept.value) { // Usamos la nueva computed `isRefundConcept`
    // Si es reembolso de depósito, el monto debe ser negativo y reflejar el potencial reembolso
    formData.final_payment_amount = -calculatedSummary.value.deposit_to_refund;
  } else if (newConcept === 'Pago final') {
    // Si es pago final, el monto debe ser el saldo pendiente
    formData.final_payment_amount = calculatedSummary.value.remaining_balance_required > 0 ? calculatedSummary.value.remaining_balance_required : 0;
  } else {
    // Para otros conceptos de pago, el monto inicial es 0
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
            deposit_to_refund: 0,
        };
    }

    const { total_price, end_date, fuel_level_pickup, vehicle_daily_price, customer_type, payments } = rentalDetails.value;
    const { actual_return_date, fuel_level_return } = formData;

    let currentFuelCharge = 0;
    let currentOverdueCharge = 0;
    let currentDaysOverdue = 0;
    let totalPaidForRental = 0;
    let depositPaid = 0;

    // Calcular total_paid_for_rental y deposit_paid desde los pagos existentes
    (payments || []).forEach(p => {
        // Para el cálculo del 'depositPaid', buscamos específicamente el depósito de garantía.
        // Si es extranjero, solo consideramos el pago de 100 como depósito, si existe.
        // Si no es extranjero, sumamos todos los pagos con concepto 'Depósito'.
        if (p.concept === 'Depósito') {
            if (isForeigner.value && parseFloat(p.amount) === DEPOSIT_AMOUNT_FOREIGNER) {
                 depositPaid = parseFloat(p.amount); // El depósito para extranjeros es fijo de 100
            } else if (!isForeigner.value) {
                depositPaid += parseFloat(p.amount); // Para no extranjeros, sumamos los depósitos normales
            }
        }
        // Sumar todos los pagos que no son depósitos (y no son reembolsos específicos)
        if (p.concept !== 'Depósito' && p.concept !== 'Reembolso de Depósito' && p.concept !== 'Reembolso de Depósito Extranjero') {
            totalPaidForRental += parseFloat(p.amount);
        }
    });

    // Si es un cliente extranjero y no tiene un pago de depósito de 100 registrado,
    // para los cálculos de la finalización asumimos que su depósito debería ser 100.
    // Esto es crucial para que el "deposit_to_refund" y "remaining_balance_required"
    // se calculen como si los $100 estuvieran presentes.
    // Esto no crea un pago real, solo afecta la visualización y cálculo dentro del modal.
    if (isForeigner.value && depositPaid === 0) {
        // Asume que el depósito de 100 se debe considerar para el cálculo,
        // incluso si no se registró un pago con el concepto "Depósito" por 100.
        // Esto ayuda a que el "saldo pendiente" y "monto a reembolsar" sean correctos.
        // El formulario de pago/reembolso se mostrará si el cliente aún debe el depósito de 100.
        depositPaid = DEPOSIT_AMOUNT_FOREIGNER;
        console.warn("FinalizeRentalModal: Cliente extranjero sin pago de depósito de $100 registrado. Asumiendo $100 para cálculo de finalización.");
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
        // 1. Cálculo de cargos por combustible
        const fuelLevelMap = new Map(FUEL_LEVEL_CHOICES.map((level, index) => [level, index]));
        const pickupLevel = fuelLevelMap.get(fuel_level_pickup);
        const returnLevel = fuelLevelMap.get(fuel_level_return);

        if (returnLevel < pickupLevel && returnLevel < fuelLevelMap.get('3/4')) {
            currentFuelCharge = (pickupLevel - returnLevel) * FUEL_COST_PER_LEVEL;
        }

        // 2. Cálculo de cargos por retraso (días)
        if (actualReturnDateObj.getTime() > expectedReturnDate.getTime()) {
            const diffMilliseconds = actualReturnDateObj.getTime() - expectedReturnDate.getTime();
            const diffHours = diffMilliseconds / (1000 * 60 * 60);
            let rawDaysOverdue = Math.ceil(diffHours / 24);

            if (rawDaysOverdue <= 0 && diffMilliseconds > 0) {
                rawDaysOverdue = 1; // Asegura al menos 1 día si hay cualquier retraso
            }
            
            const dailyPrice = parseFloat(vehicle_daily_price || 0); 
            
            // Lógica corregida para el cargo por retraso
            if (rawDaysOverdue <= 3) {
                currentOverdueCharge = dailyPrice * rawDaysOverdue;
            } else if (rawDaysOverdue > 3 && rawDaysOverdue <= 7) {
                // Para días entre 4 y 7 (inclusive), se cobra el doble de la tarifa diaria
                currentOverdueCharge = dailyPrice * rawDaysOverdue * 2;
            } else { // Más de 7 días, el cargo se mantiene como si fueran 7 días
                currentOverdueCharge = dailyPrice * 7 * 2; // Cargo por los 7 días con tarifa doble
            }
            
            currentDaysOverdue = rawDaysOverdue; // Muestra los días reales de retraso
        }
    }

    const totalOriginalPrice = parseFloat(total_price || 0);
    const totalAmountToCover = (totalOriginalPrice + currentOverdueCharge + currentFuelCharge);
    
    // El saldo restante se calcula restando lo pagado por el alquiler (sin incluir el depósito)
    let remainingBalance = totalAmountToCover - totalPaidForRental;

    let depositToRefund = 0;

    // Lógica de reembolso del depósito
    if (depositPaid > 0) {
        if (remainingBalance <= 0) { // Si no hay deuda o hay saldo a favor
            depositToRefund = depositPaid;
            remainingBalance = 0; // Se asume que el depósito cubre todo, y el saldo pendiente se convierte en 0
        } else if (remainingBalance > 0 && remainingBalance < depositPaid) { // Si la deuda es menor que el depósito
            depositToRefund = depositPaid - remainingBalance;
            remainingBalance = 0; // La deuda se cubre completamente con el depósito
        } else { // Si la deuda es mayor o igual al depósito
            remainingBalance -= depositPaid;
            depositToRefund = 0;
        }
    }

    return {
        fuel_charge: parseFloat(currentFuelCharge.toFixed(2)),
        overdue_charge: parseFloat(currentOverdueCharge.toFixed(2)),
        days_overdue: currentDaysOverdue,
        total_amount_to_cover: parseFloat(totalAmountToCover.toFixed(2)),
        total_paid_for_rental: parseFloat(totalPaidForRental.toFixed(2)),
        remaining_balance_required: parseFloat(remainingBalance.toFixed(2)),
        deposit_paid: parseFloat(depositPaid.toFixed(2)),
        deposit_to_refund: parseFloat(depositToRefund.toFixed(2)),
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

    const paymentsToSend = [];

    // Lógica para el reembolso automático del depósito de garantía
    // Esto se ejecuta siempre que haya un monto a reembolsar,
    // independientemente de si el formulario de pago está visible o no.
    if (calculatedSummary.value.deposit_to_refund > 0) {
        // Verificar si este reembolso ya está registrado para evitar duplicados.
        const hasRefundBeenProcessed = rentalDetails.value.payments.some(p =>
            (p.concept === 'Reembolso de Depósito' || p.concept === 'Reembolso de Depósito Extranjero') &&
            Math.abs(parseFloat(p.amount)) === calculatedSummary.value.deposit_to_refund
        );

        if (!hasRefundBeenProcessed) {
            let refundConcept = 'Reembolso de Depósito';
            if (isForeigner.value) {
                refundConcept = 'Reembolso de Depósito Extranjero'; // Concepto específico para extranjeros
            }
            // Para reembolsos automáticos, si el formulario está oculto, usamos un tipo de pago por defecto
            // Si el formulario está visible (por saldo pendiente > 0 pero también hay un reembolso),
            // se usará el tipo de pago seleccionado en el formulario.
            const refundPaymentType = shouldShowPaymentForm.value && formData.final_payment_type ? formData.final_payment_type : 'Transferencia Bancaria';

            if (!refundPaymentType) {
                showAlert('Para el reembolso automático, se necesita un tipo de pago. Por favor, selecciona uno si el formulario es visible, o se usará "Transferencia Bancaria".', 'warning');
                isLoading.value = false;
                return;
            }

            paymentsToSend.push({
                amount: -calculatedSummary.value.deposit_to_refund, // Monto negativo para reembolso
                payment_type: refundPaymentType,
                reference: isForeigner.value ? 'Reembolso Depósito Extranjero' : 'Reembolso Depósito',
                concept: refundConcept,
            });
        } else {
             console.log("FinalizeRentalModal: Reembolso de depósito ya procesado o registrado. Saltando la adición.");
        }
    }


    // Lógica para el pago/reembolso manual (SOLO si el formulario está visible)
    if (shouldShowPaymentForm.value) {
        // Si el formulario está visible y el monto del formulario no es cero
        if (formData.final_payment_amount !== 0) {
            if (!isRefundConcept.value && (formData.final_payment_amount <= 0 || !formData.final_payment_type)) {
                showAlert('Por favor, ingresa el monto y tipo de pago final.', 'warning');
                isLoading.value = false;
                return;
            }

            let amountToSend = parseFloat(formData.final_payment_amount);
            if (isRefundConcept.value && amountToSend > 0) {
                amountToSend = -amountToSend; // Asegura que el monto del reembolso sea negativo
            }

            paymentsToSend.push({
                amount: amountToSend,
                payment_type: formData.final_payment_type,
                reference: formData.final_payment_reference,
                concept: formData.final_payment_concept,
            });
        } else if (calculatedSummary.value.remaining_balance_required > 0 && formData.final_payment_concept === 'Pago final') {
            // Si el formulario está visible, hay saldo pendiente, y el concepto es "Pago final", el monto no puede ser cero.
            showAlert('Existe un saldo pendiente. Por favor, ingresa el monto a pagar.', 'warning');
            isLoading.value = false;
            return;
        } else if (isRefundConcept.value && calculatedSummary.value.deposit_to_refund > 0 && formData.final_payment_amount === 0) {
             // Si es un reembolso, hay monto a reembolsar, pero el usuario puso 0 en el form visible.
             showAlert('Debe ingresar un monto para el reembolso del depósito.', 'warning');
             isLoading.value = false;
             return;
        }
    }

    // Validación final: Si no hay pagos para enviar y *hay* un saldo pendiente > 0, es un error.
    // Esto significa que el formulario de pago debería haber estado visible y el usuario no realizó el pago.
    if (paymentsToSend.length === 0 && calculatedSummary.value.remaining_balance_required > 0) {
        showAlert('Se requiere un pago para finalizar la renta y cubrir el saldo pendiente.', 'warning');
        isLoading.value = false;
        return;
    }
    // Si no hay pagos para enviar, y el saldo es 0 o negativo (lo que implica un reembolso o que no se debe nada),
    // y el reembolso se manejó automáticamente (o no había reembolso), entonces está bien.
    // Este es el caso cuando el formulario de pago está oculto.
    // No necesitamos una validación explícita aquí, ya que el `shouldShowPaymentForm` y la lógica de reembolso automático
    // se encargan de que, si no se muestra el formulario, sea porque no se necesita pago manual.
    

    payload.final_payments = paymentsToSend;

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
            } else if (errorData.final_payments) {
                errorMessage = `Error en pagos/reembolsos: ${Object.values(errorData.final_payments).flat().join(' ')}`;
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
    formData.final_payment_concept = 'Pago final'; // Resetear el concepto de pago
    clearAlert();
    console.log('FinalizeRentalModal: Estado del modal reseteado.');
}

watch(() => props.show, async (newVal) => {
    console.log(`FinalizeRentalModal: 'show' prop cambió a ${newVal}.`);
    if (newVal) {
        if (props.rental?.id) {
            resetModalState(); // Asegura que el estado se limpie al abrir
            console.log('FinalizeRentalModal: Abriendo modal para renta con ID:', props.rental.id);
            await loadRentalDetails(props.rental.id);
        } else {
            console.warn('FinalizeRentalModal: Modal abierto, pero no se proporcionó un ID de renta válido. La carga de detalles no se realizará.');
            showAlert('No se pudo abrir la renta. No se proporcionó un ID válido.', 'danger');
            emit('error', 'ID de renta inválido.');
        }
    } else {
        resetModalState(); // Asegura que el estado se limpie al cerrar
        console.log('FinalizeRentalModal: Cerrando modal de renta.');
    }
}, { immediate: true });


const handleClose = () => {
    emit('update:show', false);
    emit('close');
    console.log('FinalizeRentalModal: handleClose ejecutado. Emitiendo cierre.');
};
</script>

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