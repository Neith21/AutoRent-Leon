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
    meta: { title: 'Tables', secure: true, requiredPermission: 'user.view_user' },
    path: '/tables',
    name: 'tables',
    component: () => import('@/views/TablesView.vue'),
  },
  {
    meta: { title: 'Branches', secure: true, requiredPermission: 'branch.view_branch' },
    path: '/branches',
    name: 'branches',
    component: () => import('@/views/BranchView.vue'),
  },
  {
    meta: { title: 'Crear Sucursal', secure: true, requiredPermission: 'branch.add_branch' },
    path: '/branch/create',
    name: 'branchCreate',
    component: () => import('@/views/BranchCreateView.vue'),
  },
  {
    meta: { title: 'Editar Sucursal', secure: true, requiredPermission: 'branch.change_branch' },
    path: '/branch/edit/:id',
    name: 'branchEdit',
    component: () => import('@/views/BranchEditView.vue'),
  },
  {
    meta: { title: 'Vehicles', secure: true, requiredPermission: 'vehicle.view_vehicle' },
    path: '/vehicles',
    name: 'vehicles',
    component: () => import('@/views/VehicleView.vue'),
  },
  {
    meta: { title: 'Crear Vehículo', secure: true, requiredPermission: 'vehicle.add_vehicle' },
    path: '/vehicles/create',
    name: 'vehicleCreate', 
    component: () => import('@/views/VehicleCreateView.vue'),
  },
  {
    meta: { title: 'Editar Vehículo', secure: true, requiredPermission: 'vehicle.change_vehicle' },
    path: '/vehicles/edit/:id',
    name: 'vehicleEdit',
    component: () => import('@/views/VehicleEditView.vue'),
    props: true
  },
  {
    meta: { title: 'Modelos de Vehículo', secure: true, requiredPermission: 'vehiclemodel.view_vehiclemodel' },
    path: '/vehiclemodels',
    name: 'vehicleModels',
    component: () => import('@/views/VehicleModelView.vue'),
  },
  {
    meta: { title: 'Customer', secure: true, requiredPermission: 'customer.view_customer' },
    path: '/customers',
    name: 'customers',
    component: () => import('@/views/CustomerView.vue'),
  },
  {
    meta: { title: 'Crear Cliente', secure: true, requiredPermission: 'customer.add_customer' },
    path: '/customers/create',
    name: 'customerCreate',
    component: () => import('@/views/CustomerCreateView.vue'),
  },
  {
    meta: { title: 'Editar Cliente', secure: true, requiredPermission: 'customer.change_customer' },
    path: '/customers/edit/:id',
    name: 'customerEdit',
    component: () => import('@/views/CustomerEditView.vue'),
    props: true
  },
  {
    meta: { title: 'Marcas', secure: true, requiredPermission: 'brand.view_brand' },
    path: '/brands',
    name: 'brands',
    component: () => import('@/views/BrandView.vue'),
  },
  {
    meta: { title: 'Categorías', secure: true, requiredPermission: 'vehiclecategory.view_vehiclecategory' },
    path: '/vehiclecategories',
    name: 'vehicleCategories',
    component: () => import('@/views/VehicleCategoryView.vue'),
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
    meta: { title: 'No Autorizado' },
    path: '/unauthorized',
    name: 'unauthorized',
    component: () => import('@/views/UnauthorizedView.vue'),
  },
  {
    meta: {
      title: 'Error',
    },
    path: '/error',
    name: 'error',
    component: () => import('@/views/ErrorView.vue'),
  },
  { 
    path: '/:pathMatch(.*)*', 
    name: 'NotFound', 
    component: () => import('@/views/ErrorView.vue'),
    meta: { title: 'Página no encontrada' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  },
})

//guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.secure) {
    const isLoggedIn = authStore.checkLoggedIn(); // Verifica token (existencia y expiración)

    if (!isLoggedIn) {
      authStore.clearAuthData();
      return next({ name: 'login', query: { redirect: to.fullPath } });
    }
    if (authStore.userPermissions === null) {
        const permissionsLoadedOk = await authStore.fetchUserPermissions();
        if (!permissionsLoadedOk) {
            if (!authStore.checkLoggedIn()) {
                return next({ name: 'login', query: { redirect: to.fullPath } });
            } else {
                return next({ name: 'unauthorized', query: { error: 'permissions_unavailable' } });
            }
        }
    }

    if (to.meta.requiredPermission) {
      if (!authStore.hasPermission(to.meta.requiredPermission)) {
        return next({ name: 'unauthorized', query: { attempted: to.name, required: to.meta.requiredPermission } });
      }
    }
    return next();

  } else if ((to.name === 'login' || to.name === 'register') && authStore.isAuthenticated) {
    return next({ name: 'dashboard' });
  } else {
    return next();
  }
});

export default router;