import {defineStore} from "pinia";

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
        token: null as string | null
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
        },
        login(authData: UserLogin) {
            console.log("Вызван login:", authData)
        },
        register(registerData: UserRegister) {
            console.log("Вызван register:", registerData);
        },
        fetchCurrentUser() {

        }
    }
})