import * as yup from 'yup';
//npm i vee-validate --save
//npm i @vee-validate/yup

export const loginSchema = yup.object({
  email: yup
    .string()
    .required("El correo electrónico es obligatorio.")
    .email("El formato del correo electrónico no es válido."),
  password: yup
    .string()
    .required("La contraseña es obligatoria."),
});

export const registerSchema = yup.object({
  name: yup
    .string()
    .required("El nombre es obligatorio.")
    .matches(/^[a-zA-ZÀ-ÿ\s'-]+$/, "El nombre solo puede contener letras y espacios."),
  email: yup
    .string()
    .required("El correo electrónico es obligatorio.")
    .email("El formato del correo electrónico no es válido."),
  password: yup
    .string()
    .required("La contraseña es obligatoria.")
    .min(8, "La contraseña debe tener al menos 8 caracteres."),
});