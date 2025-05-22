<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { mdiArrowLeftCircle, mdiContentSaveEdit } from '@mdi/js';
import axios from 'axios';
import FormField from '@/components/FormField.vue';
import FormControl from '@/components/FormControl.vue';
import BaseButton from '@/components/BaseButton.vue';
import BaseButtons from '@/components/BaseButtons.vue';
import CardBox from '@/components/CardBox.vue';
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue';
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue';
import { useMainStore } from '@/stores/main';
import NotificationBar from '@/components/NotificationBar.vue';

const route = useRoute();
const router = useRouter();
const mainStore = useMainStore();
const token = localStorage.getItem('autorent_leon_token');

const loading = ref(false);
const initialLoading = ref(true);
const loadingDepartments = ref(false);
const loadingMunicipalities = ref(false);
const loadingDistricts = ref(false);

const branchId = ref(null);
const originalBranchName = ref('');

const departments = ref([]);
const selectedDepartmentId = ref(null);
const municipalitiesByDepartment = ref([]);
const selectedMunicipalityId = ref(null);
const districtsByMunicipality = ref([]);

let initialDepartmentIdFromBranch = null;
let initialMunicipalityIdFromBranch = null;
let initialDistrictIdFromBranch = null;

const form = ref({
  id: null,
  name: '',
  phone: '',
  address: '',
  email: '',
  district_id: null,
});

const pageTitle = computed(() => originalBranchName.value ? `Editar Sucursal: ${originalBranchName.value}` : 'Editar Sucursal');
const API_URL = import.meta.env.VITE_API_URL;

const fetchBranchData = async (id) => {
  if (!token || !id) {
    mainStore.notify({ color: 'danger', message: 'No se proporcionó ID de sucursal o falta token.' });
    router.push({ name: 'branches' });
    return false;
  }
  try {
    const config = { headers: { Authorization: `Bearer ${token}` } };
    const response = await axios.get(`${API_URL}branch/${id}`, config);
    const branchData = response.data?.data;

    if (branchData) {
      form.value.id = branchData.id;
      form.value.name = branchData.name || '';
      originalBranchName.value = branchData.name || '';
      form.value.phone = branchData.phone || '';
      form.value.address = branchData.address || '';
      form.value.email = branchData.email || '';
      
      initialDistrictIdFromBranch = branchData.district_id || null;
      form.value.district_id = initialDistrictIdFromBranch;

      if (branchData.district_details?.municipality?.department) {
        initialDepartmentIdFromBranch = branchData.district_details.municipality.department.id;
        initialMunicipalityIdFromBranch = branchData.district_details.municipality.id;
        return true; // ta bien
      } else {
        mainStore.notify({ color: 'warning', message: 'Detalles de ubicación incompletos. Por favor, re-seleccione.' });
        return false; // medio bien
      }
    } else {
      mainStore.notify({ color: 'danger', message: 'Sucursal no encontrada.' });
      router.push({ name: 'branches' });
      return false;
    }
  } catch (e) {
    console.error("Error fetching branch data:", e);
    mainStore.notify({ color: 'danger', message: 'Error cargando datos de la sucursal: ' + (e.response?.data?.message || e.message) });
    router.push({ name: 'branches' });
    return false;
  }
};

const fetchDepartments = async () => {
  if (!token) return;
  loadingDepartments.value = true;
  try {
    const config = { headers: { Authorization: `Bearer ${token}` } };
    const response = await axios.get(`${API_URL}department`, config);
    departments.value = response.data?.data?.map(dept => ({
      id: dept.id,
      label: dept.name || dept.department || 'Departamento Desconocido'
    })) || [];
  } catch (e) {
    console.error("Error fetching departments:", e);
    departments.value = []; // Limpiar si hay horroress
    mainStore.notify({ color: 'danger', message: 'Error cargando departamentos.' });
  } finally {
    loadingDepartments.value = false;
  }
};

const fetchMunicipalitiesForSelectedDepartment = async (departmentId) => {
  if (!token || !departmentId) {
    municipalitiesByDepartment.value = [];
    selectedMunicipalityId.value = null; // resetear si no hay de partamento seleccionado
    districtsByMunicipality.value = [];
    form.value.district_id = null;
    return;
  }
  loadingMunicipalities.value = true;
  try {
    const config = { headers: { Authorization: `Bearer ${token}` } };
    const response = await axios.get(`${API_URL}branch/municipalities/${departmentId}`, config);
    municipalitiesByDepartment.value = response.data?.data?.map(mun => ({
      id: mun.id,
      label: mun.name || 'Municipio Desconocido'
    })) || [];

    if (initialMunicipalityIdFromBranch && municipalitiesByDepartment.value.some(m => m.id === initialMunicipalityIdFromBranch)) {
      selectedMunicipalityId.value = initialMunicipalityIdFromBranch;
    } else if (initialMunicipalityIdFromBranch) {
        selectedMunicipalityId.value = null;
        mainStore.notify({ color: 'warning', message: 'El municipio guardado no pertenece al departamento actual o no existe. Por favor, seleccione uno.' });
    }

  } catch (e) {
    console.error("Error fetching municipalities for department:", e);
    municipalitiesByDepartment.value = [];
    selectedMunicipalityId.value = null;
    mainStore.notify({ color: 'danger', message: `Error cargando municipios: ${e.response?.data?.message || e.message}` });
  } finally {
    loadingMunicipalities.value = false;
  }
};

const fetchDistrictsForSelectedMunicipality = async (municipalityId) => {
  if (!token || !municipalityId) {
    districtsByMunicipality.value = [];
    form.value.district_id = null;
    return;
  }
  loadingDistricts.value = true;
  try {
    const config = { headers: { Authorization: `Bearer ${token}` } };
    const response = await axios.get(`${API_URL}branch/districts/${municipalityId}`, config);
    districtsByMunicipality.value = response.data?.data?.map(dist => ({
      id: dist.id,
      label: dist.name || 'Distrito Desconocido'
    })) || [];

    if (initialDistrictIdFromBranch && !districtsByMunicipality.value.some(d => d.id === initialDistrictIdFromBranch)) {
        mainStore.notify({ color: 'warning', message: 'El distrito guardado no pertenece al municipio actual o no existe. Por favor, seleccione uno si es necesario.' });
    } else if (initialDistrictIdFromBranch && districtsByMunicipality.value.some(d => d.id === initialDistrictIdFromBranch)) {
        form.value.district_id = initialDistrictIdFromBranch;
    }


  } catch (e) {
    console.error("Error fetching districts for municipality:", e);
    districtsByMunicipality.value = [];
    form.value.district_id = null;
    mainStore.notify({ color: 'danger', message: `Error cargando distritos: ${e.response?.data?.message || e.message}` });
  } finally {
    loadingDistricts.value = false;
  }
};

watch(selectedDepartmentId, (newDepartmentId, oldDepartmentId) => {
  if (oldDepartmentId !== null && newDepartmentId !== oldDepartmentId) {
    selectedMunicipalityId.value = null;
    municipalitiesByDepartment.value = [];
    form.value.district_id = null;
    districtsByMunicipality.value = [];
    initialMunicipalityIdFromBranch = null;
    initialDistrictIdFromBranch = null;
  }
  if (newDepartmentId) {
    fetchMunicipalitiesForSelectedDepartment(newDepartmentId);
  }
});

watch(selectedMunicipalityId, (newMunicipalityId, oldMunicipalityId) => {
  if (oldMunicipalityId !== null && newMunicipalityId !== oldMunicipalityId) {
    form.value.district_id = null;
    districtsByMunicipality.value = [];
    initialDistrictIdFromBranch = null;
  }
  if (newMunicipalityId) {
    fetchDistrictsForSelectedMunicipality(newMunicipalityId);
  }
});

onMounted(async () => {
  branchId.value = route.params.id;
  initialLoading.value = true;
  if (branchId.value) {
    await fetchDepartments();
    const branchDataLoadedSuccessfully = await fetchBranchData(branchId.value);

    if (branchDataLoadedSuccessfully && initialDepartmentIdFromBranch) {
      if (departments.value.some(d => d.id === initialDepartmentIdFromBranch)) {
        selectedDepartmentId.value = initialDepartmentIdFromBranch;
      } else {
        mainStore.notify({ color: 'warning', message: 'El departamento original de la sucursal no está disponible. Por favor, seleccione uno nuevo.' });
        initialLoading.value = false;
      }
    } else {
        initialLoading.value = false;
    }
  } else {
    mainStore.notify({ color: 'danger', message: 'ID de sucursal no especificado.' });
    router.push({ name: 'branches' });
    initialLoading.value = false;
  }
  if (!selectedDepartmentId.value) {
      initialLoading.value = false;
  }

  setTimeout(() => {
    initialLoading.value = false;
  }, 1);

});

const getAuthConfigJson = () => ({
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const handleSubmit = async () => {
  if (!form.value.id) {
    mainStore.notify({ color: 'danger', message: 'No se puede actualizar: ID de sucursal no definido.' });
    return;
  }
  loading.value = true;

  const requiredFields = {
    name: 'Nombre de Sucursal',
    phone: 'Teléfono',
    address: 'Dirección',
    email: 'Correo Electrónico',
    district_id: 'Distrito'
  };
  if (!selectedDepartmentId.value) {
     mainStore.notify({ color: 'danger', message: 'El campo Departamento es requerido.' });
     loading.value = false;
     return;
  }
  if (!selectedMunicipalityId.value) {
     mainStore.notify({ color: 'danger', message: 'El campo Municipio es requerido.' });
     loading.value = false;
     return;
  }
  for (const fieldKey in requiredFields) {
    if (form.value[fieldKey] === null || form.value[fieldKey] === '' || form.value[fieldKey] === undefined) {
      mainStore.notify({ color: 'danger', message: `El campo '${requiredFields[fieldKey]}' es requerido.` });
      loading.value = false;
      return;
    }
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (form.value.email && !emailRegex.test(form.value.email)) {
    mainStore.notify({ color: 'danger', message: 'Por favor, ingrese un correo electrónico válido.' });
    loading.value = false;
    return;
  }

  try {
    const payload = { ...form.value };

    await axios.put(`${API_URL}branch/${form.value.id}`, payload, getAuthConfigJson());
    mainStore.notify({ color: 'success', message: 'Sucursal actualizada exitosamente.' });
    router.push({ name: 'branches' });
  } catch (e) {
    console.error('Error actualizando sucursal:', e);
    let messagesToShow = [];
    const errorColor = 'danger';

     if (e.response && e.response.data) {
      const backendError = e.response.data;
      if (backendError.message && backendError.message !== "Datos inválidos. Por favor, corrija los errores.") {
         messagesToShow.push(backendError.message);
      } else if (backendError.mensaje && backendError.mensaje !== "Datos inválidos. Por favor, corrija los errores.") {
         messagesToShow.push(backendError.mensaje);
      }

      if (backendError.details && typeof backendError.details === 'object') {
        for (const field in backendError.details) {
          if (Array.isArray(backendError.details[field])) {
            backendError.details[field].forEach(errText => {
              let fieldNameDisplay = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ');
               if (field === 'district' || field === 'district_id') fieldNameDisplay = 'Distrito';
              messagesToShow.push(`- ${fieldNameDisplay}: ${errText}`);
            });
          }
        }
      }
       if (messagesToShow.length === 0 && (backendError.message || backendError.detail || backendError.mensaje)) {
        messagesToShow.push(backendError.message || backendError.detail || backendError.mensaje);
      }

    } else if (e.message) {
      messagesToShow.push(e.message);
    }

    if (messagesToShow.length === 0) {
      messagesToShow.push('Ha ocurrido un error inesperado. Intente de nuevo.');
    }
    mainStore.notify({
      color: errorColor,
      message: messagesToShow.join('\n'), 
    });
  } finally {
    loading.value = false;
  }
};

const cancelForm = () => {
  router.push({ name: 'branches' });
};

</script>

<template>
  <LayoutAuthenticated>
    <div v-if="mainStore && mainStore.notification" class="sticky top-0 z-40 px-4 md:px-6">
      <NotificationBar
        v-model="mainStore.notification.show"
        :color="mainStore.notification.color"
        :icon="mainStore.notification.icon"
        class="mt-2"
      >
       <pre class="whitespace-pre-wrap">{{ mainStore.notification.message }}</pre>
      </NotificationBar>
    </div>

    <SectionTitleLineWithButton :icon="mdiContentSaveEdit" :title="pageTitle" main style="margin: 1rem;">
      <BaseButton
        :to="{ name: 'branches' }"
        :icon="mdiArrowLeftCircle"
        label="Volver a la lista"
        color="contrast"
        rounded-full
        small
      />
    </SectionTitleLineWithButton>
    <CardBox v-if="!initialLoading && form.id" is-form @submit.prevent="handleSubmit" style="margin: 1rem;">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField label="Nombre de Sucursal" required>
          <FormControl v-model="form.name" id="name" placeholder="Ej: Sucursal Central" />
        </FormField>

        <FormField label="Teléfono" required>
          <FormControl v-model="form.phone" id="phone" placeholder="Ej: 2277-7777" />
        </FormField>

        <FormField label="Correo Electrónico" required>
          <FormControl v-model="form.email" id="email" type="email" placeholder="Ej: central@empresa.com" />
        </FormField>

        <FormField label="Departamento" required>
          <FormControl
            v-model="selectedDepartmentId"
            id="department_id_edit"
            :options="departments"
            :disabled="loadingDepartments || initialLoading"
            placeholder="Seleccione un departamento"
          />
           <div v-if="loadingDepartments" class="text-xs text-gray-500 mt-1">Cargando departamentos...</div>
        </FormField>

        <FormField label="Municipio" required>
          <FormControl
            v-model="selectedMunicipalityId"
            id="municipality_id_edit"
            :options="municipalitiesByDepartment"
            :disabled="!selectedDepartmentId || loadingMunicipalities || initialLoading"
            placeholder="Seleccione un municipio"
          />
          <div v-if="loadingMunicipalities" class="text-xs text-gray-500 mt-1">Cargando municipios...</div>
          <div v-if="selectedDepartmentId && municipalitiesByDepartment.length === 0 && !loadingMunicipalities && !initialLoading && !loadingDepartments" class="text-xs text-gray-500 mt-1">
            No hay municipios para este departamento.
          </div>
        </FormField>

        <FormField label="Distrito" required>
          <FormControl
            v-model="form.district_id"
            id="district_id_edit"
            :options="districtsByMunicipality"
            :disabled="!selectedMunicipalityId || loadingDistricts || initialLoading"
            placeholder="Seleccione un distrito"
          />
          <div v-if="loadingDistricts" class="text-xs text-gray-500 mt-1">Cargando distritos...</div>
           <div v-if="selectedMunicipalityId && districtsByMunicipality.length === 0 && !loadingDistricts && !initialLoading && !loadingMunicipalities" class="text-xs text-gray-500 mt-1">
            No hay distritos para este municipio.
          </div>
        </FormField>

        <FormField label="Dirección Completa" class="md:col-span-2" required>
          <FormControl
            v-model="form.address"
            id="address"
            type="textarea"
            placeholder="Escriba la dirección completa de la sucursal..."
          />
        </FormField>
      </div>

      <template #footer>
        <BaseButtons>
          <BaseButton
            color="info"
            type="submit"
            :disabled="loading || initialLoading"
            :label="loading ? 'Actualizando...' : 'Actualizar Sucursal'"
          />
          <BaseButton color="whiteDark" label="Cancelar" @click="cancelForm" outline :disabled="initialLoading" />
        </BaseButtons>
      </template>
    </CardBox>
     <CardBox v-else-if="initialLoading" style="margin: 1rem;" class="text-center p-6">
      <p>Cargando datos de la sucursal...</p>
    </CardBox>
    <CardBox v-else style="margin: 1rem;" class="text-center p-6">
        <p class="text-red-500">No se pudieron cargar los datos de la sucursal o la sucursal no existe.</p>
         <BaseButton
            :to="{ name: 'branches' }"
            :icon="mdiArrowLeftCircle"
            label="Volver a la lista"
            color="contrast"
            rounded-full
            small
            class="mt-4"
        />
    </CardBox>
  </LayoutAuthenticated>
</template>