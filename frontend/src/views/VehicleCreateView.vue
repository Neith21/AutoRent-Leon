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

const getObjectURL = (file) => {
  if (file instanceof File) {
    return URL.createObjectURL(file);
  }
  return '';
};

const router = useRouter();
const mainStore = useMainStore();
const token = localStorage.getItem('autorent_leon_token');

const loading = ref(false);

// Refs para dropdowns
const brands = ref([]);
const selectedBrandId = ref(null);
const modelsByBrand = ref([]);
const vehicleCategories = ref([]);

const engineTypeOptions = ref([
  { id: 'Gasolina', label: 'Gasolina' },
  { id: 'Diesel', label: 'Diesel' },
  { id: 'Eléctrico', label: 'Eléctrico' },
  { id: 'Híbrido', label: 'Híbrido' }
]);

const statusOptions = ref([
  { id: 'Disponible', label: 'Disponible' },
  { id: 'Alquilado', label: 'Alquilado' },
  { id: 'Mantenimiento', label: 'Mantenimiento' },
  { id: 'Fuera de servicio', label: 'Fuera de servicio' }
]);

const form = ref({
  plate: '',
  vehiclemodel_id: null,
  vehiclecategory_id: null,
  color: '',
  year: new Date().getFullYear(),
  engine: '',
  engine_type: 'Gasolina',
  engine_number: '',
  vin: '',
  seat_count: 4,
  description: '',
  status: 'Disponible',
  images: [] // Para las imágenes a subir
});

const pageTitle = computed(() => 'Crear Nuevo Vehículo');
const API_URL = import.meta.env.VITE_API_URL;

// --- Funciones para cargar datos de dropdowns ---
const fetchBrands = async () => {
  if (!token) return;
  loading.value = true;
  try {
    const config = { headers: { Authorization: `Bearer ${token}` } };
    const response = await axios.get(`${API_URL}brand`, config);
    brands.value = response.data?.data?.map(brand => ({
      id: brand.id,
      label: brand.name || 'Marca Desconocida'
    })) || [];
  } catch (e) {
    console.error("Error fetching brands:", e);
    mainStore.notify({ color: 'danger', message: 'Error cargando marcas.' });
  } finally {
    loading.value = false;
  }
};

const fetchModelsForSelectedBrand = async (brandId) => {
  if (!token || !brandId) {
    modelsByBrand.value = [];
    return;
  }
  loading.value = true;
  try {
    const config = { headers: { Authorization: `Bearer ${token}` } };
    const response = await axios.get(`${API_URL}vehicle/models/${brandId}`, config);
    modelsByBrand.value = response.data?.data?.map(model => ({
      id: model.id,
      label: model.name || 'Modelo Desconocido'
    })) || [];
  } catch (e) {
    console.error("Error fetching models for brand:", e);
    modelsByBrand.value = [];
    mainStore.notify({ color: 'danger', message: `Error cargando modelos para la marca: ${e.response?.data?.message || e.message}` });
  } finally {
    loading.value = false;
  }
};

const fetchVehicleCategories = async () => {
  if (!token) return;
  try {
    const config = { headers: { Authorization: `Bearer ${token}` } };
    const response = await axios.get(`${API_URL}vehiclecategory`, config);
    vehicleCategories.value = response.data?.data?.map(category => ({
      id: category.id,
      label: category.name || 'Categoría Desconocida'
    })) || [];
  } catch (e) {
    console.error("Error fetching vehicle categories:", e);
    mainStore.notify({ color: 'danger', message: 'Error cargando categorías de vehículo.' });
  }
};

watch(selectedBrandId, async (newBrandId, oldBrandId) => {
  if (newBrandId !== oldBrandId) {
    form.value.vehiclemodel_id = null;
    modelsByBrand.value = [];
  }
  if (newBrandId) {
    await fetchModelsForSelectedBrand(newBrandId);
  } else {
    modelsByBrand.value = [];
  }
});

onMounted(async () => {
  await fetchBrands();
  await fetchVehicleCategories();
  form.value.id = null;
  selectedBrandId.value = null;
  modelsByBrand.value = [];
  form.value.images = [];
});

const handleImageFiles = (event) => {
  const selectedFiles = Array.from(event.target.files);
  const allowedTypes = ['image/png', 'image/jpeg'];
  const validFiles = [];
  const invalidFileNames = [];

  selectedFiles.forEach(file => {
    if (allowedTypes.includes(file.type)) {
      validFiles.push(file);
    } else {
      invalidFileNames.push(file.name);
    }
  });

  if (invalidFileNames.length > 0) {
    mainStore.notify({
      color: 'warning',
      message: `Archivos no válidos (solo PNG/JPEG): ${invalidFileNames.join(', ')}. No serán añadidos.`
    });
  }

  form.value.images = validFiles;

  if (form.value.images.length > 6) {
    mainStore.notify({ color: 'warning', message: 'Solo se permiten un máximo de 6 imágenes. Se tomarán las primeras 6.' });
    form.value.images = form.value.images.slice(0, 6);
  }
};

const getAuthConfigMultiPart = () => ({
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'multipart/form-data'
  }
});

const handleSubmit = async () => {
  loading.value = true;

  const requiredFields = {
    plate: 'Placa',
    selectedBrandId: 'Marca',
    vehiclemodel_id: 'Modelo',
    vehiclecategory_id: 'Categoría',
    color: 'Color',
    year: 'Año',
    engine: 'Motor (C.C.)',
    engine_type: 'Tipo de Motor',
    engine_number: 'Número de Motor',
    vin: 'VIN',
    seat_count: 'N° de Asientos',
    status: 'Estado'
  };

  for (const fieldKey in requiredFields) {
    const valueToTest = fieldKey === 'selectedBrandId' ? selectedBrandId.value : form.value[fieldKey];
    if (valueToTest === null || valueToTest === '' || valueToTest === undefined) {
      mainStore.notify({ color: 'danger', message: `El campo '${requiredFields[fieldKey]}' es requerido.` });
      loading.value = false;
      return;
    }
  }

  // Validación de imagen obligatoria
  if (form.value.images.length === 0) {
    mainStore.notify({ color: 'danger', message: 'Debe subir al menos una imagen para el vehículo.' });
    loading.value = false;
    return;
  }

  // Preparar FormData para la creación
  const formData = new FormData();
  Object.keys(form.value).forEach(key => {
    if (key !== 'id' && key !== 'images' && form.value[key] !== null && form.value[key] !== undefined) {
      formData.append(key, form.value[key]);
    }
  });

  if (form.value.images.length > 0) {
    form.value.images.forEach(file => {
      formData.append('images', file); // El backend espera 'images' como una lista de archivos
    });
  }

  console.log('FormData a enviar (CREATE):');
  for (let pair of formData.entries()) {
    console.log(pair[0] + ': ' + pair[1]);
  }

  try {
    await axios.post(`${API_URL}vehicle`, formData, getAuthConfigMultiPart());
    mainStore.notify({ color: 'success', message: 'Vehículo creado exitosamente.' });
    router.push({ name: 'vehicles' });
  } catch (e) {
    console.error('Error creando vehículo:', e);
    let errorTitleForNotification = 'Error de Validación';
    let messagesToShow = [];
    const errorColor = 'danger';

    if (e.response && e.response.data) {
      console.error('Detalles del error del backend:', e.response.data);

      if (e.response.data.mensaje && e.response.data.mensaje !== "Datos inválidos. Por favor, corrija los errores.") {
        messagesToShow.push(e.response.data.mensaje);
      } else if (e.response.data.message && e.response.data.message !== "Datos inválidos. Por favor, corrija los errores.") {
        messagesToShow.push(e.response.data.message);
      }

      if (e.response.data.detalles && typeof e.response.data.detalles === 'object') {
        for (const field in e.response.data.detalles) {
          if (Array.isArray(e.response.data.detalles[field])) {
            e.response.data.detalles[field].forEach(errObj => {
              let fieldNameDisplay = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ');
              messagesToShow.push(`- ${fieldNameDisplay}: ${errObj.message}`);
            });
          }
        }
      }

      if (messagesToShow.length === 0 && (e.response.data.message || e.response.data.detail)) {
        messagesToShow.push(e.response.data.message || e.response.data.detail);
      }

    } else if (e.message) {
      messagesToShow.push(e.message);
      errorTitleForNotification = 'Error de Conexión';
    }

    if (messagesToShow.length === 0) {
      messagesToShow.push('Ha ocurrido un error inesperado. Intente de nuevo.');
    }
    const finalFormattedMessage = messagesToShow.join('\n');
    mainStore.notify({
      color: errorColor,
      message: finalFormattedMessage,
    });

  } finally {
    loading.value = false;
  }
};

const cancelForm = () => {
  router.push({ name: 'vehicles' });
};

</script>

<template>
  <LayoutAuthenticated>
    <div v-if="mainStore && mainStore.notification" class="sticky top-0 z-40 px-4 md:px-6">
      <NotificationBar v-model="mainStore.notification.show" :color="mainStore.notification.color"
        :icon="mainStore.notification.icon" class="mt-2">
        {{ mainStore.notification.message }}
      </NotificationBar>
    </div>
    <div v-else-if="mainStore && !mainStore.notification">
      <p class="text-red-500 p-4">Error: mainStore.notification no está definido.</p>
    </div>
    <div v-else>
      <p class="text-red-500 p-4">Error: mainStore no está disponible.</p>
    </div>
    <SectionTitleLineWithButton :icon="mdiPlus" :title="pageTitle" main style="margin: 1rem;">
      <BaseButton :to="{ name: 'vehicles' }" :icon="mdiArrowLeftCircle" label="Volver a la lista" color="contrast"
        rounded-full small />
    </SectionTitleLineWithButton>
    <CardBox is-form @submit.prevent="handleSubmit" style="margin: 1rem;">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField label="Placa">
          <FormControl v-model="form.plate" id="plate" required placeholder="Ej: P123XYZ" />
        </FormField>

        <FormField label="Marca">
          <FormControl v-model="selectedBrandId" id="brand_id" :options="brands" required
            placeholder="Seleccione una marca" />
        </FormField>

        <FormField label="Modelo">
          <FormControl v-model="form.vehiclemodel_id" id="vehiclemodel_id" :options="modelsByBrand"
            :disabled="!selectedBrandId || modelsByBrand.length === 0" required placeholder="Seleccione un modelo" />
          <div v-if="selectedBrandId && modelsByBrand.length === 0 && !loading && brands.length > 0"
            class="text-xs text-gray-500 mt-1">
            No hay modelos para esta marca o seleccione una marca primero.
          </div>
        </FormField>

        <FormField label="Categoría">
          <FormControl v-model="form.vehiclecategory_id" id="vehiclecategory_id" :options="vehicleCategories"
            required />
        </FormField>
        <FormField label="Color">
          <FormControl v-model="form.color" id="color" required placeholder="Ej: Rojo" />
        </FormField>
        <FormField label="Año">
          <FormControl v-model="form.year" id="year" type="number" required :min="1900"
            :max="new Date().getFullYear() + 1" />
        </FormField>
        <FormField label="Motor (C.C.)">
          <FormControl v-model="form.engine" id="engine" required placeholder="Ej: 1600" />
        </FormField>

        <FormField label="Tipo de Motor">
          <FormControl v-model="form.engine_type" id="engine_type" :options="engineTypeOptions" required />
        </FormField>

        <FormField label="Número de Motor">
          <FormControl v-model="form.engine_number" id="engine_number" required />
        </FormField>
        <FormField label="VIN">
          <FormControl v-model="form.vin" id="vin" required />
        </FormField>
        <FormField label="N° de Asientos">
          <FormControl v-model="form.seat_count" id="seat_count" type="number" required :min="1" />
        </FormField>

        <FormField label="Estado">
          <FormControl v-model="form.status" id="status" :options="statusOptions" required />
        </FormField>

        <FormField label="Descripción" class="md:col-span-2">
          <FormControl v-model="form.description" id="description" type="textarea"
            placeholder="Detalles adicionales del vehículo..." />
        </FormField>

        <FormField label="Imágenes (Máx. 6, al menos 1 obligatoria)" class="md:col-span-2">
          <FormControl id="images" type="file" multiple @change="handleImageFiles" accept="image/png, image/jpeg"
            required />
          <div class="mt-2 text-xs text-gray-500">Solo archivos PNG o JPEG.</div>
          <div v-if="form.images.length > 0"
            class="mt-2 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
            <div v-for="(file, index) in form.images" :key="index" class="h-24 border rounded overflow-hidden relative">
              <img :src="getObjectURL(file)" class="w-full h-full object-cover" :alt="file.name">
            </div>
          </div>
        </FormField>
      </div>

      <template #footer>
        <BaseButtons>
          <BaseButton color="info" type="submit" :disabled="loading"
            :label="loading ? 'Creando...' : 'Crear Vehículo'" />
          <BaseButton color="whiteDark" label="Cancelar" @click="cancelForm" outline />
        </BaseButtons>
      </template>
    </CardBox>
  </LayoutAuthenticated>
</template>