<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { mdiArrowLeftCircle, mdiContentSaveEdit } from '@mdi/js';
import axios from 'axios';
import FormField from '@/components/FormField.vue';
import FormControl from '@/components/FormControl.vue';
import BaseButton from '@/components/BaseButton.vue';
import BaseButtons from '@/components/BaseButtons.vue';
import CardBox from '@/components/CardBox.vue';
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue';
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue';
import { useMainStore } from '@/stores/main';
import { useAuthStore } from '@/stores/authStore';
import NotificationBar from '@/components/NotificationBar.vue';

const route = useRoute();
const router = useRouter();
const mainStore = useMainStore();
const authStore = useAuthStore();

const loading = ref(false);
const initialLoading = ref(true);

const customerId = ref(null);
const originalCustomerName = ref('');

const documentTypeOptions = [ { id: 'DUI', label: 'DUI' }, { id: 'Pasaporte', label: 'Pasaporte' } ];
const customerTypeOptions = [ { id: 'Nacional', label: 'Nacional' }, { id: 'Extranjero', label: 'Extranjero' } ];
const statusOptions = [ { id: 'Activo', label: 'Activo' }, { id: 'Inactivo', label: 'Inactivo' }, { id: 'Lista Negra', label: 'Lista Negra' } ];

const form = ref({
  id: null,
  first_name: '',
  last_name: '',
  document_type: 'DUI',
  document_number: '',
  address: '',
  phone: '',
  email: '',
  customer_type: 'Nacional',
  birth_date: '',
  status: 'Activo',
  reference: '',
  notes: ''
});

const pageTitle = computed(() => originalCustomerName.value ? `Editar Cliente: ${originalCustomerName.value}` : 'Editar Cliente');
const API_URL = import.meta.env.VITE_API_URL;

// CustomerEditView.vue

const fetchCustomerData = async (id) => {
  if (!authStore.authToken || !id) {
    mainStore.notify({ color: 'danger', message: 'No se proporcionó ID de cliente o falta token.' });
    router.push({ name: 'customers' });
    return;
  }
  initialLoading.value = true;
  try {
    const config = { headers: { Authorization: `Bearer ${authStore.authToken}` } };
    const response = await axios.get(`${API_URL}customer/${id}`, config);
    
    if (response.data?.data) {
      const customerData = response.data.data;

      if (customerData.birth_date && typeof customerData.birth_date === 'string') {
        const parts = customerData.birth_date.split('-');
        
        if (parts.length === 3) {
          const day = parts[0];
          const month = parts[1];
          const year = parts[2];
          
          customerData.birth_date = `${year}-${month}-${day}`;
        }
      }

      form.value = customerData;
      originalCustomerName.value = `${form.value.first_name} ${form.value.last_name}`;

    } else {
      mainStore.notify({ color: 'danger', message: 'Cliente no encontrado.' });
      router.push({ name: 'customers' });
    }
  } catch (e) {
    console.error("Error fetching customer data:", e);
    mainStore.notify({ color: 'danger', message: 'Error cargando datos del cliente: ' + (e.response?.data?.message || e.message) });
    router.push({ name: 'customers' });
  } finally {
    initialLoading.value = false;
  }
};

onMounted(async () => {
  customerId.value = route.params.id;
  if (customerId.value) {
    await fetchCustomerData(customerId.value);
  } else {
    mainStore.notify({ color: 'danger', message: 'ID de cliente no especificado.' });
    router.push({ name: 'customers' });
  }
});

const getAuthConfigJson = () => ({
  headers: {
    'Authorization': `Bearer ${authStore.authToken}`,
    'Content-Type': 'application/json'
  }
});

const handleSubmit = async () => {
  if (!form.value.id) {
    mainStore.notify({ color: 'danger', message: 'No se puede actualizar: ID de cliente no definido.' });
    return;
  }
  loading.value = true;

  const requiredFields = {
    first_name: 'Nombres', last_name: 'Apellidos', document_type: 'Tipo de Documento', document_number: 'Número de Documento',
    address: 'Dirección', phone: 'Teléfono', email: 'Correo Electrónico', customer_type: 'Tipo de Cliente',
    birth_date: 'Fecha de Nacimiento', status: 'Estado'
  };
  for (const fieldKey in requiredFields) {
    if (!form.value[fieldKey]) {
      mainStore.notify({ color: 'danger', message: `El campo '${requiredFields[fieldKey]}' es requerido.` });
      loading.value = false; return;
    }
  }

  try {

    const payload = { ...form.value }; 
    await axios.put(`${API_URL}customer/${form.value.id}`, payload, getAuthConfigJson());
    mainStore.notify({ color: 'success', message: 'Cliente actualizado exitosamente.' });
    router.push({ name: 'customers' });
  } catch (e) {
    console.error('Error actualizando cliente:', e);
    const errorMessage = e.response?.data?.message || e.response?.data?.errors || e.message || 'Ha ocurrido un error inesperado.';
    mainStore.notify({ color: 'danger', message: errorMessage });
  } finally {
    loading.value = false;
  }
};

const cancelForm = () => {
  router.push({ name: 'customers' });
};

</script>

<template>
  <LayoutAuthenticated>
    <div v-if="mainStore.notification" class="sticky top-0 z-40 px-4 md:px-6">
      <NotificationBar v-model="mainStore.notification.show" :color="mainStore.notification.color" :icon="mainStore.notification.icon" class="mt-2">
        <span v-html="mainStore.notification.message?.replace(/\n/g, '<br>')"></span>
      </NotificationBar>
    </div>

    <SectionTitleLineWithButton :icon="mdiContentSaveEdit" :title="pageTitle" main>
      <BaseButton :to="{ name: 'customers' }" :icon="mdiArrowLeftCircle" label="Volver a la lista" color="contrast" rounded-full small />
    </SectionTitleLineWithButton>
    
    <CardBox v-if="initialLoading" class="mx-4 md:mx-0 text-center p-6">
      <p>Cargando datos del cliente...</p>
    </CardBox>

    <CardBox v-if="!initialLoading && form.id" is-form @submit.prevent="handleSubmit" class="mx-4 md:mx-0">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField label="Nombres" required><FormControl v-model="form.first_name" /></FormField>
        <FormField label="Apellidos" required><FormControl v-model="form.last_name" /></FormField>
        <FormField label="Tipo de Documento" required><FormControl v-model="form.document_type" :options="documentTypeOptions" /></FormField>
        <FormField label="Número de Documento" required>
          <FormControl v-model="form.document_number" :placeholder="form.document_type === 'DUI' ? '00000000-0' : 'Número de Pasaporte'" />
        </FormField>
        <FormField label="Correo Electrónico" required><FormControl v-model="form.email" type="email" /></FormField>
        <FormField label="Teléfono" required><FormControl v-model="form.phone" /></FormField>
        <FormField label="Fecha de Nacimiento" required><FormControl v-model="form.birth_date" type="date" /></FormField>
        <FormField label="Tipo de Cliente" required><FormControl v-model="form.customer_type" :options="customerTypeOptions" /></FormField>
        <FormField label="Dirección Completa" class="md:col-span-2" required><FormControl v-model="form.address" type="textarea" /></FormField>
        <FormField label="Referencia (Opcional)"><FormControl v-model="form.reference" /></FormField>
        <FormField label="Estado" required><FormControl v-model="form.status" :options="statusOptions" /></FormField>
        <FormField label="Notas Adicionales (Opcional)" class="md:col-span-2"><FormControl v-model="form.notes" type="textarea" /></FormField>
      </div>

      <template #footer>
        <BaseButtons>
          <BaseButton color="info" type="submit" :disabled="loading || initialLoading" :label="loading ? 'Actualizando...' : 'Actualizar Cliente'" />
          <BaseButton color="whiteDark" label="Cancelar" @click="cancelForm" outline :disabled="initialLoading" />
        </BaseButtons>
      </template>
    </CardBox>
  </LayoutAuthenticated>
</template>