import {createRouter, createWebHistory} from "vue-router";
import NotePage from "../components/pages/NotePage.vue";
import LoginPage from "../components/pages/LoginPage.vue";
import RegisterPage from "../components/pages/RegisterPage.vue";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: "/",
            name: "notes",
            component: NotePage
        },
        {
            path: "/login",
            name: "login",
            component: LoginPage
        },
        {
            path: "/register",
            name: "register",
            component: RegisterPage
        }
    ]
})

export default router