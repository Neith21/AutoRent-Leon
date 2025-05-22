<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useMainStore } from '@/stores/main'
import { mdiEye, mdiTrashCan, mdiPencil, mdiPlus, mdiMagnify, mdiFilePdfBox, mdiFileExcel, mdiFileDelimited } from '@mdi/js'
import CardBoxModal from '@/components/CardBoxModal.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseButton from '@/components/BaseButton.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { jwtDecode } from "jwt-decode";
import axios from 'axios'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import { saveAs } from 'file-saver'
import * as XLSX from 'xlsx'

const mainStore = useMainStore()
const token = localStorage.getItem('autorent_leon_token')
const users = ref([])
const searchTerm = ref('')

// Pagination
const perPage = ref(5)
const currentPage = ref(0)
const filteredUsers = computed(() => {
  if (!searchTerm.value) return users.value
  return users.value.filter(user => {
    return Object.values(user).some(value => 
      value && value.toString().toLowerCase().includes(searchTerm.value.toLowerCase())
    )
  })
})
const itemsPaginated = computed(() =>
  filteredUsers.value.slice(perPage.value * currentPage.value, perPage.value * (currentPage.value + 1))
)
const numPages = computed(() => Math.ceil(filteredUsers.value.length / perPage.value))
const currentPageHuman = computed(() => currentPage.value + 1)
const pagesList = computed(() => Array.from({ length: numPages.value }, (_, i) => i))

// Reset to first page when search changes
watch(searchTerm, () => {
  currentPage.value = 0
})

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
  modalTitle.value = 'Editar Usuario'
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
}

const config = {
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}` 
  } 
}

// Submit create or update
const handleSubmit = async () => {
  loading.value = true
  try {
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
    await axios.put(
      `${import.meta.env.VITE_API_URL}user/delete/${currentUser.value.user_id}`,
      {},
      config
    )
    
    isDeleteModalActive.value = false
    await fetchUsers()
  } catch (e) {
    console.error('Error deleting user:', e)
    alert('Error deleting: ' + e.message)
  } finally {
    loading.value = false
  }
}

// Export functions
const exportToPDF = () => {
    try {
        // Crear documento PDF con orientación horizontal
        const doc = new jsPDF({
            orientation: 'landscape',
            unit: 'mm',
            format: 'a4'
        })
        
        // Título y fecha
        doc.setFontSize(18)
        doc.text('Reporte de Usuarios', 14, 22)
        doc.setFontSize(11)
        doc.text(`Fecha: ${new Date().toLocaleDateString()}`, 14, 30)
        
        // Definir columnas y datos
        const tableColumn = ["ID", "Username", "Nombre", "Apellido", "Email"]
        const tableRows = []
        
        // Preparar datos para la tabla
        filteredUsers.value.forEach(user => {
            const userData = [
                user.user_id || '',
                user.username || '',
                user.first_name || '',
                user.last_name || '',
                user.email || ''
            ]
            tableRows.push(userData)
        })
        
        // Generar tabla automática
        autoTable(doc, {
            head: [tableColumn],
            body: tableRows,
            startY: 35,
            theme: 'grid',
            styles: { fontSize: 8, cellPadding: 2 },
            headStyles: { 
                fillColor: [41, 128, 185],
                textColor: [255, 255, 255],
                fontStyle: 'bold'
            },
            alternateRowStyles: { fillColor: [245, 245, 245] },
            margin: { left: 10, right: 10 }
        })
        
        // Guardar el documento
        doc.save('usuarios.pdf')
    } catch (error) {
        console.error('Error al generar PDF:', error)
        alert('Error al generar PDF: ' + error.message)
    }
}

const exportToCSV = () => {
    const headers = ["ID", "Username", "Nombre", "Apellido", "Email"]
    
    let csvContent = headers.join(',') + '\n'
    
    filteredUsers.value.forEach(user => {
        const row = [
            user.user_id,
            user.username,
            user.first_name,
            user.last_name,
            user.email
        ]
        
        // Escape commas and quotes
        const formattedRow = row.map(cell => {
            if (cell === null || cell === undefined) return ''
            cell = cell.toString()
            if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) {
                return `"${cell.replace(/"/g, '""')}"`
            }
            return cell
        })
        
        csvContent += formattedRow.join(',') + '\n'
    })
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    saveAs(blob, 'usuarios.csv')
}

const exportToExcel = () => {
    const headers = ["ID", "Username", "Nombre", "Apellido", "Email"]
    
    const data = filteredUsers.value.map(user => [
        user.user_id,
        user.username,
        user.first_name,
        user.last_name,
        user.email
    ])
    
    data.unshift(headers)
    
    const ws = XLSX.utils.aoa_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, "Usuarios")
    
    XLSX.writeFile(wb, 'usuarios.xlsx')
}
</script>

<template>
  <!-- Create/Edit Modal -->
  <CardBoxModal v-model="isModalActive" :title="modalTitle">
    <form @submit.prevent="handleSubmit">
      <div class="space-y-4">
        <div>
          <label for="first_name" class="block text-sm font-medium">Nombre</label>
          <input v-model="form.first_name" id="first_name" type="text" class="mt-1 block w-full" required />
        </div>
        <div>
          <label for="last_name" class="block text-sm font-medium">Apellido</label>
          <input v-model="form.last_name" id="last_name" type="text" class="mt-1 block w-full" required />
        </div>
        <div v-if="modalTitle !== 'Editar Usuario'">
          <label for="email" class="block text-sm font-medium">Correo Electrónico</label>
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
  <CardBoxModal v-model="isDeleteModalActive" title="Confirmar Eliminación" button="danger" has-cancel>
    <p>¿Está seguro que desea desactivar al usuario <strong>{{ currentUser.username }}</strong>?</p>
    <p>Esta acción solo marcará el usuario como inactivo.</p>
    <div class="mt-6 flex justify-end space-x-2">
      <BaseButton color="whiteDark" label="Cancelar" @click="isDeleteModalActive = false" />
      <BaseButton 
        color="danger" 
        :label="loading ? 'Eliminando...' : 'Eliminar'" 
        :disabled="loading" 
        @click="confirmDelete"
      />
    </div>
  </CardBoxModal>

  <!-- Search and Actions Bar -->
  <div class="flex flex-wrap items-center justify-between gap-2 mb-4">
    <div class="flex items-center gap-2">
      <!-- Para crear usuarios -->
      <!--<BaseButton color="info" :icon="mdiPlus" label="Crear Usuario" @click="openCreate" />-->
    </div>
    
    <div v-if="isSuperuser" class="flex items-center gap-2">
      <div class="relative">
        <input 
          v-model="searchTerm"
          type="text"
          placeholder="Buscar..." 
          class="pl-10 pr-4 py-2 border rounded-lg focus:ring focus:ring-blue-200"
        />
        <div class="absolute left-3 top-2.5 text-gray-400">
          <span class="material-icons-outlined">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path :d="mdiMagnify" fill="currentColor" />
            </svg>
          </span>
        </div>
      </div>
      
      <BaseButton color="success" small :icon="mdiFilePdfBox" title="Exportar a PDF" @click="exportToPDF" />
      <BaseButton color="info" small :icon="mdiFileDelimited" title="Exportar a CSV" @click="exportToCSV" />
      <BaseButton color="warning" small :icon="mdiFileExcel" title="Exportar a Excel" @click="exportToExcel" />
    </div>
  </div>

  <div class="overflow-x-auto">
    <table class="w-full">
      <thead>
        <tr>
          <th />
          <th>ID</th>
          <th>Nombre</th>
          <th>Apellido</th>
          <th>Correo</th>
          <th v-if="isSuperuser">Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in itemsPaginated" :key="user.user_id">
          <td class="border-b-0 lg:w-6 before:hidden">
            <UserAvatar :src="user.user_image" :username="user.username" class="w-24 h-24 mx-auto lg:w-6 lg:h-6" />
          </td>
          <td data-label="ID">{{ user.user_id }}</td>
          <td data-label="Nombre">{{ user.first_name }}</td>
          <td data-label="Apellido">{{ user.last_name }}</td>
          <td data-label="Correo">{{ user.email }}</td>
          <td v-if="isSuperuser" class="whitespace-nowrap" data-label="Acciones">
            <BaseButtons type="justify-start lg:justify-center" no-wrap>
              <BaseButton 
                color="info" 
                :icon="mdiPencil" 
                small 
                title="Editar" 
                @click="openEdit(user)" 
              />
              <BaseButton 
                color="danger"
                :icon="mdiTrashCan"
                small
                title="Eliminar"
                @click="openDelete(user)"
              />
            </BaseButtons>
          </td>
        </tr>
        <tr v-if="itemsPaginated.length === 0">
          <td colspan="7" class="text-center py-4">No se encontraron resultados</td>
        </tr>
      </tbody>
    </table>
  </div>
  
  <!-- Pagination -->
  <div class="p-3 lg:px-6 border-t border-gray-100 dark:border-slate-800">
    <div class="flex flex-wrap items-center justify-between gap-3">
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
      <small>Página {{ currentPageHuman }} de {{ numPages }}</small>
    </div>
  </div>
</template>

<style scoped>
  /* Mejoras de responsividad para móviles */
  @media (max-width: 768px) {
    table {
      border: 0;
    }
    
    table thead {
      display: none;
    }
    
    table tr {
      margin-bottom: 1rem;
      display: block;
      border: 1px solid #ddd;
      border-radius: 0.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      padding: 0.5rem;
    }
    
    table td {
      display: flex;
      justify-content: space-between;
      text-align: right;
      padding: 0.5rem;
      border-bottom: 1px solid #eee;
    }
    
    table td:last-child {
      border-bottom: 0;
    }
    
    table td::before {
      content: attr(data-label);
      float: left;
      font-weight: bold;
    }

    table td.before\:hidden::before {
      content: none;
    }
  }
</style>