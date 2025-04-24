import { defineStore } from "pinia";
import { jwtDecode } from "jwt-decode";

export const useAuthStore = defineStore('auth', {
    state: () => ({
        authToken: (localStorage.getItem('autorent_leon_token') !== null) ? localStorage.getItem('autorent_leon_token') : null,
    }),
    actions: {
        initiateSession(data) {
            localStorage.setItem('autorent_leon_token', data.token);
        },
        checkLoggedIn() {
            // Primero refrescamos los datos del almacenamiento
            this.authToken = localStorage.getItem('autorent_leon_token');
            
            // Luego verificamos - importante: este orden es crucial
            if (this.authToken === null) {
                window.location.href = `${import.meta.env.VITE_BASE_URL}/autorent-leon/#/login`;
                return false;
            }
            
            try {
                const decoded = jwtDecode(this.authToken);
                const now = Math.floor(Date.now() / 1000);

                if (decoded.exp < now) {
                    localStorage.clear();
                    window.location.href = `${import.meta.env.VITE_BASE_URL}/autorent-leon/#/login`;
                    return false;
                }

                return true;
            } catch (error) {
                localStorage.clear();
                window.location.href = `${import.meta.env.VITE_BASE_URL}/autorent-leon/#/login`;
                return false;
            }
        },
        logout() {
            if (window.confirm("Do you really want to log out?")) {
                localStorage.clear();
                window.location.href = `${import.meta.env.VITE_BASE_URL}/autorent-leon/#/login`;
            }
        },
    }
});
