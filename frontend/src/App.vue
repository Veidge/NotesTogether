<script setup lang="ts">

import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import {useAuthStore} from "./stores/auth.ts";
import ToastContainer from "./components/ui/ToastContainer.vue";
import {useToastStore} from "./stores/toast.ts";

const authStore = useAuthStore();
const toastStore = useToastStore();

onMounted(() => {
    authStore.fetchCurrentUser()
})

</script>

<template>
    <RouterView/>
    <ToastContainer/>
</template>
