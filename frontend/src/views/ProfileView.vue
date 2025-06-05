<script setup>
import { reactive, ref, onMounted, watch, computed } from 'vue'
import { useMainStore } from '@/stores/main'
import { mdiAccount, mdiAsterisk, mdiFormTextboxPassword, mdiPencil, mdiCancel, mdiContentSave } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import BaseDivider from '@/components/BaseDivider.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import FormFilePicker from '@/components/FormFilePicker.vue'
import BaseButton from '@/components/BaseButton.vue'
import UserCard from '@/components/UserCard.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'

import axios from 'axios'
import { jwtDecode } from "jwt-decode";

const mainStore = useMainStore()

const token = localStorage.getItem('autorent_leon_token')

const userId = ref('');
const userEmail = ref('');
const user = ref(null);

// --- Estado de Edición ---
const isProfileEditing = ref(false);
const isPasswordEditing = ref(false);

// --- Formularios Reactivos ---
const profileForm = reactive({
  name: '',
  last_name: '',
  email: '', // Se muestra pero no se edita
});

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
});

// --- Almacenamiento de datos originales para "Cancelar" ---
const originalProfileData = reactive({
  name: '',
  last_name: '',
});

// --- Mensajes de Error/Éxito del Backend ---
const backendProfileError = ref(''); // Para errores generales del formulario de perfil
const backendFieldErrors = ref({}); // Para errores específicos de campos del perfil
const backendPasswordError = ref('');
const backendImageError = ref('');
const successProfileMessage = ref('');
const successPasswordMessage = ref('');
const successImageMessage = ref('');


// Refs for image upload
const avatarFile = ref(null);
const showSubmitImageButton = ref(false);
const imageUploading = ref(false);
const avatarPreview = ref(null); // Para previsualización de imagen

if (token) {
  try {
    const decoded = jwtDecode(token);
    userId.value = decoded.id || '';
    userEmail.value = decoded.email || '';
  } catch (error) {
  }
}

const getAuthConfig = (contentType = 'application/json') => {
  return {
    headers: {
      'Content-Type': contentType,
      'Authorization': `Bearer ${token}`
    }
  };
}

const fetchUser = async () => {
  if (!token || !userId.value) {
    backendProfileError.value = "No se pudo cargar la información del perfil. Intenta recargar la página.";
    return;
  }
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_URL}user/${userId.value}`, getAuthConfig());
    user.value = response.data?.data || null;

    if (user.value) {
      profileForm.name = user.value.first_name || '';
      profileForm.last_name = user.value.last_name || '';
      profileForm.email = user.value.email || '';
      
      originalProfileData.name = user.value.first_name || '';
      originalProfileData.last_name = user.value.last_name || '';

      let avatarUrl = user.value.user_image;
      if (avatarUrl) {
        avatarUrl = `${avatarUrl}?t=${new Date().getTime()}`;
      } else {
        avatarUrl = mainStore.userAvatar;
      }
      
      avatarPreview.value = avatarUrl;
      mainStore.setUser({
        name: user.value.first_name,
        email: user.value.email,
        avatar: avatarUrl,
      });
    } else {
      backendProfileError.value = "No se encontró información del perfil.";
    }
  } catch (e) {
    backendProfileError.value = `Error al cargar el perfil: ${e.response?.data?.message || e.message || 'Error desconocido'}`;
  }
}

onMounted(() => {
  fetchUser();
});

const toggleProfileEdit = () => {
  isProfileEditing.value = !isProfileEditing.value;
  backendProfileError.value = '';
  backendFieldErrors.value = {}; 
  successProfileMessage.value = '';
  if (!isProfileEditing.value) {
    profileForm.name = originalProfileData.name;
    profileForm.last_name = originalProfileData.last_name;
  }
};

const cancelProfileEdit = () => {
  profileForm.name = originalProfileData.name;
  profileForm.last_name = originalProfileData.last_name;
  isProfileEditing.value = false;
  backendProfileError.value = '';
  backendFieldErrors.value = {}; 
  successProfileMessage.value = '';
};

const submitProfile = async () => {
  if (!isProfileEditing.value) return;
  backendProfileError.value = '';
  backendFieldErrors.value = {}; 
  successProfileMessage.value = '';

  try {
    const payload = {
      first_name: profileForm.name,
      last_name: profileForm.last_name,
    };
    const response = await axios.put(
      `${import.meta.env.VITE_API_URL}user/${userId.value}`,
      payload,
      getAuthConfig()
    );

    if (response.data.status === "ok") {
      successProfileMessage.value = response.data.message || 'Perfil actualizado exitosamente.';
      await fetchUser(); 
      isProfileEditing.value = false; 
    } else {
      backendProfileError.value = response.data.message || 'Error desconocido al actualizar el perfil.';
      if (response.data.errors && typeof response.data.errors === 'object') {
        backendFieldErrors.value = response.data.errors;
      }
    }
  } catch (error) {
    if (error.response && error.response.data) {
      if (error.response.data.errors && typeof error.response.data.errors === 'object') {
        backendFieldErrors.value = error.response.data.errors;
        backendProfileError.value = error.response.data.message || "Por favor, corrige los errores indicados.";
      } else if (error.response.data.message) {
        backendProfileError.value = error.response.data.message;
      } else {
        backendProfileError.value = 'Ocurrió un error al actualizar el perfil.';
      }
    } else {
      backendProfileError.value = 'Ocurrió un error de red al actualizar el perfil. Verifica tu conexión.';
    }
  }
};


const togglePasswordEdit = () => {
  isPasswordEditing.value = !isPasswordEditing.value;
  backendPasswordError.value = '';
  successPasswordMessage.value = '';
  if (!isPasswordEditing.value) {
    passwordForm.current_password = '';
    passwordForm.new_password = '';
    passwordForm.confirm_password = '';
  }
};

const cancelPasswordEdit = () => {
  passwordForm.current_password = '';
  passwordForm.new_password = '';
  passwordForm.confirm_password = '';
  isPasswordEditing.value = false;
  backendPasswordError.value = '';
  successPasswordMessage.value = '';
};

const submitPass = async () => {
  if (!isPasswordEditing.value) return;
  backendPasswordError.value = '';
  successPasswordMessage.value = '';

  if (passwordForm.new_password !== passwordForm.confirm_password) {
    backendPasswordError.value = 'La nueva contraseña y la confirmación no coinciden.';
    return;
  }
  if (!passwordForm.current_password || !passwordForm.new_password) {
    backendPasswordError.value = 'Todos los campos de contraseña son requeridos.';
    return;
  }

  try {
    const payload = {
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
      confirm_password: passwordForm.confirm_password,
    };
    const response = await axios.post(
        `${import.meta.env.VITE_API_URL}user/edit/password`,
        payload, 
        getAuthConfig()
    );

    if (response.data.status === "ok") {
      successPasswordMessage.value = response.data.message || 'Contraseña actualizada exitosamente.';
      passwordForm.current_password = '';
      passwordForm.new_password = '';
      passwordForm.confirm_password = '';
      isPasswordEditing.value = false;
    } else {
      backendPasswordError.value = response.data.message || 'Error desconocido al cambiar la contraseña.';
    }
  } catch (error) {
    backendPasswordError.value = error.response?.data?.message || 'Ocurrió un error al cambiar la contraseña.';
  }
};

watch(avatarFile, (newFile) => {
  if (newFile) {
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    const maxSize = 500 * 1024; 
    backendImageError.value = ''; 
    successImageMessage.value = ''; 

    if (!validTypes.includes(newFile.type)) {
      backendImageError.value = 'Por favor, selecciona un archivo PNG o JPG.';
      avatarFile.value = null; 
      showSubmitImageButton.value = false;
      avatarPreview.value = user.value?.user_image ? `${user.value.user_image}?t=${new Date().getTime()}` : mainStore.userAvatar;
      return;
    }

    if (newFile.size > maxSize) {
      backendImageError.value = 'El archivo es demasiado grande. El tamaño máximo es 500KB.';
      avatarFile.value = null; 
      showSubmitImageButton.value = false;
      avatarPreview.value = user.value?.user_image ? `${user.value.user_image}?t=${new Date().getTime()}` : mainStore.userAvatar;
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      avatarPreview.value = e.target.result; 
    };
    reader.readAsDataURL(newFile);
    showSubmitImageButton.value = true;
  } else { 
    showSubmitImageButton.value = false;
    if (user.value && user.value.user_image) {
        avatarPreview.value = `${user.value.user_image}?t=${new Date().getTime()}`;
    } else if (mainStore.userAvatar) { 
        avatarPreview.value = mainStore.userAvatar;
    } else {
        avatarPreview.value = null; 
    }
  }
});

const submitImage = async () => {
  if (!avatarFile.value) {
    backendImageError.value = 'Por favor, selecciona una imagen primero.';
    return;
  }
  backendImageError.value = '';
  successImageMessage.value = '';
  imageUploading.value = true;
  showSubmitImageButton.value = false;

  const formData = new FormData();
  formData.append('user_image', avatarFile.value);
  formData.append('id', userId.value);

  try {
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL}user/edit/image`,
      formData,
      getAuthConfig('multipart/form-data')
    );

    if (response.status === 200 || response.status === 201) {
      const successMsg = response.data?.message ||'Foto de perfil actualizada exitosamente.';
      successImageMessage.value = successMsg;
      alert(successMsg);
      await fetchUser(); 
      avatarFile.value = null; 
      window.location.reload();
    } else {
      backendImageError.value = `Error al actualizar la foto: ${response.data?.message || 'Respuesta inesperada'}`;
      showSubmitImageButton.value = true; 
    }
  } catch (error) {
    backendImageError.value = error.response?.data?.message || "Ocurrió un error al subir la imagen.";
    showSubmitImageButton.value = true;
  } finally {
    imageUploading.value = false;
  }
};

const userAvatarComputed = computed(() => {
  if (avatarFile.value && avatarPreview.value && avatarPreview.value.startsWith('data:image')) {
    return avatarPreview.value;
  }
  return avatarPreview.value; 
});

</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <UserCard class="mb-6" :user-name="profileForm.name" :user-email="profileForm.email" :avatar="userAvatarComputed" />

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="flex flex-col gap-6">
          <CardBox is-form @submit.prevent="submitImage" class="flex flex-col items-center text-center">
            <h2 class="text-xl font-semibold mb-4">Actualizar Foto de Perfil</h2>
            
            <div class="mb-4">
              <img :src="avatarPreview" alt="Previsualización de Avatar" class="rounded-full h-32 w-32 object-cover mx-auto border-2 border-gray-300" v-if="avatarPreview">
              <div v-else class="rounded-full h-32 w-32 bg-gray-200 flex items-center justify-center mx-auto border-2 border-gray-300 text-gray-500">
                Sin foto
              </div>
            </div>

            <div v-if="backendImageError" class="text-red-500 text-sm mb-2 p-2 bg-red-100 border border-red-300 rounded">{{ backendImageError }}</div>
            <div v-if="successImageMessage" class="text-green-500 text-sm mb-2 p-2 bg-green-100 border border-green-300 rounded">{{ successImageMessage }}</div>

            <FormField help="Selecciona PNG o JPG (Max 500kb)." class="w-full max-w-xs mb-4">
              <FormFilePicker v-model="avatarFile" label="Seleccionar archivo" accept=".png, .jpg, .jpeg" is-rounded />
            </FormField>
            
            <BaseButton v-if="showSubmitImageButton && !imageUploading" color="info" type="submit" label="Subir Foto" :icon="mdiContentSave" class="mt-2" small />
            <BaseButton v-if="imageUploading" color="info" label="Subiendo..." disabled class="mt-2" small>
              <span class="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full" role="status" aria-label="loading"></span>
            </BaseButton>
          </CardBox>

          <CardBox is-form @submit.prevent="submitProfile">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-semibold">Datos Personales</h2>
              <BaseButton 
                v-if="!isProfileEditing" 
                color="contrast" 
                small 
                label="Editar Perfil" 
                :icon="mdiPencil" 
                @click="toggleProfileEdit" 
              />
            </div>

            <div v-if="backendProfileError && !Object.keys(backendFieldErrors).length" class="text-red-500 text-sm mb-3 p-2 bg-red-100 border border-red-300 rounded">
              {{ backendProfileError }}
            </div>
             <div v-if="backendProfileError && Object.keys(backendFieldErrors).length" class="text-orange-600 text-sm mb-3 p-2 bg-orange-100 border border-orange-300 rounded">
              {{ backendProfileError }} </div>
            <div v-if="successProfileMessage" class="text-green-500 text-sm mb-3 p-2 bg-green-100 border border-green-300 rounded">
              {{ successProfileMessage }}
            </div>
            
            <FormField label="Nombre" :help="isProfileEditing ? 'Ingresa tu nombre' : ''">
              <FormControl 
                v-model="profileForm.name" 
                :icon="mdiAccount" 
                name="name" 
                required 
                autocomplete="given-name" 
                :disabled="!isProfileEditing" 
              />
              <div v-if="backendFieldErrors.first_name" class="text-red-500 text-sm mt-1">
                {{ backendFieldErrors.first_name }}
              </div>
            </FormField>

            <FormField label="Apellido" :help="isProfileEditing ? 'Ingresa tu apellido' : ''">
              <FormControl 
                v-model="profileForm.last_name" 
                :icon="mdiAccount" 
                name="last_name" 
                autocomplete="family-name" 
                :disabled="!isProfileEditing" 
              />
              <div v-if="backendFieldErrors.last_name" class="text-red-500 text-sm mt-1">
                {{ backendFieldErrors.last_name }}
              </div>
            </FormField>

            <FormField label="Correo Electrónico" help="El correo electrónico no se puede modificar.">
              <FormControl v-model="profileForm.email" name="email" required autocomplete="email" readonly disabled />
            </FormField>

            <div v-if="isProfileEditing" class="flex justify-end space-x-2 mt-4">
                <BaseButton color="success" type="submit" label="Guardar Cambios" :icon="mdiContentSave" small />
                <BaseButton color="danger" outline label="Cancelar" :icon="mdiCancel" @click="cancelProfileEdit" small />
            </div>
          </CardBox>
        </div>

        <div>
          <CardBox is-form @submit.prevent="submitPass">
             <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-semibold">Cambiar Contraseña</h2>
              <BaseButton 
                v-if="!isPasswordEditing" 
                color="contrast" 
                small 
                label="Editar Contraseña" 
                :icon="mdiPencil" 
                @click="togglePasswordEdit" 
              />
            </div>

            <div v-if="backendPasswordError" class="text-red-500 text-sm mb-3 p-2 bg-red-100 border border-red-300 rounded">{{ backendPasswordError }}</div>
            <div v-if="successPasswordMessage" class="text-green-500 text-sm mb-3 p-2 bg-green-100 border border-green-300 rounded">{{ successPasswordMessage }}</div>

            <FormField label="Contraseña Actual" help="Requerida para cambiar tu contraseña.">
              <FormControl v-model="passwordForm.current_password" :icon="mdiAsterisk" name="current_password" type="password" required autocomplete="current-password" :disabled="!isPasswordEditing" />
            </FormField>

            <BaseDivider />

            <FormField label="Nueva Contraseña" help="Mínimo 8 caracteres, con mayúsculas, minúsculas, números y símbolos.">
              <FormControl v-model="passwordForm.new_password" :icon="mdiFormTextboxPassword" name="new_password" type="password" required autocomplete="new-password" :disabled="!isPasswordEditing" />
            </FormField>

            <FormField label="Confirmar Nueva Contraseña" help="Vuelve a ingresar tu nueva contraseña.">
              <FormControl v-model="passwordForm.confirm_password" :icon="mdiFormTextboxPassword" name="confirm_password" type="password" required autocomplete="new-password" :disabled="!isPasswordEditing" />
            </FormField>

            <div v-if="isPasswordEditing" class="flex justify-end space-x-2 mt-4">
                <BaseButton type="submit" color="success" label="Guardar Contraseña" :icon="mdiContentSave" small />
                <BaseButton color="danger" outline label="Cancelar" :icon="mdiCancel" @click="cancelPasswordEdit" small />
            </div>
          </CardBox>
        </div>
      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<style scoped>
.text-red-500 {
  color: #ef4444; /* Tailwind red-500 */
}
.bg-red-100 {
  background-color: #fee2e2; /* Tailwind red-100 */
}
.border-red-300 {
  border-color: #fca5a5; /* Tailwind red-300 */
}

.text-green-500 {
  color: #22c55e; /* Tailwind green-500 */
}
.bg-green-100 {
  background-color: #dcfce7; /* Tailwind green-100 */
}
.border-green-300 {
  border-color: #86efac; /* Tailwind green-300 */
}

.animate-spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>