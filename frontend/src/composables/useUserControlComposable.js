import { useAuthStore } from "@/stores/authStore";
import axios from "axios";
import { useRouter } from 'vue-router';

// Composable para el REGISTRO
export function registerComposable() {
  const router = useRouter();

  const sendData = async (userData) => {
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}user-control/register`, 
        userData, 
        { headers: { "Content-Type": "application/json" } }
      );

      if (response.data.status === "ok") {

        return { 
          success: true, 
          message: response.data.message || "Registro exitoso. Revisa tu correo para activar la cuenta." 
        };
      } else {
         return { 
          success: false, 
          message: response.data.message || "Ocurrió un error durante el registro." 
        };
      }
    } catch (error) {
      let errorMessage = "Ocurrió un error inesperado durante el registro.";
      if (error.response && error.response.data && error.response.data.message) {
        errorMessage = error.response.data.message;
      }
      return { success: false, message: errorMessage };
    }
  };

  return {
    sendData,
  };
}

// Composable para el LOGIN
export function loginComposable() {
  const router = useRouter();
  const store = useAuthStore();

  const sendData = async (credentials) => {
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}user-control/login`,
        credentials,
        { headers: { "Content-Type": "application/json" } }
      );

      if (response.data.status === "ok" && response.data.token) {
        store.initiateSession(response.data);

        setTimeout(() => {
          window.location.href = `${import.meta.env.VITE_BASE_URL}/autorent-leon/#/`; 
          setTimeout(() => window.location.reload(), 50);
        }, 100);
        
        return { success: true };
      } else {
         return { 
          success: false, 
          message: response.data.message || "Error en la respuesta del servidor." 
        };
      }
    } catch (error) {
      let errorMessage = "Credenciales inválidas o error inesperado.";
      if (error.response && error.response.data && error.response.data.message) {
        errorMessage = error.response.data.message;
      }
      return { success: false, message: errorMessage };
    }
  };

  return {
    sendData,
  };
}