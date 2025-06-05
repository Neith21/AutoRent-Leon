<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import LayoutGuest from '@/layouts/LayoutGuest.vue';
import { Form, Field, ErrorMessage } from 'vee-validate';
import { registerSchema } from '@/schemas/loginValidationsSchema'; 
import { registerComposable } from '@/composables/useUserControlComposable';

const router = useRouter();

const name = ref('');
const email = ref('');
const password = ref('');

const showButton = ref(true);
const backendErrorMessage = ref('');
const successMessage = ref('');

const { sendData } = registerComposable();

const handleRegister = async () => {
  backendErrorMessage.value = '';
  successMessage.value = '';
  showButton.value = false;

  const result = await sendData({
    name: name.value,
    email: email.value,
    password: password.value,
  });

  if (result.success) {
    successMessage.value = result.message;
    name.value = '';
    email.value = '';
    password.value = '';
    setTimeout(() => {
        if (successMessage.value) {
            router.push('/login');
        }
    }, 3000);
  } else {
    backendErrorMessage.value = result.message;
  }
  showButton.value = true;
};
</script>

<template>
  <LayoutGuest>
    <div class="SectionFullScreenRegister">
      <div class="card-box">
        <h2 class="text-center mb-4">Crear Cuenta</h2>

        <div v-if="backendErrorMessage" class="alert alert-danger text-center mb-3">
          {{ backendErrorMessage }}
        </div>
        <div v-if="successMessage" class="alert alert-success text-center mb-3">
          {{ successMessage }}
        </div>

        <Form :validation-schema="registerSchema" @submit="handleRegister">
          <div class="mb-4">
            <label for="register-name" class="form-label">Nombre Completo</label>
            <Field
              type="text"
              v-model="name"
              name="name"
              id="register-name"
              class="form-control"
              placeholder="Nombre Completo"
            />
            <ErrorMessage name="name" class="text-danger-frontend" />
          </div>

          <div class="mb-4">
            <label for="register-email" class="form-label">Correo Electrónico</label>
            <Field
              type="email"
              v-model="email"
              name="email"
              id="register-email"
              class="form-control"
              placeholder="correo@ejemplo.com"
            />
            <ErrorMessage name="email" class="text-danger-frontend" />
          </div>

          <div class="mb-4">
            <label for="register-password" class="form-label">Contraseña</label>
            <Field
              type="password"
              v-model="password"
              name="password"
              id="register-password"
              class="form-control"
              placeholder="Crea una contraseña segura"
            />
            <ErrorMessage name="password" class="text-danger-frontend" />
            <small class="form-text text-muted mt-1 d-block">Debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y un carácter especial.</small>
          </div>

          <div v-if="showButton" class="text-center">
            <button type="submit" class="btn btn-register" title="Registrarse">
              Registrarse
            </button>
          </div>

          <div v-else class="text-center mt-4">
            <center><img src="/img/load.gif" alt="Cargando..." width="40" /></center>
          </div>
          
          <div class="text-center mt-4">
            <p>¿Ya tienes una cuenta? <a @click.prevent="router.push('/login')" href="/autorent-leon/#/login">Inicia Sesión</a></p>
          </div>
        </Form>
      </div>
    </div>
  </LayoutGuest>
</template>

<style scoped>
/* Fondo con gradiente (Register) */
.SectionFullScreenRegister {
  background: linear-gradient(135deg, #6a11cb, #2575fc);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 1rem;
}

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

.form-control {
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #ced4da;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-control:focus {
  border-color: #6a11cb;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(106, 17, 203, 0.25);
}

.btn.btn-register {
  background-color: #6a11cb;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out, transform 0.1s ease;
  font-size: 1rem;
  font-weight: 500;
}

.btn.btn-register:hover {
  background-color: #2575fc;
  transform: translateY(-2px);
}

.btn.btn-register:active {
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

.alert.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  font-size: 0.9rem;
}


/* Enlaces */
a {
  color: #6a11cb; /* Color primario de Register */
  text-decoration: none;
  font-weight: 500;
}

a:hover {
  text-decoration: underline;
  color: #2575fc;
}

h2 {
  color: #333;
  font-weight: 600;
}

.form-text.text-muted {
    font-size: 0.8rem;
    color: #6c757d;
}

.d-block {
    display: block;
}
</style>