<script setup>
import { mdiForwardburger, mdiBackburger, mdiMenu } from '@mdi/js'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import menuAsideItemsDefinition from '@/menuAside.js'
import menuNavBar from '@/menuNavBar.js'
import { useDarkModeStore } from '@/stores/darkMode.js'
import BaseIcon from '@/components/BaseIcon.vue' 
import NavBar from '@/components/NavBar.vue'
import NavBarItemPlain from '@/components/NavBarItemPlain.vue'
import AsideMenu from '@/components/AsideMenu.vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore();

const layoutAsidePadding = 'xl:pl-60'

const darkModeStore = useDarkModeStore()

const router = useRouter()

const isAsideMobileExpanded = ref(false)
const isAsideLgActive = ref(false)

router.beforeEach(() => {
  isAsideMobileExpanded.value = false
  isAsideLgActive.value = false
})

const menuClick = (event, item) => {
  if (item.isToggleLightDark) {
    darkModeStore.set()
  }

  if (item.isLogout) {
    authStore.logout()
  }

}

const filteredMenuAside = computed(() => {
  const canShowItem = (item) => {
    if (item.requiredPermission) {
      return authStore.hasPermission(item.requiredPermission);
    }
    return true;
  };

  const processMenuItems = (items) => {
    if (!items) {
      return [];
    }

    return items
      .map(item => {
        if (!canShowItem(item)) {
          return null;
        }

        if (item.menu && Array.isArray(item.menu)) {
          const filteredSubMenu = processMenuItems(item.menu);
          
          if (item.to || filteredSubMenu.length > 0) {
            return { ...item, menu: filteredSubMenu };
          } else {
            return null; 
          }
        }

        return item;
      })
      .filter(item => item !== null);
  };

  if (authStore.isLoadingPermissions) {
    return []; 
  }
  if (authStore.permissionsError) {
    console.error("Error al cargar permisos, el menú lateral podría estar incompleto:", authStore.permissionsError);
    return [{ label: 'Error de menú', icon: mdiAlertCircle }];
  }
  
  return processMenuItems(menuAsideItemsDefinition);
});

</script>

<template>
  <div
    :class="{
      'overflow-hidden lg:overflow-visible': isAsideMobileExpanded,
    }"
  >
    <div
      :class="[layoutAsidePadding, { 'ml-60 lg:ml-0': isAsideMobileExpanded }]"
      class="pt-14 min-h-screen w-screen transition-position lg:w-auto bg-gray-50 dark:bg-slate-800 dark:text-slate-100"
    >
      <NavBar
        :menu="menuNavBar"
        :class="[layoutAsidePadding, { 'ml-60 lg:ml-0': isAsideMobileExpanded }]"
        @menu-click="menuClick"
      >
        <NavBarItemPlain
          display="flex lg:hidden"
          @click.prevent="isAsideMobileExpanded = !isAsideMobileExpanded"
        >
          <BaseIcon :path="isAsideMobileExpanded ? mdiBackburger : mdiForwardburger" size="24" />
        </NavBarItemPlain>
        <NavBarItemPlain display="hidden lg:flex xl:hidden" @click.prevent="isAsideLgActive = true">
          <BaseIcon :path="mdiMenu" size="24" />
        </NavBarItemPlain>
      </NavBar>
      <AsideMenu
        :is-aside-mobile-expanded="isAsideMobileExpanded"
        :is-aside-lg-active="isAsideLgActive"
        :menu="filteredMenuAside" @menu-click="menuClick" 
        @aside-lg-close-click="isAsideLgActive = false"
      />
      <slot />
      </div>
  </div>
</template>