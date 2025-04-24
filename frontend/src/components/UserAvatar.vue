<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { jwtDecode } from "jwt-decode";

const user = ref({})
const token = localStorage.getItem('autorent_leon_token')

const props = defineProps({
  username: { type: String, required: true },
  src: { type: String, default: null }
})

const src = computed(() =>
  props.src ?? user.value.user_image
)

onMounted(async () => {
  if (!token) return
  try {
    const { id } = jwtDecode(token)
    const config = {
      headers: {
        'Content-Type':  'application/json',
        'Authorization': `Bearer ${token}`
      }
    }
    const { data } = await axios.get(
      `${import.meta.env.VITE_API_URL}user/${id}`,
      config
    )
    user.value = data?.data || {}
  } catch (error) {
    console.error('Error fetching user:', error)
  }
})
</script>

<template>
  <div>
    <img
      :src="src"
      :alt="username"
      class="rounded-full block h-auto w-full max-w-full 
             bg-gray-100 dark:bg-slate-800"
    />
    <slot />
  </div>
</template>
