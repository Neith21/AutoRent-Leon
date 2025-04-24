<script setup>
import { computed, ref } from 'vue'
import { useMainStore } from '@/stores/main'
import { mdiCheckDecagram } from '@mdi/js'
import BaseLevel from '@/components/BaseLevel.vue'
import UserAvatarCurrentUser from '@/components/UserAvatarCurrentUser.vue'
import CardBox from '@/components/CardBox.vue'
import FormCheckRadio from '@/components/FormCheckRadio.vue'
import PillTag from '@/components/PillTag.vue'
import { jwtDecode } from "jwt-decode";

const mainStore = useMainStore()

const userName = computed(() => mainStore.userName)

const userSwitchVal = ref(false)

// Corregimos la URL del panel de administración
const adminUrl = import.meta.env.VITE_ADMIN_DASHBOARD

// Convertimos el valor a booleano explícitamente
const isSuperuser = ref('');

const token = localStorage.getItem('autorent_leon_token');

if (token) {
  try {
    const decoded = jwtDecode(token);
    isSuperuser.value = decoded.is_superuser || '';
  } catch (error) {
    console.error('Error decoding JWT token:', error);
  }
}

</script>

<template>
  <CardBox>
    <BaseLevel type="justify-around lg:justify-center">
      <UserAvatarCurrentUser class="lg:mx-12" />
      <div class="space-y-3 text-center md:text-left lg:mx-12">
        <h1 class="text-2xl">
          Howdy, <b>{{ userName }}</b>!
        </h1>
        <div class="flex justify-center md:block">
          <PillTag label="Verified" color="info" :icon="mdiCheckDecagram" />

          <!-- Solo mostramos el botón si el usuario es superusuario -->
          <a v-if="isSuperuser" :href="adminUrl" target="_blank"
            class="mt-3 ml-2 inline-flex items-center px-4 py-1 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-full shadow transition duration-150 ease-in-out">
            Ir al Panel de Administración
          </a>
        </div>
      </div>
    </BaseLevel>
  </CardBox>
</template>