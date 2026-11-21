// @ts-ignore
import "./assets/style/main.css"

import { createApp } from 'vue'
import App from './App.vue'
import router from "./router";
import {createPinia} from "pinia";
import {useAuthStore} from "./stores/auth.ts";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

const authStore = useAuthStore();
await authStore.fetchCurrentUser();

app.mount('#app');