<script setup>
import { defineProps, defineEmits } from 'vue';
import BaseButton from '@/components/BaseButton.vue'; // Asegúrate de que la ruta sea correcta

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Confirmar Acción'
  },
  message: {
    type: String,
    default: '¿Está seguro de que desea realizar esta acción?'
  },
  confirmLabel: {
    type: String,
    default: 'Confirmar'
  },
  cancelLabel: {
    type: String,
    default: 'Cancelar'
  },
  confirmColor: {
    type: String,
    default: 'info'
  },
  cancelColor: {
    type: String,
    default: 'whiteDark'
  }
});

const emit = defineEmits(['confirm', 'cancel', 'update:show']);

const confirm = () => {
  emit('confirm');
  emit('update:show', false); // Oculta el modal al confirmar
};

const cancel = () => {
  emit('cancel');
  emit('update:show', false); // Oculta el modal al cancelar
};

// Ocultar el modal al presionar ESC (opcional)
const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    cancel();
  }
};
</script>

<template>
  <Transition name="fade">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @keydown.esc="handleKeydown" tabindex="-1">
      <div class="bg-white p-6 rounded-lg shadow-xl max-w-sm w-full mx-4" @click.stop>
        <h3 class="text-lg font-bold mb-4">{{ title }}</h3>
        <p class="mb-4">{{ message }}</p>
        <div class="flex justify-end space-x-4">
          <BaseButton 
            :label="cancelLabel" 
            :color="cancelColor" 
            @click="cancel"
            outline
          />
          <BaseButton 
            :label="confirmLabel" 
            :color="confirmColor" 
            @click="confirm"
          />
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
/* Transiciones simples para el modal */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>