<script setup>
import { useMainStore } from '@/stores/main'
import UserAvatar from '@/components/UserAvatar.vue'

const mainStore = useMainStore()
</script>

<template>
  <UserAvatar :username="mainStore.userName" :avatar="mainStore.userAvatar" class="rounded-full">
    <slot />
  </UserAvatar>
</template>
