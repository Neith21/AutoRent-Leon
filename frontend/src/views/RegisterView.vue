<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { mdiAccount, mdiEmail, mdiAsterisk } from '@mdi/js'
import LayoutGuest from '@/layouts/LayoutGuest.vue'
import { Form, Field, ErrorMessage } from 'vee-validate'
import { registerSchema } from '@/schemas/loginValidationsSchema'
import { registerComposable } from '@/composables/useUserControlComposable'

let name = ref('');
let email = ref('');
let password = ref('');

// Para cuando se envía el formulario:
let button = ref('block');
let preloader = ref('none');

const { sendData } = registerComposable();

const send = () => {
  button.value = 'none';
  preloader.value = 'block';
  sendData({
    name: name.value,
    email: email.value,
    password: password.value,
  });
};
</script>

<template>
  <LayoutGuest>
    <div class="SectionFullScreen">
      <div class="card-box">
        <h2 class="text-center mb-4">Register</h2>
        
        <Form :validation-schema="registerSchema" @submit="send">
          <div class="mb-4">
            <ErrorMessage name="name" class="text-danger" />
            <Field
              type="text"
              v-model="name"
              name="name"
              class="form-control"
              placeholder="Enter your name"
            />
          </div>

          <div class="mb-4">
            <ErrorMessage name="email" class="text-danger" />
            <Field
              type="email"
              v-model="email"
              name="email"
              class="form-control"
              placeholder="Enter your email"
            />
          </div>

          <div class="mb-4">
            <ErrorMessage name="password" class="text-danger" />
            <Field
              type="password"
              v-model="password"
              name="password"
              class="form-control"
              placeholder="Enter your password"
            />
          </div>

          <div class="text-center" :style="'display:' + button">
            <button type="submit" class="btn" title="Register">
              Register
            </button>
          </div>

          <div class="text-center mt-4" :style="'display:' + preloader">
            <img src="/img/load.gif" alt="Loading..." width="40" />
          </div>
          
          <div class="text-center mt-4">
            <p>Already have an account? <a href="/autorent-leon/#/login">Login</a></p>
          </div>
        </Form>
      </div>
    </div>
  </LayoutGuest>
</template>

<style scoped>
/* Fondo con gradiente */
.SectionFullScreen {
  background: linear-gradient(135deg, #6a11cb, #2575fc);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

/* Tarjeta del formulario */
.card-box {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 100%;
}

/* Input */
.form-control {
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #ccc;
  width: 100%;
  margin-bottom: 12px;
}

/* Botón */
.btn {
  background-color: #6a11cb;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.btn:hover {
  background-color: #2575fc;
}

/* Errores */
.text-danger {
  font-size: 14px;
  margin-bottom: 4px;
  color: #e63946;
  display: block;
}

/* Enlaces */
a {
  color: #6a11cb;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

h2 {
  color: #333;
  margin-bottom: 1.5rem;
}
</style>