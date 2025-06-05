// File: src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useMainStore } from '@/stores/main.js'

import './css/main.css'

import { useDarkModeStore } from './stores/darkMode'

const pinia = createPinia()

createApp(App).use(router).use(pinia).mount('#app')

const mainStore = useMainStore(pinia)

mainStore.fetchSampleClients()
mainStore.fetchSampleHistory()

const darkModeStore = useDarkModeStore(pinia)

if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
  const storedDarkMode = localStorage.getItem('darkMode');
  const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (storedDarkMode === '1' || (storedDarkMode === null && prefersDarkScheme)) {
    if (!darkModeStore.isEnabled) {
        darkModeStore.set(true);
    }
  } else if (storedDarkMode === '0' || (storedDarkMode === null && !prefersDarkScheme)) {
    if (darkModeStore.isEnabled) {
        darkModeStore.set(false);
    }
  }
}

const defaultDocumentTitle = 'Auntorent Leon'

router.afterEach((to) => {
  document.title = to.meta?.title
    ? `${to.meta.title} — ${defaultDocumentTitle}`
    : defaultDocumentTitle
})