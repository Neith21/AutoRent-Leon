<script setup>
import { ref, watch } from 'vue';
import axios from 'axios';
import { useMainStore } from '@/stores/main';
import BaseButton from '@/components/BaseButton.vue';
import { mdiClose } from '@mdi/js';

const mainStore = useMainStore();

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

const emit = defineEmits(['update:show', 'close']);

const payments = ref([]);
const loadingPayments = ref(false);
const paymentHistoryError = ref('');

const fetchPayments = async () => {
    if (!props.rental || !props.rental.id) {
        console.log("No rental ID available, skipping fetch.");
        payments.value = []; // Asegura que payments sea un array vacío
        return;
    }

    loadingPayments.value = true;
    paymentHistoryError.value = '';
    try {
        const token = localStorage.getItem('autorent_leon_token');
        const API_URL = import.meta.env.VITE_API_URL;
        const authConfig = { headers: { 'Authorization': `Bearer ${token}` } };

        const response = await axios.get(`${API_URL}payment/?rental_id=${props.rental.id}`, authConfig);
        
        // Verificar que response.data exista y tenga la propiedad 'data' y sea un array
        if (response.data && Array.isArray(response.data.data)) {
            payments.value = response.data.data;
        } else {
            // Si la estructura no es la esperada, asumimos que no hay pagos válidos
            payments.value = [];
            console.warn("API response for payments did not contain expected 'data' array:", response.data);
            paymentHistoryError.value = "Formato de datos de pagos inesperado del servidor.";
        }

    } catch (error) {
        console.error("Error fetching payment history:", error);
        // Mejorar el mensaje de error para el usuario
        paymentHistoryError.value = error.response?.data?.message || error.response?.data?.detail || "No se pudo cargar el historial de pagos. Inténtalo de nuevo.";
        mainStore.notify({ color: 'danger', message: 'Error al cargar historial de pagos.' });
    } finally {
        loadingPayments.value = false;
    }
};

watch(() => props.show, async (newVal) => {
    if (newVal && props.rental) {
        await fetchPayments();
    } else if (!newVal) {
        payments.value = [];
        // Restablecer el estado de error y carga al cerrar el modal
        paymentHistoryError.value = '';
        loadingPayments.value = false;
    }
}, { immediate: true });

const handleClose = () => {
    emit('update:show', false);
    emit('close');
};

const formatDate = (dateString) => {
    const date = new Date(dateString);
    if (isNaN(date)) {
        return 'Fecha inválida';
    }
    return date.toLocaleDateString('es-SV', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'America/El_Salvador' // Asegurarse de la zona horaria de El Salvador
    });
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
            Historial de Pagos de la Renta #{{ rental ? rental.id : '' }}
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

        <div class="mt-6 space-y-4 max-h-[70vh] overflow-y-auto">
          <div v-if="loadingPayments" class="text-center text-gray-600">
            Cargando pagos...
          </div>
          <div v-else-if="paymentHistoryError" class="text-center text-red-500">
            Error al cargar pagos: {{ paymentHistoryError }}
          </div>
          <div v-else>
            <div v-if="payments.length > 0" class="overflow-x-auto rounded-md border border-gray-200">
              <table class="min-w-full divide-y divide-gray-200 text-sm">
                <thead class="bg-gray-100 text-gray-500 uppercase text-xs tracking-wider">
                  <tr>
                    <th class="px-4 py-2 text-left">Fecha</th>
                    <th class="px-4 py-2 text-left">Concepto</th>
                    <th class="px-4 py-2 text-left">Monto</th>
                    <th class="px-4 py-2 text-left">Tipo de Pago</th>
                    <th class="px-4 py-2 text-left">Referencia</th>
                    <th class="px-4 py-2 text-left">Creado por</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="payment in payments" :key="payment.id" class="hover:bg-gray-50">
                    <td class="px-4 py-2 text-gray-800">{{ formatDate(payment.payment_date) }}</td>
                    <td class="px-4 py-2 text-gray-800">{{ payment.concept }}</td>
                    <td class="px-4 py-2 font-semibold text-gray-900">${{ parseFloat(payment.amount).toFixed(2) }}</td>
                    <td class="px-4 py-2 text-gray-800">{{ payment.payment_type }}</td>
                    <td class="px-4 py-2 text-gray-800">{{ payment.reference || 'N/A' }}</td>
                    <td class="px-4 py-2 text-gray-800">{{ payment.created_by_name || 'Desconocido' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center text-gray-600">No hay pagos registrados para esta renta.</div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>


<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
