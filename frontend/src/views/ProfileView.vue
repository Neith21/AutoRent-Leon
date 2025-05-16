<script setup>
import { reactive, ref, onMounted, watch } from 'vue'
import { useMainStore } from '@/stores/main'
import { mdiAccount, mdiAsterisk, mdiFormTextboxPassword } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import BaseDivider from '@/components/BaseDivider.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import FormFilePicker from '@/components/FormFilePicker.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import UserCard from '@/components/UserCard.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'

import axios from 'axios'
import { jwtDecode } from "jwt-decode";

const mainStore = useMainStore()

const token = localStorage.getItem('autorent_leon_token')

const userId = ref('');
const userEmail = ref('');
const user = ref(null);

const profileForm = reactive({
  name: '',
  last_name: '',
  email: '',
})

// Refs for image upload
const avatarFile = ref(null);
const showSubmitImageButton = ref(false);
const imageUploading = ref(false);

if (token) {
  try {
    const decoded = jwtDecode(token);
    userId.value = decoded.id || '';
    userEmail.value = decoded.email || '';
  } catch (error) {
    console.error('Error decoding JWT token:', error);
  }
}

const getAuthConfig = () => {
  return {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  };
}

const getAuthFormConfig = () => {
  return {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  };
}


// Cargar user
const fetchUser = async () => {
  if (!token || !userId.value) {
    console.warn('Token or User ID is missing. Cannot fetch user.');
    return;
  }
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_URL}user/${userId.value}`, getAuthConfig());
    user.value = response.data?.data || null;

    if (user.value) {
      profileForm.name = user.value.first_name || '';
      profileForm.last_name = user.value.last_name || '';
      profileForm.email = user.value.email || '';
      profileForm.userAvatar = user.value.user_image
      mainStore.setUser({
        name: user.value.first_name,
        email: user.value.email,
        avatar: user.value.avatar_url || mainStore.userAvatar,
      });
    }
  } catch (e) {
    console.error('Error obteniendo usuario:', e);
  }
}

onMounted(() => {
  fetchUser();
});

// Para ver errores y cosas así
watch(avatarFile, (newFile) => {
  if (newFile) {
    const validTypes = ['image/png', 'image/jpeg'];
    const maxSize = 500 * 1024; // 500KB

    if (!validTypes.includes(newFile.type)) {
      alert('Por favor, selecciona un archivo PNG o JPG.');
      avatarFile.value = null; // Resetea file input
      showSubmitImageButton.value = false;
      return;
    }

    if (newFile.size > maxSize) {
      alert('El archivo es demasiado grande. El tamaño máximo es 500KB.');
      avatarFile.value = null; // Resetea file input
      showSubmitImageButton.value = false;
      return;
    }
    showSubmitImageButton.value = true;
  } else {
    showSubmitImageButton.value = false;
  }
});

const submitImage = async () => {
  if (!avatarFile.value) {
    alert('Por favor, selecciona una imagen primero.');
    return;
  }

  imageUploading.value = true;
  showSubmitImageButton.value = false; // Hide button durante no se cargue algo

  const formData = new FormData();
  formData.append('user_image', avatarFile.value);
  formData.append('id', userId.value);

  try {
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL}user/edit/image`,
      formData,
      getAuthFormConfig()
    );

    if (response.status === 200 || response.status === 201) {
      alert('Foto de perfil actualizada exitosamente.');
      window.location.reload();
    } else {
      alert(`Error al actualizar la foto: ${response.data?.message || 'Respuesta inesperada del servidor'}`);
    }
  } catch (error) {
    console.error('Error subiendo imagen:', error);
    let errorMessage = "Ocurrió un error inesperado al subir la imagen.";
    if (error.response && error.response.data && error.response.data.message) {
      errorMessage = error.response.data.message;
    } else if (error.message) {
      errorMessage = error.message;
    }
    alert(errorMessage);
  } finally {
    imageUploading.value = false;
  }
};

const submitProfile = async () => {
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
    if (response.status === 200) {
      alert('Perfil actualizado exitosamente.');
      await fetchUser();
    } else {
      alert(`Error al actualizar el perfil: ${response.data?.message || 'Error desconocido'}`);
    }
  } catch (error) {
    console.error('Error actualizando perfil:', error);
    alert(`Ocurrió un error al actualizar el perfil: ${error.response?.data?.message || error.message}`);
  }
}

const passwordForm = reactive({
  password_current: '',
  password: '',
  password_confirmation: '',
})

const submitPass = async () => {
  if (passwordForm.password !== passwordForm.password_confirmation) {
    alert('Las contraseñas nuevas no coinciden.');
    return;
  }
  if (!passwordForm.password_current || !passwordForm.password) {
    alert('Todos los campos de contraseña son requeridos.');
    return;
  }

  try {
    const payload = {
      id: userId.value,
      email: userEmail.value,
      current_password: passwordForm.password_current,
      new_password: passwordForm.password,
      confirm_password: passwordForm.password_confirmation,
    };
    // Example endpoint, adjust to your API
    const response = await axios.post(`${import.meta.env.VITE_API_URL}user/edit/password`, payload, getAuthConfig());

    if (response.status === 200) {
      alert('Contraseña actualizada exitosamente.');
      passwordForm.password_current = '';
      passwordForm.password = '';
      passwordForm.password_confirmation = '';
    } else {
      alert(`Error al cambiar la contraseña: ${response.data?.message || 'Error desconocido'}`);
    }
  } catch (error) {
    console.error('Error cambiando contraseña:', error);
    alert(`Ocurrió un error al cambiar la contraseña: ${error.response?.data?.message || error.message}`);
  }
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <UserCard class="mb-6" :user-name="profileForm.name" :user-email="profileForm.email" />

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="flex flex-col gap-6">
          <CardBox is-form @submit.prevent="submitImage" class="flex flex-col items-center text-center">
            <h2 class="text-xl font-semibold mb-4">Actualizar Foto de Perfil</h2>
            <FormField help="Selecciona PNG o JPG (Max 500kb)." class="w-full max-w-xs mb-4">
              <FormFilePicker v-model="avatarFile" label="Seleccionar archivo" accept="image/png, image/jpeg"
                is-rounded />
            </FormField>
            <BaseButton v-if="showSubmitImageButton && !imageUploading" color="info" type="submit"
              label="Actualizar Foto" class="mt-2" />
            <BaseButton v-if="imageUploading" color="info" label="Subiendo..." disabled class="mt-2">
              <span class="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full"
                role="status" aria-label="loading"></span>
            </BaseButton>
          </CardBox>

          <CardBox is-form @submit.prevent="submitProfile">
            <FormField label="Nombre">
              <FormControl v-model="profileForm.name" :icon="mdiAccount" name="name" required autocomplete="name" />
            </FormField>

            <FormField label="Apellido">
              <FormControl v-model="profileForm.last_name" :icon="mdiAccount" name="last_name" required
                autocomplete="last_name" />
            </FormField>

            <FormField label="E-mail" help="El correo electrónico no se puede modificar desde aquí.">
              <FormControl v-model="profileForm.email" name="email" required autocomplete="email" readonly disabled />
            </FormField>

            <template #footer>
              <BaseButtons>
                <BaseButton color="info" type="submit" label="Guardar Cambios" />
              </BaseButtons>
            </template>
          </CardBox>
        </div>

        <div>
          <CardBox is-form @submit.prevent="submitPass">
            <FormField label="Contraseña Actual" help="Requerida. Tu contraseña actual.">
              <FormControl v-model="passwordForm.password_current" :icon="mdiAsterisk" name="password_current"
                type="password" required autocomplete="current-password" />
            </FormField>

            <BaseDivider />

            <FormField label="Nueva Contraseña" help="Requerida. Tu nueva contraseña.">
              <FormControl v-model="passwordForm.password" :icon="mdiFormTextboxPassword" name="password"
                type="password" required autocomplete="new-password" />
            </FormField>

            <FormField label="Confirmar Nueva Contraseña" help="Requerida. Ingresa la nueva contraseña otra vez.">
              <FormControl v-model="passwordForm.password_confirmation" :icon="mdiFormTextboxPassword"
                name="password_confirmation" type="password" required autocomplete="new-password" />
            </FormField>

            <template #footer>
              <BaseButtons>
                <BaseButton type="submit" color="info" label="Cambiar Contraseña" />
              </BaseButtons>
            </template>
          </CardBox>
        </div>
      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>