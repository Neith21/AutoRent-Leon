import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '@/views/HomeView.vue'
import { useAuthStore } from '@/stores/authStore'

const routes = [
  {
    // Document title tag
    // We combine it with defaultDocumentTitle set in `src/main.js` on router.afterEach hook
    meta: {
      title: 'Dashboard',
    },
    path: '/',
    name: 'dashboard',
    component: Home,
    meta: {
      secure: true
    }
  },
  {
    meta: {
      title: 'Tables',
      secure: true
    },
    path: '/tables',
    name: 'tables',
    component: () => import('@/views/TablesView.vue'),
  },
  {
    meta: {
      title: 'Forms',
      secure: true
    },
    path: '/forms',
    name: 'forms',
    component: () => import('@/views/FormsView.vue'),
  },
  {
    meta: {
      title: 'Profile',
      secure: true
    },
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
  },
  {
    meta: {
      title: 'Login',
    },
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
  },
  {
    meta: {
      title: 'Register',
    },
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue'),
  },
  {
    meta: {
      title: 'Error',
    },
    path: '/error',
    name: 'error',
    component: () => import('@/views/ErrorView.vue'),
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  },
})

//guards
router.beforeEach(async (to, from) => {
  const store = useAuthStore();
  
  // Si la ruta requiere autenticación
  if (to.meta.secure) {
      // Verifica si está logueado
      const isLoggedIn = store.checkLoggedIn();
      
      // Si no está logueado y trata de acceder a una ruta segura
      if (!isLoggedIn) {
          return { name: 'login' }; // Usa navegación declarativa de vue-router
      }
  }
  
  // Si intenta acceder al login estando autenticado, redirigir al dashboard
  if ((to.name === 'login' || to.name === 'register') && store.authId) {
      return { name: 'dashboard' };
  }
})

export default router
