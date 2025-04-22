import { useAuthStore } from "@/stores/authStore";
import axios from "axios";

export function registerComposable(body) {
    let sendData = async (body) => {
        axios.post(`${import.meta.env.VITE_API_URL}user-control/register`, body, { headers: { "Content-Type": "application/json" } })
            .then((response) => {
                alert("You have successfully registered. We have sent an email to activate your account.");
                window.location.href = `${import.meta.env.VITE_BASE_URL}/autorent-leon/#/login`;
            })
            .catch(() => {
                alert("An unexpected error occurred.");
                window.location.reload();
            });
    };
    return {
        sendData,
    }
}

export function loginComposable() {
    let sendData = async (body) => {
        try {
            const response = await axios.post(
                `${import.meta.env.VITE_API_URL}user-control/login`, 
                body, 
                { headers: { "Content-Type": "application/json" } }
            );
            
            let store = useAuthStore();
            store.initiateSession(response.data);
            
            // Usar window.location pero con setTimeout para que primero se guarde en localStorage
            setTimeout(() => {
                window.location.href = `${import.meta.env.VITE_BASE_URL}/autorent-leon/#/`;
                // Para forzar recarga después de la redirección
                setTimeout(() => window.location.reload(), 50);
            }, 100);
            
            return true;
        } catch (error) {
            alert("An unexpected error occurred.");
            return false;
        }
    };
    
    return {
        sendData,
    }
}