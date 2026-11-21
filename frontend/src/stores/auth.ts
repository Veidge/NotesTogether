import {defineStore} from "pinia";
import { getUser, login, register, type ApiError } from "../services/api.ts";
import { useNotesStore } from "./notes.ts";
import { useToastStore } from "./toast.ts";

export interface UserRegister {
    displayName: string;
    username: string;
    password: string;
}

export interface UserLogin {
    username: string;
    password: string;
}

export interface User {
    displayName: string;
    username: string;
}

export const useAuthStore = defineStore("auth", {
    state: () => ({
        user: null as User | null,
        token: localStorage.getItem("token"),
    }),

    getters: {
        isAuthenticated : function(): boolean {
            return this.token !== null;
        }
    },

    actions: {
        logout() {
            this.user = null;
            this.token = null;
            localStorage.removeItem("token");
            const notesStore = useNotesStore();
            notesStore.$reset();
        },
        async login(authData: UserLogin) {
            const tokenResponse  = await login(authData.username, authData.password);
            this.token = tokenResponse.access_token
            localStorage.setItem("token", tokenResponse.access_token)
            const userResponse = await getUser(tokenResponse.access_token);
            this.user = { displayName: userResponse.display_name, username: userResponse.username };
        },
        async register(registerData: UserRegister) {
            const userResponse = await register(registerData.displayName, registerData.username, registerData.password);
            this.user = { displayName: userResponse.display_name, username: userResponse.username };
        },
        async fetchCurrentUser() {
            if (!this.token) {
                return;
            }
            try {
                const userResponse = await getUser(this.token);
                this.user = { displayName: userResponse.display_name, username: userResponse.username };
            }
            catch (error) {
                if (error instanceof Error && "status" in error && typeof error.status === "number") {
                    const apiError = error as ApiError;
                    if (apiError.status === 401) {
                        this.handleSessionExpired();
                        return;
                    }
                }
                throw error;
            }
        },

        handleSessionExpired() {
            if (!this.token) return;
            const toastStore = useToastStore();
            toastStore.addToast("error", "Время Вашей сессии истекло. Пожалуйста, войдите снова");
            this.logout();
        },
    }
})