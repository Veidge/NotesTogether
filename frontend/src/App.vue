<script setup lang="ts">

import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import {useAuthStore} from "./stores/auth.ts";

const authStore = useAuthStore();
onMounted(() => {
    authStore.fetchCurrentUser()
})

</script>

<template>
    <RouterView/>
</template>
