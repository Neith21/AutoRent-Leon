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

const adminUrl = import.meta.env.VITE_ADMIN_DASHBOARD

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
      <UserAvatarCurrentUser class="
      rounded-full
      bg-gray-100 dark:bg-slate-800
      w-12 h-12           /* móvil: 3rem x 3rem */
      sm:w-16 sm:h-16     /* ≥640px: 4rem x 4rem */
      md:w-24 md:h-24     /* ≥768px: 6rem x 6rem */
      lg:w-32 lg:h-32     /* ≥1024px: 8rem x 8rem */
      xl:w-40 xl:h-40     /* ≥1280px: 10rem x 10rem */
      " />
      <div class="space-y-3 text-center md:text-left lg:mx-12">
        <h1 class="text-2xl">
          ¡Hola, <b>{{ userName }}</b>!
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