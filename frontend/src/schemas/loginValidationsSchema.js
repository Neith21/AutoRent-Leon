import * as yup from 'yup';
//npm i vee-validate --save
//npm i @vee-validate/yup

export const loginSchema = yup.object({
    email: yup
        .string()
        .required("The E-mail field is required")
        .email("Invalid E-mail"),
    password: yup
        .string()
        .required("The password field is required"),
});

export const registerSchema = yup.object({
    name: yup
        .string()
        .required("The name field is required"),
    email: yup
        .string()
        .required("The E-mail field is required")
        .email("Invalid E-mail"),
    password: yup
        .string()
        .required("The password field is required"),
});