// NotificationBar.vue
<script setup>
import { computed, useSlots } from 'vue';
import { mdiClose } from '@mdi/js';
import { colorsBgLight, colorsOutline } from '@/colors.js';
import BaseLevel from '@/components/BaseLevel.vue';
import BaseIcon from '@/components/BaseIcon.vue';
import BaseButton from '@/components/BaseButton.vue';

const props = defineProps({
  icon: {
    type: String,
    default: null,
  },
  outline: Boolean,
  color: {
    type: String,
    required: true,
  },
  modelValue: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(['update:modelValue', 'dismiss']);

const componentClass = computed(() =>
  props.outline ? colorsOutline[props.color] : colorsBgLight[props.color],
);

const dismiss = () => {
  emit('update:modelValue', false);
  emit('dismiss');
};

const slots = useSlots();
const hasRightSlot = computed(() => slots.right);
</script>

<template>
  <div
    v-if="modelValue"
    :class="componentClass"
    class="px-3 py-6 md:py-3 mb-6 last:mb-0 border rounded-lg transition-colors duration-150 animate-fade-in"
    role="alert"
  >
    <BaseLevel>
      <div class="flex flex-col md:flex-row items-center">
        <BaseIcon
          v-if="icon"
          :path="icon"
          w="w-10 md:w-5"
          h="h-10 md:h-5"
          size="24"
          class="md:mr-2"
        />
        <span class="text-center md:text-left md:py-2 whitespace-pre-line"><slot /></span>
      </div>
      <slot v-if="hasRightSlot" name="right" />
      <BaseButton v-else :icon="mdiClose" small rounded-full color="white" @click="dismiss" />
    </BaseLevel>
  </div>
</template>