<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMainStore } from '@/stores/main'
import { mdiEye, mdiTrashCan, mdiPencil, mdiPlus } from '@mdi/js'
import CardBoxModal from '@/components/CardBoxModal.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseButton from '@/components/BaseButton.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { jwtDecode } from "jwt-decode";
import axios from 'axios'

const mainStore = useMainStore()
const token = localStorage.getItem('autorent_leon_token')
const users = ref([])

// Pagination
const perPage = ref(5)
const currentPage = ref(0)
const itemsPaginated = computed(() =>
  users.value.slice(perPage.value * currentPage.value, perPage.value * (currentPage.value + 1))
)
const numPages = computed(() => Math.ceil(users.value.length / perPage.value))
const currentPageHuman = computed(() => currentPage.value + 1)
const pagesList = computed(() => Array.from({ length: numPages.value }, (_, i) => i))

// Modals and form state
const isModalActive = ref(false)
const isDeleteModalActive = ref(false)
const modalTitle = ref('')
const loading = ref(false)
const currentUser = ref({})
const form = ref({ 
  user_id: null, 
  username: '', 
  first_name: '', 
  last_name: '', 
  email: '' 
})

const isSuperuser = ref('');
if (token) {
  try {
    const decoded = jwtDecode(token);
    isSuperuser.value = decoded.is_superuser || '';
  } catch (error) {
    console.error('Error decoding JWT token:', error);
  }
}

// Load users
const fetchUsers = async () => {
  if (!token) return
  try {
    const decoded = jwtDecode(token)
    const config = { 
      headers: { 
        'Content-Type': 'application/json', 
        'Authorization': `Bearer ${token}` 
      } 
    }
    
    let response = decoded.is_superuser
      ? await axios.get(`${import.meta.env.VITE_API_URL}user`, config)
      : await axios.get(`${import.meta.env.VITE_API_URL}user/${decoded.id}`, config)
    
    const data = response.data?.data
    users.value = Array.isArray(data) ? data : data ? [data] : []
  } catch (e) {
    console.error('Error fetching users:', e)
  }
}

onMounted(() => {
  fetchUsers()
})

// Modal actions
/*const openCreate = () => {
  modalTitle.value = 'Create User'
  form.value = { user_id: null, username: '', first_name: '', last_name: '', email: '' }
  isModalActive.value = true
}*/

const openEdit = (user) => {
  modalTitle.value = 'Edit User'
  form.value = { 
    user_id: user.user_id, 
    username: user.username, 
    first_name: user.first_name, 
    last_name: user.last_name, 
    email: user.email 
  }
  isModalActive.value = true
}

const openDelete = (user) => {
  currentUser.value = user
  isDeleteModalActive.value = true
  console.log(currentUser.value.user_id)
}

// Submit create or update
const handleSubmit = async () => {
  loading.value = true
  try {
    const config = { 
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      } 
    }
    
    if (form.value.user_id) {
      await axios.put(
        `${import.meta.env.VITE_API_URL}user/${form.value.user_id}`, 
        form.value, 
        config
      )
    } /*else {
      await axios.post(`${import.meta.env.VITE_API_URL}user`, form.value, config)
    }*/
    
    isModalActive.value = false
    // Volvemos a cargar los usuarios en lugar de recargar la página
    await fetchUsers()
  } catch (e) {
    console.error('Error saving user:', e)
    alert('Error: ' + e.message)
  } finally {
    loading.value = false
  }
}

// Confirm delete
const confirmDelete = async () => {
  loading.value = true
  try {
    await axios.put(`${import.meta.env.VITE_API_URL}user/delete/${currentUser.value.user_id}`, {
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      }
    })
    
    isDeleteModalActive.value = false
    // Volvemos a cargar los usuarios en lugar de recargar la página
    await fetchUsers()
  } catch (e) {
    console.error('Error deleting user:', e)
    alert('Error deleting: ' + e.message)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <!-- Create/Edit Modal -->
  <CardBoxModal v-model="isModalActive" :title="modalTitle">
    <form @submit.prevent="handleSubmit">
      <div class="space-y-4">
        <div>
          <label for="username" class="block text-sm font-medium">Username</label>
          <input v-model="form.username" id="username" type="text" class="mt-1 block w-full" required />
        </div>
        <div>
          <label for="first_name" class="block text-sm font-medium">First Name</label>
          <input v-model="form.first_name" id="first_name" type="text" class="mt-1 block w-full" required />
        </div>
        <div>
          <label for="last_name" class="block text-sm font-medium">Last Name</label>
          <input v-model="form.last_name" id="last_name" type="text" class="mt-1 block w-full" required />
        </div>
        <div>
          <label for="email" class="block text-sm font-medium">Email</label>
          <input v-model="form.email" id="email" type="email" class="mt-1 block w-full" required />
        </div>
      </div>
      <div class="mt-6 flex justify-end space-x-2">
        <BaseButton color="whiteDark" label="Cancelar" @click="isModalActive = false" />
        <BaseButton 
          color="info" 
          type="submit" 
          :disabled="loading" 
          :label="loading ? 'Guardando...' : 'Guardar'" 
        />
      </div>
    </form>
  </CardBoxModal>

  <!-- Delete Confirmation Modal -->
  <CardBoxModal v-model="isDeleteModalActive" title="Confirmar eliminación" button="danger" has-cancel>
    <p>¿Está seguro que desea eliminar al usuario <strong>{{ currentUser.username }}</strong>?</p>
    <p>Esta acción solo desactivará el usuario en el sistema.</p>
    
    <template #footer>
      <BaseButtons>
        <BaseButton color="whiteDark" label="Cancelar" @click="isDeleteModalActive = false" />
        <BaseButton 
          color="danger" 
          :label="loading ? 'Eliminando...' : 'Eliminar'" 
          :disabled="loading" 
          @click="confirmDelete"
        />
      </BaseButtons>
    </template>
  </CardBoxModal>

  <!-- Button to create a new user -->
  <!--<div class="mb-4">
    <BaseButton 
      color="info" 
      :icon="mdiPlus" 
      label="Crear Usuario" 
      @click="openCreate" 
    />
  </div>-->

  <!-- Users Table -->
  <table>
    <thead>
      <tr>
        <th />
        <th>Id</th>
        <th>Username</th>
        <th>First Name</th>
        <th>Last Name</th>
        <th>Email</th>
        <th>Acciones</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="user in itemsPaginated" :key="user.user_id">
        <td class="border-b-0 lg:w-6 before:hidden">
          <UserAvatar :src="user.user_image" :username="user.username" class="w-24 h-24 mx-auto lg:w-6 lg:h-6" />
        </td>
        <td data-label="Id">{{ user.user_id }}</td>
        <td data-label="Username">{{ user.username }}</td>
        <td data-label="first_name">{{ user.first_name }}</td>
        <td data-label="last_name">{{ user.last_name }}</td>
        <td data-label="email">{{ user.email }}</td>
        <td class="before:hidden lg:w-1 whitespace-nowrap">
          <BaseButtons type="justify-start lg:justify-end" no-wrap>
            <BaseButton 
              color="info" 
              :icon="mdiPencil" 
              small 
              title="Editar" 
              @click="openEdit(user)" 
            />
            <BaseButton v-if="isSuperuser"
              color="danger"
              :icon="mdiTrashCan"
              small
              title="Eliminar"
              @click="openDelete(user)"
            />
          </BaseButtons>
        </td>
      </tr>
    </tbody>
  </table>
  
  <!-- Pagination -->
  <div class="p-3 lg:px-6 border-t border-gray-100 dark:border-slate-800">
    <BaseLevel>
      <BaseButtons>
        <BaseButton
          v-for="page in pagesList"
          :key="page"
          :active="page === currentPage"
          :label="page + 1"
          :color="page === currentPage ? 'lightDark' : 'whiteDark'"
          small
          @click="currentPage = page"
        />
      </BaseButtons>
      <small>Page {{ currentPageHuman }} of {{ numPages }}</small>
    </BaseLevel>
  </div>
</template>