import { defineStore } from "pinia";

export const useAuthStore = defineStore('auth', {
    state: () => ({
        authId: (localStorage.getItem('autorent_leon_id') !== null) ? localStorage.getItem('autorent_leon_id') : null,
        authName: (localStorage.getItem('autorent_leon_name') !== null) ? localStorage.getItem('autorent_leon_name') : null,
        authEmail: (localStorage.getItem('autorent_leon_email') !== null) ? localStorage.getItem('autorent_leon_email') : null,
        authIsSuperuser: (localStorage.getItem('autorent_leon_is_superuser') !== null) ? localStorage.getItem('autorent_leon_is_superuser') : null,
        authToken: (localStorage.getItem('autorent_leon_token') !== null) ? localStorage.getItem('autorent_leon_token') : null,
    }),
    actions: {
        initiateSession(data) {
            localStorage.setItem('autorent_leon_id', data.id);
            localStorage.setItem('autorent_leon_name', data.name);
            localStorage.setItem('autorent_leon_email', data.email);
            localStorage.setItem('autorent_leon_is_superuser', data.is_superuser);
            localStorage.setItem('autorent_leon_token', data.token);
        },
        checkLoggedIn() {
            // Primero refrescamos los datos del almacenamiento
            this.authId = localStorage.getItem('autorent_leon_id');
            this.authName = localStorage.getItem('autorent_leon_name');
            this.authEmail = localStorage.getItem('autorent_leon_email');
            this.authIsSuperuser = localStorage.getItem('autorent_leon_is_superuser');
            this.authToken = localStorage.getItem('autorent_leon_token');
            
            // Luego verificamos - importante: este orden es crucial
            if (this.authId === null) {
                window.location.href = `${import.meta.env.VITE_BASE_URL}/autorent-leon/#/login`;
                return false;
            }
            return true;
        },
        logout() {
            if (window.confirm("Do you really want to log out?")) {
                localStorage.clear();
                window.location = "/autorent-leon/#/login";
            }
        },
    }
});
