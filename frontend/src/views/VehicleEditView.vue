<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { mdiArrowLeftCircle, mdiPencil, mdiTrashCan, mdiUpload } from '@mdi/js';
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
const imageUploading = ref(false);
const imageDeletingId = ref(null);
const vehicleId = ref(null);

const brands = ref([]);
const selectedBrandId = ref(null);
const modelsByBrand = ref([]);
const vehicleCategories = ref([]);
const currentVehicleImages = ref([]);
const newSelectedImages = ref([]);

const engineTypeOptions = ref([
  { id: 'Gasolina', label: 'Gasolina' },
  { id: 'Diesel', label: 'Diesel' },
  { id: 'Eléctrico', label: 'Eléctrico' },
  { id: 'Híbrido', label: 'Híbrido' }
]);

const statusOptions = ref([
  { id: 'Disponible', label: 'Disponible' },
  { id: 'Alquilado', label: 'Alquilado' },
  { id: 'En mantenimiento', label: 'En mantenimiento' },
  { id: 'Fuera de servicio', label: 'Fuera de servicio' },
  { id: 'Reservado', label: 'Reservado' }
]);

const form = ref({
  id: null,
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
});

const pageTitle = computed(() => 'Editar Vehículo');
const API_URL = import.meta.env.VITE_API_URL;

const getObjectURL = (file) => {
  if (file instanceof File) {
    return URL.createObjectURL(file);
  }
  return '';
};

const fetchBrands = async () => {
  if (!token) return;
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
    console.error("Error fetching models for brand:", brandId, e);
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

  const wasMeaningfulOldBrand = oldBrandId !== null && oldBrandId !== undefined;

  if (wasMeaningfulOldBrand && newBrandId !== oldBrandId) {
    form.value.vehiclemodel_id = null;
  }
  if (newBrandId) {
    await fetchModelsForSelectedBrand(newBrandId);
  } else {
    modelsByBrand.value = [];
    form.value.vehiclemodel_id = null;
  }
});

const fetchVehicleData = async (id) => {
  try {
    const config = { headers: { 'Authorization': `Bearer ${token}` } };
    const response = await axios.get(`${API_URL}vehicle/${id}`, config);
    const vehicle = response.data?.data;

    if (vehicle) {
      form.value = {
        id: vehicle.id,
        plate: vehicle.plate,
        vehiclemodel_id: vehicle.vehiclemodel?.id || null,
        vehiclecategory_id: vehicle.vehiclecategory?.id || null,
        color: vehicle.color,
        year: vehicle.year,
        engine: vehicle.engine,
        engine_type: vehicle.engine_type,
        engine_number: vehicle.engine_number,
        vin: vehicle.vin,
        seat_count: vehicle.seat_count,
        description: vehicle.description,
        status: vehicle.status,
      };

      currentVehicleImages.value = vehicle.images || [];
      newSelectedImages.value = [];

      if (vehicle.vehiclemodel && vehicle.vehiclemodel.brand && vehicle.vehiclemodel.brand.id) {
        selectedBrandId.value = vehicle.vehiclemodel.brand.id;
      } else if (vehicle.vehiclemodel?.id) {
        console.warn("API did not provide vehicle.vehiclemodel.brand.id. Cannot pre-select brand or auto-load models.");
      } else {
        console.warn("No vehicle model or brand information available from API to pre-select.");
      }
    } else {
      throw new Error('Vehículo no encontrado');
    }
  } catch (e) {
    console.error('Error obteniendo datos del vehículo:', e);
    mainStore.notify({ color: 'danger', message: 'Error cargando datos del vehículo: ' + (e.response?.data?.message || e.message) });
    router.push({ name: 'vehicles' });
  }
};

onMounted(async () => {
  if (route.params.id) {
    vehicleId.value = route.params.id;
    loading.value = true;
    try {
      await fetchBrands();
      await fetchVehicleCategories();
      await fetchVehicleData(vehicleId.value);
    } catch (error) {
      console.error("Error in onMounted initial data load:", error);
      mainStore.notify({ color: 'danger', message: 'Error crítico cargando datos para edición.' });
    } finally {
      loading.value = false;
    }
  } else {
    mainStore.notify({ color: 'danger', message: 'No se especificó un ID de vehículo para editar.' });
    router.push({ name: 'vehicles' });
  }
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
  newSelectedImages.value = validFiles;

  if (newSelectedImages.value.length > 6) {
    mainStore.notify({ color: 'warning', message: 'Solo se permiten un máximo de 6 imágenes nuevas a la vez. Se tomarán las primeras 6.' });
    newSelectedImages.value = newSelectedImages.value.slice(0, 6);
  }
  if (event.target) {
    event.target.value = null;
  }
};

const handleSubmit = async () => {
  loading.value = true;

  const requiredFields = {
    plate: 'Placa', selectedBrandId: 'Marca', vehiclemodel_id: 'Modelo',
    vehiclecategory_id: 'Categoría', color: 'Color', year: 'Año',
    engine: 'Motor (C.C.)', engine_type: 'Tipo de Motor', engine_number: 'Número de Motor',
    vin: 'VIN', seat_count: 'N° de Asientos', status: 'Estado'
  };

  const payload = { ...form.value };
  delete payload.id;

  console.log('Payload a enviar (PUT):', payload);

  try {
    await axios.put(`${API_URL}vehicle/${vehicleId.value}`, payload, { headers: { 'Authorization': `Bearer ${token}` } });
    mainStore.notify({ color: 'success', message: 'Vehículo actualizado exitosamente.' });
    router.push({ name: 'vehicles' });
  } catch (e) {
    console.error('Error actualizando/creando vehículo:', e); // Mensaje genérico
    let errorTitleForNotification = 'Error de Validación';
    let messagesToShow = [];
    const errorColor = 'danger';

    if (e.response && e.response.data) {
      console.error('Detalles del error del backend:', e.response.data);

      const backendMainMessage = e.response.data.mensaje || e.response.data.message;
      if (backendMainMessage && backendMainMessage.toLowerCase() !== "datos inválidos. por favor, corrija los errores.") {
        messagesToShow.push(backendMainMessage);
      } else if (e.response.data.detail) {
        messagesToShow.push(e.response.data.detail);
      }

      if (e.response.data.detalles && typeof e.response.data.detalles === 'object') {
        for (const field in e.response.data.detalles) {
          if (Array.isArray(e.response.data.detalles[field])) {
            e.response.data.detalles[field].forEach(errorItem => { // 'errorItem' puede ser un string o un objeto
              let messageText = '';
              if (typeof errorItem === 'string') {
                // CASO 1: El error es directamente un string
                messageText = errorItem;
              } else if (errorItem && typeof errorItem.message === 'string') {
                // CASO 2: El error es un objeto con una propiedad 'message'
                messageText = errorItem.message;
              } else {
                messageText = 'Error no especificado para este campo.';
                console.warn(`Estructura de error inesperada para el campo ${field}:`, errorItem);
              }

              let fieldNameDisplay = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ');
              messagesToShow.push(`- ${fieldNameDisplay}: ${messageText}`);
            });
          }
        }
      }

      if (messagesToShow.length === 0 && (e.response.data.message || e.response.data.detail)) {
        messagesToShow.push(e.response.data.message || e.response.data.detail || "Error procesando la solicitud.");
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

const maxImages = 6;
const canUploadMoreImages = computed(() => currentVehicleImages.value.length < maxImages);

const handleUploadNewImages = async () => {
  if (newSelectedImages.value.length === 0) {
    mainStore.notify({ color: 'info', message: 'No hay nuevas imágenes seleccionadas para subir.' });
    return;
  }
  const slotsAvailable = maxImages - currentVehicleImages.value.length;
  if (newSelectedImages.value.length > slotsAvailable) {
    mainStore.notify({ color: 'warning', message: `Solo puede añadir ${slotsAvailable} imagen(es) más. Ya tiene ${currentVehicleImages.value.length}.` });
    return;
  }

  imageUploading.value = true;
  const formData = new FormData();
  newSelectedImages.value.forEach(file => {
    formData.append('images', file);
  });

  try {
    const config = { headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'multipart/form-data' } };
    const response = await axios.post(`${API_URL}vehicleimage/${vehicleId.value}`, formData, config);

    if (response.data && response.data.added_images) {
      currentVehicleImages.value.push(...response.data.added_images);
    }
    mainStore.notify({ color: 'success', message: 'Nuevas imágenes subidas exitosamente.' });
    newSelectedImages.value = []; // Limpiar selección
  } catch (e) {
    console.error('Error subiendo nuevas imágenes:', e);
    mainStore.notify({ color: 'danger', message: `Error subiendo imágenes: ${e.response?.data?.message || e.response?.data?.mensaje || e.message}` });
  } finally {
    imageUploading.value = false;
  }
};

const handleDeleteImage = async (imageId) => {
  if (!confirm('¿Está seguro de que desea eliminar esta imagen?')) return;

  imageDeletingId.value = imageId;
  try {
    const config = { headers: { 'Authorization': `Bearer ${token}` } };
    await axios.delete(`${API_URL}vehicleimage/${imageId}`, config);
    currentVehicleImages.value = currentVehicleImages.value.filter(img => img.id !== imageId);
    mainStore.notify({ color: 'success', message: 'Imagen eliminada exitosamente.' });
  } catch (e) {
    console.error('Error eliminando imagen:', e);
    mainStore.notify({ color: 'danger', message: `Error eliminando imagen: ${e.response?.data?.message || e.response?.data?.mensaje || e.message}` });
  } finally {
    imageDeletingId.value = null;
  }
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
    <SectionTitleLineWithButton :icon="mdiPencil" :title="pageTitle" main style="margin: 1rem;">
      <BaseButton :to="{ name: 'vehicles' }" :icon="mdiArrowLeftCircle" label="Volver a la lista" color="contrast"
        rounded-full small />
    </SectionTitleLineWithButton>
    <CardBox class="mb-6" is-form @submit.prevent="handleSubmit" style="margin: 1rem;">
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
      </div>

      <template #footer>
        <BaseButtons>
          <BaseButton color="info" type="submit" :disabled="loading"
            :label="loading ? 'Actualizando Datos...' : 'Guardar Cambios de Datos'" />
          <BaseButton color="whiteDark" label="Cancelar" @click="cancelForm" outline />
        </BaseButtons>
      </template>
    </CardBox>

    <SectionTitleLineWithButton :icon="mdiPencil" title="Gestionar Imágenes del Vehículo" class="mt-8" />
    <CardBox class="mb-6">
      <FormField label="Imágenes Actuales" v-if="currentVehicleImages.length > 0">
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 mt-2">
          <div v-for="image in currentVehicleImages" :key="image.id"
            class="h-32 border rounded overflow-hidden relative group">
            <img :src="image.url" class="w-full h-full object-cover" alt="Imagen actual del vehículo">
            <BaseButton color="danger" :icon="mdiTrashCan" small rounded-full
              class="absolute top-1 right-1 opacity-50 group-hover:opacity-100 transition-opacity z-10"
              title="Eliminar Imagen" :disabled="imageDeletingId === image.id" :loading="imageDeletingId === image.id"
              @click="handleDeleteImage(image.id)" />
          </div>
        </div>
      </FormField>
      <div v-else class="text-gray-500 italic py-4">Este vehículo no tiene imágenes actualmente.</div>

      <FormField label="Añadir Nuevas Imágenes" class="mt-6" v-if="canUploadMoreImages">
        <FormControl id="new_vehicle_images_input" type="file" multiple @change="handleImageFiles"
          accept="image/png, image/jpeg" :disabled="imageUploading || !canUploadMoreImages" />
        <div class="mt-1 text-xs text-gray-500">
          Solo PNG o JPEG. Límite total de {{ maxImages }} imágenes.
          ({{ Math.max(0, maxImages - currentVehicleImages.length) }} ranura(s) disponible(s)).
        </div>

        <div v-if="newSelectedImages.length > 0" class="mt-4">
          <h4 class="text-sm font-semibold mb-2">Previsualización de imágenes a subir:</h4>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
            <div v-for="(file, index) in newSelectedImages" :key="index"
              class="h-24 border rounded overflow-hidden relative">
              <img :src="getObjectURL(file)" class="w-full h-full object-cover" :alt="file.name">
            </div>
          </div>
          <BaseButton color="success" label="Subir Imágenes Seleccionadas" :icon="mdiUpload" class="mt-3"
            :disabled="imageUploading || newSelectedImages.length === 0" :loading="imageUploading"
            @click="handleUploadNewImages" />
        </div>
      </FormField>
      <div v-else-if="currentVehicleImages.length >= maxImages" class="mt-6 text-sm text-orange-600 py-4">
        Ha alcanzado el límite de {{ maxImages }} imágenes. Elimine alguna existente para poder añadir nuevas.
      </div>
    </CardBox>

  </LayoutAuthenticated>
</template>