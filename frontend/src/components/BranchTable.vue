<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useMainStore } from '@/stores/main'
import { mdiTrashCan, mdiPencil, mdiPlus, mdiMagnify, mdiFilePdfBox, mdiFileExcel, mdiFileDelimited } from '@mdi/js'
import CardBoxModal from '@/components/CardBoxModal.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseButton from '@/components/BaseButton.vue'
import axios from 'axios'
import { jwtDecode } from "jwt-decode";
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import { saveAs } from 'file-saver'
import * as XLSX from 'xlsx'

const mainStore = useMainStore()
const token = localStorage.getItem('autorent_leon_token')
const branches = ref([])
const searchTerm = ref('')

// Pagination
const perPage = ref(5)
const currentPage = ref(0)
const filteredBranches = computed(() => {
  if (!searchTerm.value) return branches.value
  return branches.value.filter(branch => {
    return Object.values(branch).some(value => 
      value && value.toString().toLowerCase().includes(searchTerm.value.toLowerCase())
    )
  })
})
const itemsPaginated = computed(() =>
    filteredBranches.value.slice(perPage.value * currentPage.value, perPage.value * (currentPage.value + 1))
)
const numPages = computed(() => Math.ceil(filteredBranches.value.length / perPage.value))
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
const currentBranch = ref({})
const form = ref({
    branch_id: null,
    name: '',
    phone: '',
    address: '',
    department: '',
    district: '',
    email: '',
    userc: '',
    useru: '',
})

const user_id = ref('');
if (token) {
  try {
    const decoded = jwtDecode(token);
    user_id.value = decoded.id || '';
  } catch (error) {
    console.error('Error decodificando token JWT:', error);
  }
}

// Load branches
const fetchBranches = async () => {
    if (!token) return
    try {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        }
        const response = await axios.get(`${import.meta.env.VITE_API_URL}branch`, config)
        branches.value = response.data?.data || []
    } catch (e) {
        console.error('Error obteniendo sucursales:', e)
    }
}

onMounted(() => {
    fetchBranches()
})

// Modal actions
const openCreate = () => {
    modalTitle.value = 'Crear Sucursal'
    form.value = {
        name: '',
        phone: '',
        address: '',
        department: '',
        district: '',
        email: '',
        userc: user_id.value,
        useru: user_id.value
    }
    isModalActive.value = true
}

const openEdit = (branch) => {
    modalTitle.value = 'Editar Sucursal'
    form.value = {
        branch_id: branch.id,
        name: branch.name,
        phone: branch.phone,
        address: branch.address,
        department: branch.department,
        district: branch.district,
        email: branch.email,
        useru: user_id.value
    }
    isModalActive.value = true
}

const openDelete = (branch) => {
    currentBranch.value = branch
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
        if (form.value.branch_id) {
            // UPDATE
            await axios.put(
                `${import.meta.env.VITE_API_URL}branch/${form.value.branch_id}`,
                form.value,
                config
            )
        } else {
            // CREATE
            await axios.post(
                `${import.meta.env.VITE_API_URL}branch`,
                form.value,
                config
            )
        }

        isModalActive.value = false
        await fetchBranches()
    } catch (e) {
        console.error('Error guardando sucursal:', e)
        alert('Error: ' + e.message)
    } finally {
        loading.value = false
    }
}

// Confirm delete (deactivate)
const confirmDelete = async () => {
    loading.value = true
    try {
        await axios.put(
            `${import.meta.env.VITE_API_URL}branch/delete/${currentBranch.value.id}`,
            {},
            config
        )
        isDeleteModalActive.value = false
        await fetchBranches()
    } catch (e) {
        console.error('Error eliminando sucursal:', e)
        alert('Error al eliminar: ' + e.message)
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
        doc.text('Reporte de Sucursales', 14, 22)
        doc.setFontSize(11)
        doc.text(`Fecha: ${new Date().toLocaleDateString()}`, 14, 30)
        
        // Definir columnas y datos
        const tableColumn = ["ID", "Nombre", "Teléfono", "Dirección", "Departamento", "Distrito", "Email"]
        const tableRows = []
        
        // Preparar datos para la tabla
        filteredBranches.value.forEach(branch => {
            const branchData = [
                branch.id || '',
                branch.name || '',
                branch.phone || '',
                branch.address || '',
                branch.department || '',
                branch.district || '',
                branch.email || ''
            ]
            tableRows.push(branchData)
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
        doc.save('sucursales.pdf')
    } catch (error) {
        console.error('Error al generar PDF:', error)
        alert('Error al generar PDF: ' + error.message)
    }
}

const exportToCSV = () => {
    const headers = ["ID", "Nombre", "Teléfono", "Dirección", "Departamento", "Distrito", "Email"]
    
    let csvContent = headers.join(',') + '\n'
    
    filteredBranches.value.forEach(branch => {
        const row = [
            branch.id,
            branch.name,
            branch.phone,
            branch.address,
            branch.department,
            branch.district,
            branch.email
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
    saveAs(blob, 'sucursales.csv')
}

const exportToExcel = () => {
    const headers = ["ID", "Nombre", "Teléfono", "Dirección", "Departamento", "Distrito", "Email"]
    
    const data = filteredBranches.value.map(branch => [
        branch.id,
        branch.name,
        branch.phone,
        branch.address,
        branch.department,
        branch.district,
        branch.email
    ])
    
    data.unshift(headers)
    
    const ws = XLSX.utils.aoa_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, "Sucursales")
    
    XLSX.writeFile(wb, 'sucursales.xlsx')
}
</script>

<template>
    <!-- Create/Edit Modal -->
    <CardBoxModal v-model="isModalActive" :title="modalTitle">
        <form @submit.prevent="handleSubmit">
            <div class="space-y-4">
                <div>
                    <label for="name" class="block text-sm font-medium">Nombre</label>
                    <input v-model="form.name" id="name" type="text" class="mt-1 block w-full" required />
                </div>
                <div>
                    <label for="phone" class="block text-sm font-medium">Teléfono</label>
                    <input v-model="form.phone" id="phone" type="text" class="mt-1 block w-full" required />
                </div>
                <div>
                    <label for="address" class="block text-sm font-medium">Dirección</label>
                    <input v-model="form.address" id="address" type="text" class="mt-1 block w-full" required />
                </div>
                <div>
                    <label for="department" class="block text-sm font-medium">Departamento</label>
                    <input v-model="form.department" id="department" type="text" class="mt-1 block w-full" required />
                </div>
                <div>
                    <label for="district" class="block text-sm font-medium">Distrito</label>
                    <input v-model="form.district" id="district" type="text" class="mt-1 block w-full" required />
                </div>
                <div>
                    <label for="email" class="block text-sm font-medium">Correo Electrónico</label>
                    <input v-model="form.email" id="email" type="email" class="mt-1 block w-full" required />
                </div>
            </div>
            <div class="mt-6 flex justify-end space-x-2">
                <BaseButton color="whiteDark" label="Cancelar" @click="isModalActive = false" />
                <BaseButton color="info" type="submit" :disabled="loading" :label="loading ? 'Guardando...' : 'Guardar'" />
            </div>
        </form>
    </CardBoxModal>

    <!-- Delete Confirmation Modal -->
    <CardBoxModal v-model="isDeleteModalActive" title="Confirmar Eliminación" button="danger" has-cancel>
        <p>¿Está seguro que desea desactivar la sucursal <strong>{{ currentBranch.name }}</strong>?</p>
        <p>Esta acción solo marcará la sucursal como inactiva.</p>
        <div class="mt-6 flex justify-end space-x-2">
            <BaseButton color="whiteDark" label="Cancelar" @click="isDeleteModalActive = false" />
            <BaseButton color="danger" :label="loading ? 'Eliminando...' : 'Eliminar'" :disabled="loading" @click="confirmDelete" />
        </div>
    </CardBoxModal>

    <!-- Search and Actions Bar -->
    <div class="flex flex-wrap items-center justify-between gap-2 mb-4">
        <div class="flex items-center gap-2">
            <BaseButton color="info" :icon="mdiPlus" label="Crear Sucursal" @click="openCreate" />
        </div>
        
        <div class="flex items-center gap-2">
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
            
            <!-- Export Buttons -->
            <BaseButton color="success" small :icon="mdiFilePdfBox" title="Exportar a PDF" @click="exportToPDF" />
            <BaseButton color="info" small :icon="mdiFileDelimited" title="Exportar a CSV" @click="exportToCSV" />
            <BaseButton color="warning" small :icon="mdiFileExcel" title="Exportar a Excel" @click="exportToExcel" />
        </div>
    </div>

    <!-- Branches Table -->
    <div class="overflow-x-auto">
        <table class="w-full">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Teléfono</th>
                    <th>Dirección</th>
                    <th>Departamento</th>
                    <th>Distrito</th>
                    <th>Correo</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="b in itemsPaginated" :key="b.id">
                    <td data-label="ID">{{ b.id }}</td>
                    <td data-label="Nombre">{{ b.name }}</td>
                    <td data-label="Teléfono">{{ b.phone }}</td>
                    <td data-label="Dirección">{{ b.address }}</td>
                    <td data-label="Departamento">{{ b.department }}</td>
                    <td data-label="Distrito">{{ b.district }}</td>
                    <td data-label="Correo">{{ b.email }}</td>
                    <td class="whitespace-nowrap" data-label="Acciones">
                        <BaseButtons type="justify-start lg:justify-center" no-wrap>
                            <BaseButton color="info" :icon="mdiPencil" small title="Editar" @click="openEdit(b)" />
                            <BaseButton color="danger" :icon="mdiTrashCan" small title="Eliminar" @click="openDelete(b)" />
                        </BaseButtons>
                    </td>
                </tr>
                <tr v-if="itemsPaginated.length === 0">
                    <td colspan="8" class="text-center py-4">No se encontraron resultados</td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- Pagination -->
    <div class="p-3 lg:px-6 border-t border-gray-100 dark:border-slate-800">
        <div class="flex flex-wrap items-center justify-between gap-3">
            <BaseButtons>
                <BaseButton v-for="page in pagesList" :key="page" :active="page === currentPage" :label="page + 1"
                    :color="page === currentPage ? 'lightDark' : 'whiteDark'" small @click="currentPage = page" />
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
    }
</style>