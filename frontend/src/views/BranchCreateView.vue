<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { mdiArrowLeftCircle, mdiPlus } from '@mdi/js';
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

const router = useRouter();
const mainStore = useMainStore();
const token = localStorage.getItem('autorent_leon_token');

const loading = ref(false);
const loadingDepartments = ref(false);
const loadingMunicipalities = ref(false);
const loadingDistricts = ref(false);

// Refs para dropdowns
const departments = ref([]);
const selectedDepartmentId = ref(null);
const municipalitiesByDepartment = ref([]);
const selectedMunicipalityId = ref(null);
const districtsByMunicipality = ref([]);

const form = ref({
  name: '',
  phone: '',
  address: '',
  email: '',
  district_id: null,
});

const pageTitle = computed(() => 'Crear Nueva Sucursal');
const API_URL = import.meta.env.VITE_API_URL;

const fetchDepartments = async () => {
  if (!token) return;
  loadingDepartments.value = true;
  try {
    const config = { headers: { Authorization: `Bearer ${token}` } };
    const response = await axios.get(`${API_URL}department`, config);
    departments.value = response.data?.data?.map(dept => ({
      id: dept.id,
      label: dept.department || dept.department || 'Departamento Desconocido'
    })) || [];
  } catch (e) {
    console.error("Error fetching departments:", e);
    mainStore.notify({ color: 'danger', message: 'Error cargando departamentos: ' + (e.response?.data?.message || e.message) });
  } finally {
    loadingDepartments.value = false;
  }
};

const fetchMunicipalitiesForSelectedDepartment = async (departmentId) => {
  if (!token || !departmentId) {
    municipalitiesByDepartment.value = [];
    selectedMunicipalityId.value = null; // Resetea municipality si department cambia
    form.value.district_id = null; // lo mismo de arriba
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
  } catch (e) {
    console.error("Error fetching municipalities for department:", e);
    municipalitiesByDepartment.value = [];
    mainStore.notify({ color: 'danger', message: `Error cargando municipios: ${e.response?.data?.message || e.message}` });
  } finally {
    loadingMunicipalities.value = false;
  }
};

const fetchDistrictsForSelectedMunicipality = async (municipalityId) => {
  if (!token || !municipalityId) {
    districtsByMunicipality.value = [];
    form.value.district_id = null; // Lo mismo del reseteo si cambia
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
  } catch (e) {
    console.error("Error fetching districts for municipality:", e);
    districtsByMunicipality.value = [];
    mainStore.notify({ color: 'danger', message: `Error cargando distritos: ${e.response?.data?.message || e.message}` });
  } finally {
    loadingDistricts.value = false;
  }
};

watch(selectedDepartmentId, async (newDepartmentId) => {
  form.value.district_id = null;
  districtsByMunicipality.value = [];
  selectedMunicipalityId.value = null;
  municipalitiesByDepartment.value = [];
  if (newDepartmentId) {
    await fetchMunicipalitiesForSelectedDepartment(newDepartmentId);
  }
});

watch(selectedMunicipalityId, async (newMunicipalityId) => {
  form.value.district_id = null;
  districtsByMunicipality.value = [];
  if (newMunicipalityId) {
    await fetchDistrictsForSelectedMunicipality(newMunicipalityId);
  }
});

onMounted(async () => {
  await fetchDepartments();
  // Resetear formulario
  form.value = {
    name: '',
    phone: '',
    address: '',
    email: '',
    district_id: null,
  };
  selectedDepartmentId.value = null;
  selectedMunicipalityId.value = null;
  municipalitiesByDepartment.value = [];
  districtsByMunicipality.value = [];
});

const getAuthConfigJson = () => ({
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const handleSubmit = async () => {
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
    
    await axios.post(`${API_URL}branch`, payload, getAuthConfigJson());
    mainStore.notify({ color: 'success', message: 'Sucursal creada exitosamente.' });
    router.push({ name: 'branches' });
  } catch (e) {
    console.error('Error creando sucursal:', e);
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
            backendError.details[field].forEach(errObj => {
              let fieldNameDisplay = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ');
              if (field === 'district') fieldNameDisplay = 'Distrito';
              messagesToShow.push(`- ${fieldNameDisplay}: ${errObj.message}`);
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

    <SectionTitleLineWithButton :icon="mdiPlus" :title="pageTitle" main style="margin: 2rem;">
      <BaseButton
        :to="{ name: 'branches' }"
        :icon="mdiArrowLeftCircle"
        label="Volver a la lista"
        color="contrast"
        rounded-full
        small
      />
    </SectionTitleLineWithButton>
    <CardBox is-form @submit.prevent="handleSubmit" style="margin: 2rem;">
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
            id="department_id"
            :options="departments"
            :disabled="loadingDepartments"
            placeholder="Seleccione un departamento"
          />
           <div v-if="loadingDepartments" class="text-xs text-gray-500 mt-1">Cargando departamentos...</div>
        </FormField>

        <FormField label="Municipio" required>
          <FormControl
            v-model="selectedMunicipalityId"
            id="municipality_id"
            :options="municipalitiesByDepartment"
            :disabled="!selectedDepartmentId || municipalitiesByDepartment.length === 0 || loadingMunicipalities"
            placeholder="Seleccione un municipio"
          />
          <div v-if="loadingMunicipalities" class="text-xs text-gray-500 mt-1">Cargando municipios...</div>
          <div v-if="selectedDepartmentId && municipalitiesByDepartment.length === 0 && !loadingMunicipalities && !loadingDepartments" class="text-xs text-gray-500 mt-1">
            No hay municipios para este departamento o seleccione un departamento primero.
          </div>
        </FormField>

        <FormField label="Distrito" required>
          <FormControl
            v-model="form.district_id"
            id="district_id"
            :options="districtsByMunicipality"
            :disabled="!selectedMunicipalityId || districtsByMunicipality.length === 0 || loadingDistricts"
            placeholder="Seleccione un distrito"
          />
          <div v-if="loadingDistricts" class="text-xs text-gray-500 mt-1">Cargando distritos...</div>
           <div v-if="selectedMunicipalityId && districtsByMunicipality.length === 0 && !loadingDistricts && !loadingMunicipalities" class="text-xs text-gray-500 mt-1">
            No hay distritos para este municipio o seleccione un municipio primero.
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
            :disabled="loading"
            :label="loading ? 'Creando...' : 'Crear Sucursal'"
          />
          <BaseButton color="whiteDark" label="Cancelar" @click="cancelForm" outline />
        </BaseButtons>
      </template>
    </CardBox>
  </LayoutAuthenticated>
</template>