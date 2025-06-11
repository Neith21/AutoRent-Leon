<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
    mdiMagnify,
    mdiFileDocumentPlus,
    mdiFormatListBulleted,
    mdiClose,
    mdiFileSend,
    mdiPlaylistEdit
} from '@mdi/js'
import axios from 'axios'

import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import CardBox from '@/components/CardBox.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import CardBoxModal from '@/components/CardBoxModal.vue'
import NotificationBar from '@/components/NotificationBar.vue'

import { useMainStore } from '@/stores/main'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const mainStore = useMainStore()
const authStore = useAuthStore()
const API_URL = import.meta.env.VITE_API_URL

const loading = ref(false)
const rentalId = ref(null)

const currentStep = ref(0)

const payments = ref([])
const selectedPaymentIds = ref([])
const rentalCustomerInfo = ref(null)

const isConfirmationModalActive = ref(false)
const invoicePreview = ref(null)

const pageTitle = 'Generar Factura'
const totalSelectedAmount = computed(() => {
    if (currentStep.value !== 2) return 0
    return payments.value
        .filter(p => selectedPaymentIds.value.includes(p.id))
        .reduce((sum, p) => sum + parseFloat(p.amount), 0)
        .toFixed(2)
})
const canGenerateManualInvoice = computed(() => selectedPaymentIds.value.length > 0)

const getAuthConfig = () => ({ headers: { Authorization: `Bearer ${authStore.authToken}` } })

const fetchPayments = async (endpoint) => {
    if (!rentalId.value) {
        mainStore.notify({ color: 'danger', message: 'Por favor, ingrese un ID de alquiler.' })
        return
    }
    loading.value = true
    payments.value = []
    rentalCustomerInfo.value = null

    try {
        const response = await axios.get(`${API_URL}invoice/${endpoint}/${rentalId.value}`, getAuthConfig())

        rentalCustomerInfo.value = `Alquiler #${rentalId.value}`

        if (response.data?.suggested_payments || response.data?.data) {
            payments.value = response.data.suggested_payments || response.data.data;
            if (payments.value.length === 0) {
                mainStore.notify({ color: 'warning', message: 'No se encontraron pagos para este alquiler.' })
                return;
            }
            currentStep.value = endpoint === 'suggested-invoice-payments' ? 1 : 2;
        }

    } catch (e) {
        console.error('Error obteniendo pagos:', e)
        const errorMsg = e.response?.data?.message || 'Ocurrió un error al buscar los pagos.'
        mainStore.notify({ color: 'danger', message: errorMsg })
        resetFlow()
    } finally {
        loading.value = false
    }
}

const getSuggestedPayments = () => fetchPayments('suggested-invoice-payments')
const getManualPayments = () => fetchPayments('rental-payments')


const prepareAndShowConfirmation = (paymentsToInvoice) => {
    if (paymentsToInvoice.length === 0) {
        mainStore.notify({ color: 'warning', message: 'No se ha seleccionado ningún pago para facturar.' });
        return;
    }

    const total = paymentsToInvoice.reduce((sum, p) => sum + parseFloat(p.amount), 0).toFixed(2);
    const referenceLines = paymentsToInvoice.map(p => `- ${p.reference || p.concept}: $${p.amount}`);

    invoicePreview.value = {
        rental_id: rentalId.value,
        payment_ids: paymentsToInvoice.map(p => p.id),
        total_amount: total,
        reference_detail: referenceLines.join('\n'),
        status: 'Emitida'
    };
    isConfirmationModalActive.value = true;
};

const handleContinueWithSelection = () => {
    prepareAndShowConfirmation(payments.value);
};

const handleManualGeneration = () => {
    const selected = payments.value.filter(p => selectedPaymentIds.value.includes(p.id));
    prepareAndShowConfirmation(selected);
}

const confirmAndCreateInvoice = async () => {
    if (!invoicePreview.value) return;
    loading.value = true;
    try {
        const payload = {
            rental_id: invoicePreview.value.rental_id,
            total_amount: invoicePreview.value.total_amount,
            reference_detail: invoicePreview.value.reference_detail,
            payment_ids: invoicePreview.value.payment_ids,
            status: invoicePreview.value.status
        };

        const response = await axios.post(`${API_URL}invoice`, payload, {
            headers: {
                'Authorization': `Bearer ${authStore.authToken}`,
                'Content-Type': 'application/json'
            }
        });

        mainStore.notify({ color: 'success', message: response.data.message || '¡Factura generada exitosamente!' });
        isConfirmationModalActive.value = false;
        resetFlow();

    } catch (e) {
        console.error('Error al crear la factura:', e);

        let errorMsg = 'Ocurrió un error al crear la factura.';
        if (e.response && e.response.data) {
            if (e.response.data.errors) {
                const errors = e.response.data.errors;
                errorMsg = Object.keys(errors).map(key => `${key}: ${errors[key][0].message}`).join('\n');
            } else if (e.response.data.message) {
                errorMsg = e.response.data.message;
            }
        }
        mainStore.notify({ color: 'danger', message: errorMsg });

    } finally {
        loading.value = false;
    }
}
const resetFlow = () => {
    rentalId.value = null
    payments.value = []
    selectedPaymentIds.value = []
    rentalCustomerInfo.value = null
    currentStep.value = 0
}

const goToList = () => {
    router.push({ name: 'invoices' });
}
</script>

<template>
    <LayoutAuthenticated>
        <!-- Notificaciones -->
        <div v-if="mainStore.notification && mainStore.notification.show" class="sticky top-0 z-[51] px-4 md:px-6">
            <NotificationBar v-model="mainStore.notification.show" :color="mainStore.notification.color"
                :icon="mainStore.notification.icon" @dismiss="mainStore.dismissNotification()" class="mt-2 shadow-lg">
                <span v-html="mainStore.notification.message?.replace(/\n/g, '<br>')"></span>
            </NotificationBar>
        </div>

        <!-- Modal de Confirmación -->
        <CardBoxModal v-model="isConfirmationModalActive" title="Confirmar Creación de Factura">
            <form @submit.prevent="confirmAndCreateInvoice">
                <div v-if="invoicePreview" class="space-y-4 p-4">
                    <p>Se creará una factura para <strong>{{ rentalCustomerInfo }}</strong>.</p>

                    <div class="my-4">
                        <label for="status" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Estado
                            Inicial de la Factura:</label>
                        <select v-model="invoicePreview.status" id="status"
                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            <option value="Emitida">Emitida (enviar por correo)</option>
                            <option value="Pagada">Pagada (no enviar por correo)</option>
                        </select>
                    </div>
                    <div>
                        <p class="font-bold">Detalle:</p>
                        <pre
                            class="whitespace-pre-wrap text-sm bg-gray-100 dark:bg-gray-700 p-2 rounded">{{ invoicePreview.reference_detail }}</pre>
                    </div>
                    <p class="text-lg font-bold">Monto Total: <span class="text-emerald-600">${{
                            invoicePreview.total_amount }}</span></p>

                    <p v-if="invoicePreview.status === 'Emitida'" class="text-blue-600 text-sm">
                        Se enviará una copia de la factura al correo del cliente.
                    </p>
                    <p v-else class="text-gray-500 text-sm">
                        La factura no se enviará por correo al cliente.
                    </p>
                </div>
                <div class="mt-6 px-4 py-3 flex justify-end space-x-2 bg-gray-50 dark:bg-gray-800 rounded-b-lg">
                    <BaseButton label="Cancelar" color="whiteDark" type="button"
                        @click="isConfirmationModalActive = false" :disabled="loading" />
                    <BaseButton :label="loading ? 'Generando...' : 'Confirmar y Crear'" color="success" type="submit"
                        :disabled="loading" />
                </div>
            </form>
        </CardBoxModal>

        <!-- Título Principal -->
        <SectionTitleLineWithButton :icon="mdiFileDocumentPlus" :title="pageTitle" main style="margin: 2rem;">
            <BaseButton :icon="mdiFormatListBulleted" label="Ver Facturas" color="contrast" rounded-full small
                @click="goToList" />
        </SectionTitleLineWithButton>

        <!-- Contenido Principal -->
        <CardBox class="mx-4 md:mx-0" style="margin: 2rem;">
            <!-- PASO 0: Formulario para buscar alquiler -->
            <div v-if="currentStep === 0" class="p-4">
                <form @submit.prevent="getSuggestedPayments">
                    <FormField label="ID del Alquiler"
                        help="Ingrese el ID del alquiler finalizado para el que desea generar una factura.">
                        <FormControl v-model="rentalId" :icon="mdiMagnify" name="rental_id" type="number"
                            placeholder="Ej: 123" required />
                    </FormField>
                    <div class="mt-4">
                        <BaseButton type="submit" color="info" label="Buscar Pagos" :disabled="loading"
                            :icon="mdiMagnify" />
                    </div>
                </form>
            </div>

            <!-- Tabla de pagos -->
            <div v-if="currentStep > 0" class="p-4">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-xl font-semibold">Pagos para {{ rentalCustomerInfo }}</h2>
                    <BaseButton label="Buscar otro alquiler" :icon="mdiClose" color="light" small @click="resetFlow" />
                </div>

                <!-- Tabla de Pagos -->
                <div class="overflow-x-auto shadow-md sm:rounded-lg">
                    <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                        <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                            <tr>
                                <th v-if="currentStep === 2" scope="col" class="p-4">
                                    <div class="flex items-center">
                                    </div>
                                </th>
                                <th scope="col" class="px-6 py-3">Concepto</th>
                                <th scope="col" class="px-6 py-3">Referencia</th>
                                <th scope="col" class="px-6 py-3">Monto</th>
                                <th scope="col" class="px-6 py-3">Método de Pago</th>
                                <th scope="col" class="px-6 py-3">Fecha</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="loading">
                                <td colspan="6" class="text-center py-4">Cargando...</td>
                            </tr>
                            <tr v-else-if="payments.length === 0">
                                <td colspan="6" class="text-center py-4">No se encontraron pagos.</td>
                            </tr>
                            <tr v-for="payment in payments" :key="payment.id"
                                class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
                                <td v-if="currentStep === 2" class="w-4 p-4">
                                    <div class="flex items-center">
                                        <input :id="'checkbox-table-' + payment.id" type="checkbox" :value="payment.id"
                                            v-model="selectedPaymentIds"
                                            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                                        <label :for="'checkbox-table-' + payment.id" class="sr-only">checkbox</label>
                                    </div>
                                </td>
                                <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">{{
                                    payment.concept }}</td>
                                <td class="px-6 py-4">{{ payment.reference || 'N/A' }}</td>
                                <td class="px-6 py-4 font-bold">${{ payment.amount }}</td>
                                <td class="px-6 py-4">{{ payment.payment_type }}</td>
                                <td class="px-6 py-4">{{ new Date(payment.payment_date).toLocaleString() }}</td>
                            </tr>
                        </tbody>
                        <tfoot v-if="currentStep === 2 && canGenerateManualInvoice">
                            <tr class="font-semibold text-gray-900 dark:text-white">
                                <th scope="row" colspan="2" class="px-6 py-3 text-base text-right">Total Seleccionado
                                </th>
                                <td class="px-6 py-3 text-base">${{ totalSelectedAmount }}</td>
                                <td colspan="2"></td>
                            </tr>
                        </tfoot>
                    </table>
                </div>

                <!-- Botones de Acción -->
                <div class="mt-6">
                    <div v-if="currentStep === 1">
                        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">Se ha cargado una selección sugerida de
                            pagos para la factura. Puede continuar con esta selección o cambiar al modo manual para
                            elegir los pagos usted mismo.</p>
                        <BaseButtons>
                            <BaseButton label="Continuar con esta selección" color="success" :icon="mdiFileSend"
                                @click="handleContinueWithSelection" />
                            <BaseButton label="Generar Factura Manualmente" color="warning" outline
                                :icon="mdiPlaylistEdit" @click="getManualPayments" />
                        </BaseButtons>
                    </div>
                    <div v-if="currentStep === 2">
                        <BaseButton label="Generar Factura con Selección" color="success" :icon="mdiFileSend"
                            :disabled="!canGenerateManualInvoice || loading" @click="handleManualGeneration" />
                        <p v-if="!canGenerateManualInvoice" class="text-xs text-gray-500 mt-2">Seleccione al menos un
                            pago para poder generar la factura.</p>
                    </div>
                </div>

            </div>
        </CardBox>
    </LayoutAuthenticated>
</template>