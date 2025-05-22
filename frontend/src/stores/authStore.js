import { defineStore } from "pinia";
import { ref } from 'vue';
import { jwtDecode } from "jwt-decode";
import axios from 'axios';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        authToken: localStorage.getItem('autorent_leon_token') || null,
        userPermissions: ref(null),
        isLoadingPermissions: ref(false),
        permissionsError: ref(null),
    }),
    actions: {
        async initiateSession(data) {
            localStorage.setItem('autorent_leon_token', data.token);
            this.authToken = data.token;

            this.userPermissions = null;
            this.permissionsError = null;
            this.isLoadingPermissions = false;

            await this.fetchUserPermissions(); 
        },

        checkLoggedIn() {
            this.authToken = localStorage.getItem('autorent_leon_token');
            if (!this.authToken) {
                if (this.userPermissions !== null) this.userPermissions = null;
                return false;
            }
            try {
                const decoded = jwtDecode(this.authToken);
                const now = Math.floor(Date.now() / 1000);
                if (decoded.exp < now) {
                    this.clearAuthData();
                    return false;
                }
                return true;
            } catch (error) {
                this.clearAuthData();
                return false;
            }
        },

        async fetchUserPermissions() {
            if (!this.authToken) {
                this.userPermissions = null;
                this.permissionsError = 'No autenticado para obtener permisos.';
                return false;
            }

            if (this.userPermissions !== null && !this.permissionsError && !this.isLoadingPermissions) {
                return true; 
            }

            if (this.isLoadingPermissions) {
                // console.log('Esperando carga de permisos en curso...');
                while (this.isLoadingPermissions) {
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
                return this.userPermissions !== null && !this.permissionsError;
            }

            this.isLoadingPermissions = true;
            this.permissionsError = null;

            try {
                const config = { headers: { 'Authorization': `Bearer ${this.authToken}` } };
                const response = await axios.get(`${import.meta.env.VITE_API_URL}user/permission`, config);
                
                if (response.data && typeof response.data.permissions !== 'undefined') {
                    this.userPermissions = response.data.permissions;
                } else {
                    throw new Error("Respuesta inesperada del servidor al obtener permisos.");
                }
                this.isLoadingPermissions = false;
                return true;
            } catch (error) {
                console.error("Error al obtener los permisos del usuario:", error);
                this.userPermissions = null;
                if (error.response) {
                    this.permissionsError = `Error: ${error.response.status} - ${error.response.data.mensaje || error.response.data.detail || 'Error del servidor'}`;
                    if (error.response.status === 401 || error.response.status === 403) {
                        this.clearAuthData();
                    }
                } else {
                    this.permissionsError = "No se pudo conectar para obtener permisos.";
                }
                this.isLoadingPermissions = false;
                return false;
            }
        },

        clearAuthData() {
            localStorage.removeItem('autorent_leon_token');
            this.authToken = null;
            this.userPermissions = null;
            this.permissionsError = null;
            this.isLoadingPermissions = false;
        },

        logout() {
            if (window.confirm("¿Realmente deseas cerrar sesión?")) {
                this.clearAuthData();
                window.location.href = `${import.meta.env.VITE_BASE_URL}/autorent-leon/#/login`;
            }
        },
    },
    getters: {
        isAuthenticated: (state) => !!state.authToken,
        getPermissions: (state) => state.userPermissions,
        isSuperuser: (state) => state.userPermissions === true,
        hasPermission: (state) => (permissionCodename) => {
            if (state.userPermissions === true) return true;
            if (Array.isArray(state.userPermissions)) return state.userPermissions.includes(permissionCodename);
            return false;
        },
    }
});