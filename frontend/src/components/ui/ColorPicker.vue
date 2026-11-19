<script setup lang="ts">
import Verte from "verte-vue3";
import "verte-vue3/dist/verte.css";

const color = defineModel<string>({ required: true });
</script>

<template>
    <Verte
        v-model="color"
        picker="square"
        model="hex"
        menu-position="top"
    />
</template>
