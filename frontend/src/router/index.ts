import {createRouter, createWebHistory} from "vue-router";
import NotePage from "../components/pages/NotePage.vue";
import LoginPage from "../components/pages/LoginPage.vue";
import RegisterPage from "../components/pages/RegisterPage.vue";
import { useAuthStore } from "../stores/auth";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: "/",
            name: "notes",
            component: NotePage,
            meta: { requiresAuth: true }
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

router.beforeEach((to) => {
    const authStore = useAuthStore();
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        return { name: "login" };
    }
});

export default router