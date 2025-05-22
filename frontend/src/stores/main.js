import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { jwtDecode } from "jwt-decode";

// import { useToast } from 'vue-toastification';

export const useMainStore = defineStore('main', () => {
  const userName = ref('');
  const userLastName = ref('');
  const userEmail = ref('');

  const notification = ref({
    show: false,
    message: '',
    color: 'info',
    icon: null,
    timeoutId: null,
  });

  const token = localStorage.getItem('autorent_leon_token');

  if (token) {
    try {
      const decoded = jwtDecode(token);
      userName.value = decoded.name || '';
      userLastName.value = decoded.last_name || '';
      userEmail.value = decoded.email || '';
    } catch (error) {
      console.error('Error decoding JWT token:', error);
    }
  }

  const userAvatar = computed(
    () =>
      `https://api.dicebear.com/7.x/avataaars/svg?seed=${userEmail.value.replace(
        /[^a-z0-9]+/gi,
        '-',
      )}`,
  )

  const isFieldFocusRegistered = ref(false)

  const clients = ref([])
  const history = ref([])

  function setUser(payload) {
    if (payload.name) {
      userName.value = payload.name
    }
    if (payload.last_name) {
      userLastName.value = payload.last_name
    }
    if (payload.email) {
      userEmail.value = payload.email
    }
  }

  function fetchSampleClients() {
    axios
      .get(`data-sources/clients.json?v=3`)
      .then((result) => {
        clients.value = result?.data?.data
      })
      .catch((error) => {
        notify({ message: `Error cargando clientes: ${error.message}`, color: 'danger' });
      })
  }

  function fetchSampleHistory() {
    axios
      .get(`data-sources/history.json`)
      .then((result) => {
        history.value = result?.data?.data
      })
      .catch((error) => {
        notify({ message: `Error cargando historial: ${error.message}`, color: 'danger' });
        // alert(error.message)
      })
  }

  /**
   * Muestra una notificación al usuariu
   * @param {object} options - Opciones de la notificación
   * @param {string} options.message - El mensaje a mostrar
   * @param {string} [options.color='info'] - El color/tipo de la notificación
   * @param {string|null} [options.icon=null] - El ícono para la notificación
   * @param {number} [options.duration=3000] - Duración en ms. 0 para persistente
   */
  function notify({ message, color = 'info', icon = null, duration = 3000 }) { // Duración con 3 segundos quedamossss
    if (notification.value.timeoutId) {
      clearTimeout(notification.value.timeoutId);
      notification.value.timeoutId = null;
    }

    notification.value.message = message;
    notification.value.color = color;
    notification.value.icon = icon;
    notification.value.show = true;

    if (duration > 0) {
      notification.value.timeoutId = setTimeout(() => {
        dismissNotification();
      }, duration);
    }
  }

  function dismissNotification() {
    notification.value.show = false;
    if (notification.value.timeoutId) {
      clearTimeout(notification.value.timeoutId);
      notification.value.timeoutId = null;
    }
  }

  return {
    userName,
    userLastName,
    userEmail,
    userAvatar,
    isFieldFocusRegistered,
    clients,
    history,
    setUser,
    fetchSampleClients,
    fetchSampleHistory,

    notification,
    notify,
    dismissNotification,
  }
})