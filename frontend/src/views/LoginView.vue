<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { mdiAccount, mdiAsterisk } from '@mdi/js'
import SectionFullScreen from '@/components/SectionFullScreen.vue'
import CardBox from '@/components/CardBox.vue'
import FormCheckRadio from '@/components/FormCheckRadio.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import LayoutGuest from '@/layouts/LayoutGuest.vue'
import { Form, Field, ErrorMessage } from 'vee-validate'
import { loginSchema } from '@/schemas/loginValidationsSchema'
import { loginComposable } from '@/composables/useUserControlComposable'

let email = ref('');
let password = ref('');

// Para cuando se envía el correo:
let button = ref('block');
let preloader = ref('none');

const { sendData } = loginComposable();

const send = async () => {
  button.value = 'none';
  preloader.value = 'block';
  
  const success = await sendData({
    email: email.value,
    password: password.value,
  });
  
  if (!success) {
    // Restaura el botón si hay error
    button.value = 'block';
    preloader.value = 'none';
  }
};
</script>

<template>
  <LayoutGuest>
    <div class="SectionFullScreen">
      <div class="card-box">
        <Form :validation-schema="loginSchema" @submit="send()">
          <div class="mb-4">
            <ErrorMessage name="email" class="text-danger" />
            <Field
              type="text"
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
            <button type="submit" class="btn" title="Send">
              Send
            </button>
          </div>

          <div class="text-center mt-4" :style="'display:' + preloader">
            <img src="/img/load.gif" alt="Loading..." width="40" />
          </div>

          <div class="text-center mt-4">
            <p><a href="/autorent-leon/#/register">Register</a></p>
          </div>
        </Form>
      </div>
    </div>
  </LayoutGuest>
</template>


<style scoped>
/* Fondo con gradiente */
.SectionFullScreen {
  background: linear-gradient(135deg, #ff416c, #ff4b2b);
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
  background-color: #ff416c;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.btn:hover {
  background-color: #ff4b2b;
}

/* Errores */
.text-danger {
  font-size: 14px;
  margin-bottom: 4px;
  color: #e63946;
  display: block;
}
</style>