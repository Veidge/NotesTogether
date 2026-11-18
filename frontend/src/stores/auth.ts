import {defineStore} from "pinia";
import { getUser, login, register } from "../services/api.ts";

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
        },
        async login(authData: UserLogin) {
            console.log("Вызван login:", authData)
            const tokenResponse  = await login(authData.username, authData.password);
            this.token = tokenResponse.access_token
            localStorage.setItem("token", tokenResponse.access_token)
            const userResponse = await getUser(tokenResponse.access_token);
            this.user = { displayName: userResponse.display_name, username: userResponse.username };
        },
        async register(registerData: UserRegister) {
            console.log("Вызван register:", registerData);
            const userResponse = await register(registerData.displayName, registerData.username, registerData.password);
            this.user = { displayName: userResponse.display_name, username: userResponse.username };
        },
        async fetchCurrentUser() {
            if (!this.token) {
                return;
            }
            const userResponse = await getUser(this.token);
            this.user = { displayName: userResponse.display_name, username: userResponse.username };
        }
    }
})