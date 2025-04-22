<script setup>
import { computed, ref } from 'vue'
import { useMainStore } from '@/stores/main'
import { mdiCheckDecagram } from '@mdi/js'
import BaseLevel from '@/components/BaseLevel.vue'
import UserAvatarCurrentUser from '@/components/UserAvatarCurrentUser.vue'
import CardBox from '@/components/CardBox.vue'
import FormCheckRadio from '@/components/FormCheckRadio.vue'
import PillTag from '@/components/PillTag.vue'

const mainStore = useMainStore()

const userName = computed(() => mainStore.userName)

const userSwitchVal = ref(false)

// Corregimos la URL del panel de administración
const adminUrl = import.meta.env.VITE_ADMIN_DASHBOARD

// Convertimos el valor a booleano explícitamente
const isSuperuser = ref(localStorage.getItem('autorent_leon_is_superuser') === 'true')

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
          <a 
            v-if="isSuperuser" 
            :href="adminUrl"
            target="_blank"
            class="mt-3 inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-xl shadow-md transition duration-150 ease-in-out"
          >
            Ir al Panel de Administración
          </a>
        </div>
      </div>
    </BaseLevel>
  </CardBox>
</template>