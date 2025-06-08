<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { mdiArrowLeftCircle, mdiAccountPlus } from '@mdi/js';
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

const router = useRouter();
const mainStore = useMainStore();
const authStore = useAuthStore();

const loading = ref(false);

const documentTypeOptions = [ { id: 'DUI', label: 'DUI' }, { id: 'Pasaporte', label: 'Pasaporte' } ];
const customerTypeOptions = [ { id: 'Nacional', label: 'Nacional' }, { id: 'Extranjero', label: 'Extranjero' } ];
const statusOptions = [ { id: 'Activo', label: 'Activo' }, { id: 'Inactivo', label: 'Inactivo' }, { id: 'Lista Negra', label: 'Lista Negra' } ];

const form = ref({
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

const pageTitle = computed(() => 'Crear Nuevo Cliente');
const API_URL = import.meta.env.VITE_API_URL;

const getAuthConfigJson = () => ({
  headers: {
    'Authorization': `Bearer ${authStore.authToken}`,
    'Content-Type': 'application/json'
  }
});

const handleSubmit = async () => {
  loading.value = true;

  const requiredFields = {
    first_name: 'Nombres',
    last_name: 'Apellidos',
    document_type: 'Tipo de Documento',
    document_number: 'Número de Documento',
    address: 'Dirección',
    phone: 'Teléfono',
    email: 'Correo Electrónico',
    customer_type: 'Tipo de Cliente',
    birth_date: 'Fecha de Nacimiento',
    status: 'Estado'
  };

  for (const fieldKey in requiredFields) {
    if (!form.value[fieldKey]) {
      mainStore.notify({ color: 'danger', message: `El campo '${requiredFields[fieldKey]}' es requerido.` });
      loading.value = false;
      return;
    }
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(form.value.email)) {
    mainStore.notify({ color: 'danger', message: 'Por favor, ingrese un correo electrónico válido.' });
    loading.value = false; return;
  }

  const today = new Date();
  const birthDate = new Date(form.value.birth_date);
  let age = today.getFullYear() - birthDate.getFullYear();
  const m = today.getMonth() - birthDate.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  if (age < 18) {
    mainStore.notify({ color: 'danger', message: 'El cliente debe ser mayor de 18 años.' });
    loading.value = false; return;
  }

  if (form.value.document_type === 'DUI' && !/^\d{8}-\d{1}$/.test(form.value.document_number)) {
      mainStore.notify({ color: 'danger', message: 'El formato del DUI debe ser 00000000-0.' });
      loading.value = false; return;
  }
  if (form.value.document_type === 'Pasaporte' && !/^[A-Z0-9]{6,15}$/.test(form.value.document_number)) {
      mainStore.notify({ color: 'danger', message: 'El pasaporte debe contener entre 6 y 15 caracteres alfanuméricos.' });
      loading.value = false; return;
  }

  try {
    const payload = { ...form.value };
    await axios.post(`${API_URL}customer`, payload, getAuthConfigJson());
    mainStore.notify({ color: 'success', message: 'Cliente creado exitosamente.' });
    router.push({ name: 'customers' });
  } catch (e) {
    console.error('Error creando cliente:', e);
    const errorMessage = e.response?.data?.message || e.response?.data?.errors || e.message || 'Ha ocurrido un error inesperado.';
    mainStore.notify({
      color: 'danger',
      message: errorMessage,
    });
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

    <SectionTitleLineWithButton :icon="mdiAccountPlus" :title="pageTitle" main>
      <BaseButton :to="{ name: 'customers' }" :icon="mdiArrowLeftCircle" label="Volver a la lista" color="contrast" rounded-full small />
    </SectionTitleLineWithButton>
    
    <CardBox is-form @submit.prevent="handleSubmit" class="mx-4 md:mx-0">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        <FormField label="Nombres" required><FormControl v-model="form.first_name" placeholder="Nombres del cliente" /></FormField>
        <FormField label="Apellidos" required><FormControl v-model="form.last_name" placeholder="Apellidos del cliente" /></FormField>
        
        <FormField label="Tipo de Documento" required><FormControl v-model="form.document_type" :options="documentTypeOptions" /></FormField>
        <FormField label="Número de Documento" required>
            <FormControl v-model="form.document_number" :placeholder="form.document_type === 'DUI' ? '00000000-0' : 'Número de Pasaporte'" />
        </FormField>
        
        <FormField label="Correo Electrónico" required><FormControl v-model="form.email" type="email" placeholder="cliente@email.com" /></FormField>
        <FormField label="Teléfono" required><FormControl v-model="form.phone" placeholder="Ej: 7777-7777" /></FormField>
        
        <FormField label="Fecha de Nacimiento" required help="El cliente debe ser mayor de 18 años.">
            <FormControl v-model="form.birth_date" type="date" />
        </FormField>
        <FormField label="Tipo de Cliente" required><FormControl v-model="form.customer_type" :options="customerTypeOptions" /></FormField>
        
        <FormField label="Dirección Completa" class="md:col-span-2" required>
            <FormControl v-model="form.address" type="textarea" placeholder="Escriba la dirección completa del cliente..." />
        </FormField>
        
        <FormField label="Referencia (Opcional)"><FormControl v-model="form.reference" placeholder="Contacto de referencia" /></FormField>
        <FormField label="Estado" required><FormControl v-model="form.status" :options="statusOptions" /></FormField>
        
        <FormField label="Notas Adicionales (Opcional)" class="md:col-span-2">
            <FormControl v-model="form.notes" type="textarea" placeholder="Cualquier nota relevante sobre el cliente..." />
        </FormField>

      </div>

      <template #footer>
        <BaseButtons>
          <BaseButton color="info" type="submit" :disabled="loading" :label="loading ? 'Creando...' : 'Crear Cliente'" />
          <BaseButton color="whiteDark" label="Cancelar" @click="cancelForm" outline />
        </BaseButtons>
      </template>
    </CardBox>
  </LayoutAuthenticated>
</template>