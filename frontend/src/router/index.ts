import {createRouter, createWebHistory} from "vue-router";
import NotePage from "../components/pages/NotePage.vue";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: "/",
            name: "notes",
            component: NotePage
        }
    ]
})

export default router