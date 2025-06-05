<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import LayoutGuest from '@/layouts/LayoutGuest.vue';
import { Form, Field, ErrorMessage } from 'vee-validate';
import { loginSchema } from '@/schemas/loginValidationsSchema';
import { loginComposable } from '@/composables/useUserControlComposable';

const router = useRouter();

const email = ref('');
const password = ref('');

const showButton = ref(true);
const backendErrorMessage = ref('');

const { sendData } = loginComposable();

const handleLogin = async () => {
  backendErrorMessage.value = ''; 
  showButton.value = false;

  const result = await sendData({
    email: email.value,
    password: password.value,
  });

  if (!result.success) {
    backendErrorMessage.value = result.message;
    showButton.value = true;
  } else {
    // El composable ya maneja la redirección
  }
};
</script>

<template>
  <LayoutGuest>
    <div class="SectionFullScreen">
      <div class="card-box">
        <h2 class="text-center mb-4">Iniciar Sesión</h2>

        <div v-if="backendErrorMessage" class="alert alert-danger text-center mb-3">
          {{ backendErrorMessage }}
        </div>

        <Form :validation-schema="loginSchema" @submit="handleLogin">
          <div class="mb-4">
            <label for="login-email" class="form-label">Correo Electrónico</label>
            <Field
              type="email"
              v-model="email"
              name="email"
              id="login-email"
              class="form-control"
              placeholder="correo@ejemplo.com"
            />
            <ErrorMessage name="email" class="text-danger-frontend" />
          </div>

          <div class="mb-4">
            <label for="login-password" class="form-label">Contraseña</label>
            <Field
              type="password"
              v-model="password"
              name="password"
              id="login-password"
              class="form-control"
              placeholder="Contraseña"
            />
            <ErrorMessage name="password" class="text-danger-frontend" />
          </div>

          <div v-if="showButton" class="text-center">
            <button type="submit" class="btn" title="Iniciar Sesión">
              Iniciar Sesión
            </button>
          </div>

          <div v-else class="text-center mt-4">
            <center><img src="/img/load.gif" alt="Cargando..." width="40" /></center>
          </div>

          <div class="text-center mt-4">
            <p>¿No tienes cuenta? <a @click.prevent="router.push('/register')" href="/autorent-leon/#/register">Regístrate</a></p>
          </div>
        </Form>
      </div>
    </div>
  </LayoutGuest>
</template>

<style scoped>
/* Fondo con gradiente (Login) */
.SectionFullScreen {
  background: linear-gradient(135deg, #ff416c, #ff4b2b);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 1rem; /* Espacio por si el contenido es muy grande en pantallas pequeñas */
}

/* Tarjeta del formulario */
.card-box {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  max-width: 420px;
  width: 100%;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}

/* Input */
.form-control {
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #ced4da;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-control:focus {
  border-color: #ff416c;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(255, 65, 108, 0.25);
}


/* Botón */
.btn {
  background-color: #ff416c;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out, transform 0.1s ease;
  font-size: 1rem;
  font-weight: 500;
}

.btn:hover {
  background-color: #ff4b2b;
  transform: translateY(-2px);
}

.btn:active {
  transform: translateY(0);
}

.text-danger-frontend {
  font-size: 0.875em;
  color: #dc3545;
  display: block;
  margin-top: 0.25rem;
}

.alert.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  font-size: 0.9rem;
}

a {
  color: #ff416c;
  text-decoration: none;
  font-weight: 500;
}

a:hover {
  text-decoration: underline;
  color: #ff4b2b;
}

h2 {
  color: #333;
  font-weight: 600;
}

.text-center img[alt="Cargando..."] {
  margin-top: 1rem;
}
</style>