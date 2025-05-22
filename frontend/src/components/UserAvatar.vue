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

const computedSrc = computed(() =>
  props.src ?? user.value.user_image
)

onMounted(async () => {
  if (!token) return
  if (!props.src) { 
    try {
      const { id } = jwtDecode(token)
      const config = {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      }
      const { data } = await axios.get(
        `${import.meta.env.VITE_API_URL}user/${id}`,
        config
      )
      user.value = data?.data || {}
    } catch (error) {
      console.error('Error fetching user for avatar fallback:', error)
    }
  }
})
</script>

<template>
  <div class="overflow-hidden">
    <img
      :src="computedSrc"
      :alt="username"
      class="rounded-full block w-full h-full object-cover"
      />
    <slot />
  </div>
</template>