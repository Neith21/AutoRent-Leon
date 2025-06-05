import { defineStore } from 'pinia'
import { ref, watchEffect } from 'vue'

export const useDarkModeStore = defineStore('darkMode', () => {
  const getInitialDarkMode = () => {
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
      return false;
    }

    const storedValue = localStorage.getItem('darkMode');
    if (storedValue !== null) {
      return storedValue === '1';
    }

    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return true;
    }

    return false;
  };

  const isEnabled = ref(getInitialDarkMode());

  function set(payload = null) {
    isEnabled.value = payload !== null ? payload : !isEnabled.value;
  }

  if (typeof document !== 'undefined') {
    watchEffect(() => {
      const active = isEnabled.value;

      document.body.classList.toggle('dark-scrollbars', active);
      document.documentElement.classList.toggle('dark', active);
      document.documentElement.classList.toggle('dark-scrollbars-compat', active);

      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('darkMode', active ? '1' : '0');
      }
    });
  }

  return {
    isEnabled,
    set,
  };
})