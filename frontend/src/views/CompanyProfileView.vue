<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useMainStore } from '@/stores/main'
import { useAuthStore } from '@/stores/authStore'
import {
  mdiDomain,
  mdiPencil,
  mdiContentSave,
  mdiClose,
  mdiUpload,
  mdiShieldAccount,
  mdiImageMultiple
} from '@mdi/js'

import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import CardBox from '@/components/CardBox.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import FormField from '@/components/FormField.vue'
import NotificationBar from '@/components/NotificationBar.vue'

const mainStore = useMainStore()
const authStore = useAuthStore()
const API_URL = import.meta.env.VITE_API_URL

const loading = ref(false)
const isEditing = ref(false)
const companyData = ref({}) 
const editData = ref({}) 
const errors = ref({})
const logoPreview = ref(null)
const logoFile = ref(null)

const getAuthConfig = () => ({ headers: { Authorization: `Bearer ${authStore.authToken}` } })

const fetchCompanyData = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_URL}company`, getAuthConfig())
    companyData.value = response.data.data
  } catch (error) {
    if (error.response?.status !== 404) {
      console.error('Error obteniendo datos de la empresa:', error)
      mainStore.notify({ color: 'danger', message: 'No se pudo cargar la información de la empresa.' })
    }
    companyData.value = {}
  } finally {
    loading.value = false
  }
}

const handleUpdateCompany = async () => {
  loading.value = true
  errors.value = {}

  const formData = new FormData()

  for (const key in editData.value) {
    if (editData.value[key] !== companyData.value[key] && editData.value[key] !== null) {
      formData.append(key, editData.value[key])
    }
  }

  if (logoFile.value) {
    formData.append('logo', logoFile.value)
  }

  if (Array.from(formData.keys()).length === 0) {
      mainStore.notify({ color: 'info', message: 'No se detectaron cambios para guardar.' });
      loading.value = false;
      isEditing.value = false;
      return;
  }

  try {
    const response = await axios.patch(`${API_URL}company`, formData, {
      headers: { 'Authorization': `Bearer ${authStore.authToken}` }
    });
    
    companyData.value = response.data.data
    isEditing.value = false
    mainStore.notify({ color: 'success', message: response.data.message })

  } catch (error) {
    console.error('Error actualizando la empresa:', error.response?.data)
    const validationErrors = error.response?.data?.errors;
    
    if (validationErrors) {
      errors.value = validationErrors;
      mainStore.notify({ color: 'danger', message: 'Por favor, corrige los errores marcados.' });
    } else {
      mainStore.notify({ color: 'danger', message: `Error: ${error.response?.data?.message || 'No se pudo actualizar.'}` });
    }
  } finally {
    loading.value = false
  }
}

const enableEditMode = () => {
  errors.value = {}
  editData.value = JSON.parse(JSON.stringify(companyData.value))
  logoFile.value = null
  logoPreview.value = null
  isEditing.value = true
}

const cancelEditMode = () => {
  errors.value = {}
  isEditing.value = false
}

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    logoFile.value = file
    logoPreview.value = URL.createObjectURL(file)
  }
}

onMounted(fetchCompanyData)

</script>

<template>
  <LayoutAuthenticated>
    <div v-if="mainStore.notification.show" class="sticky top-0 z-50 px-4 md:px-6">
      <NotificationBar v-model="mainStore.notification.show" :color="mainStore.notification.color" :icon="mainStore.notification.icon">
        <span v-html="mainStore.notification.message?.replace(/\n/g, '<br>')"></span>
      </NotificationBar>
    </div>

    <SectionTitleLineWithButton :icon="mdiDomain" title="Perfil de la Empresa" main style="margin: 2rem;">
      <BaseButton v-if="!isEditing && companyData.id" :icon="mdiPencil" label="Editar" color="info" rounded-full small @click="enableEditMode" />
      <BaseButtons v-if="isEditing">
        <BaseButton label="Guardar Cambios" :icon="mdiContentSave" color="success" :disabled="loading" @click="handleUpdateCompany" />
        <BaseButton label="Cancelar" :icon="mdiClose" color="danger" outline :disabled="loading" @click="cancelEditMode" />
      </BaseButtons>
    </SectionTitleLineWithButton>

    <div v-if="loading" class="text-center py-10">Cargando información...</div>
    
    <CardBox v-else-if="companyData.id" style="margin: 2rem;">
      <div v-if="!isEditing" class="p-6 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
          <div>
            <h3 class="text-lg font-semibold mb-2">Información General</h3>
            <p><strong>Nombre Comercial:</strong> {{ companyData.trade_name }}</p>
            <p><strong>NRC:</strong> {{ companyData.nrc }}</p>
            <p><strong>Clasificación:</strong> {{ companyData.classification }}</p>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-2">Contacto</h3>
            <p><strong>Teléfono:</strong> {{ companyData.phone }}</p>
            <p><strong>Email:</strong> {{ companyData.email }}</p>
            <p><strong>Sitio Web:</strong> <a :href="companyData.website" target="_blank" class="text-blue-500 hover:underline">{{ companyData.website }}</a></p>
          </div>
          <div class="col-span-full">
            <p><strong>Dirección:</strong> {{ companyData.address }}</p>
          </div>
        </div>

        <div v-if="companyData.logo" class="pt-4 border-t">
          <SectionTitleLineWithButton :icon="mdiImageMultiple" title="Datos de Imagen" />
          <div class="flex items-start space-x-6">
            <img :src="companyData.logo" alt="Logotipo" class="w-28 h-28 object-contain border rounded-lg bg-gray-50" />
            <div class="text-sm space-y-2">
              <p><strong>ID Público (Cloudinary):</strong> <span class="text-gray-600 dark:text-gray-400">{{ companyData.logo_public_id }}</span></p>
              <p><strong>URL Alta Calidad:</strong> <a :href="companyData.logo" target="_blank" class="text-blue-500 hover:underline break-all">{{ companyData.logo }}</a></p>
              <p><strong>URL Baja Calidad (LQIP):</strong> <a :href="companyData.logo_lqip" target="_blank" class="text-blue-500 hover:underline break-all">{{ companyData.logo_lqip }}</a></p>
            </div>
          </div>
        </div>
        
        <div v-if="authStore.isSuperuser" class="pt-4 border-t">
          <SectionTitleLineWithButton :icon="mdiShieldAccount" title="Auditoría" />
          <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2 text-sm">
            <p><strong>Creado por:</strong> {{ companyData.created_by_name || 'N/D' }}</p>
            <p><strong>Fecha Creación:</strong> {{ companyData.created_at }}</p>
            <p><strong>Modificado por:</strong> {{ companyData.modified_by_name || 'N/D' }}</p>
            <p><strong>Fecha Modificación:</strong> {{ companyData.updated_at }}</p>
          </div>
        </div>
      </div>

      <form v-else @submit.prevent="handleUpdateCompany" class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField label="Nombre Comercial">
            <FormControl v-model="editData.trade_name" :error="errors.trade_name" />
            <div v-if="errors.trade_name" class="text-sm text-red-500 mt-1">{{ errors.trade_name[0] }}</div>
          </FormField>
          <FormField label="NRC">
            <FormControl v-model="editData.nrc" :error="errors.nrc" />
            <div v-if="errors.nrc" class="text-sm text-red-500 mt-1">{{ errors.nrc[0] }}</div>
          </FormField>
          <FormField label="Clasificación">
            <FormControl v-model="editData.classification" :options="[{id: 'Pequeña', label: 'Pequeña'}, {id: 'Mediana', label: 'Mediana'}, {id: 'Gran', label: 'Gran Contribuyente'}]" :error="errors.classification" />
             <div v-if="errors.classification" class="text-sm text-red-500 mt-1">{{ errors.classification[0] }}</div>
          </FormField>
          <FormField label="Teléfono">
            <FormControl v-model="editData.phone" :error="errors.phone" />
             <div v-if="errors.phone" class="text-sm text-red-500 mt-1">{{ errors.phone[0] }}</div>
          </FormField>
          <FormField label="Email">
            <FormControl v-model="editData.email" type="email" :error="errors.email" />
             <div v-if="errors.email" class="text-sm text-red-500 mt-1">{{ errors.email[0] }}</div>
          </FormField>
          <FormField label="Sitio Web">
            <FormControl v-model="editData.website" type="url" :error="errors.website" />
             <div v-if="errors.website" class="text-sm text-red-500 mt-1">{{ errors.website[0] }}</div>
          </FormField>
        </div>
        <FormField label="Dirección" class="mt-6">
          <FormControl v-model="editData.address" type="textarea" :error="errors.address" />
           <div v-if="errors.address" class="text-sm text-red-500 mt-1">{{ errors.address[0] }}</div>
        </FormField>
        <FormField label="Logotipo" class="mt-6">
          <div class="flex items-center space-x-4">
             <img v-if="logoPreview" :src="logoPreview" class="w-24 h-24 object-contain border rounded" alt="Previsualización del nuevo logo">
             <img v-else-if="editData.logo" :src="editData.logo" class="w-24 h-24 object-contain border rounded" alt="Logo Actual">
             <div class="flex-1">
                <FormControl type="file" @change="handleFileChange" accept="image/*" />
                <p class="text-xs text-gray-500 mt-1">Sube un nuevo logo para reemplazar el anterior.</p>
             </div>
          </div>
        </FormField>
      </form>
    </CardBox>
    
    <CardBox v-else class="text-center py-10">
      <p>Aún no se ha configurado la información de la empresa.</p>
      <BaseButton class="mt-4" label="Configurar Ahora" color="info" @click="enableEditMode" />
    </CardBox>

  </LayoutAuthenticated>
</template>