<script setup lang="ts">

const searchQuery = defineModel<string>({ default: "" });

</script>

<template>
    <div class="flex justify-between items-center mb-4 shadow-[0_5px_8px_-2px_rgba(64,58,51,0.25)]">
        <div class="gap-2 content-center">
            <h1 class="font-logo md:text-3xl text-xl md:p-4 py-2 px-1">Notes Together</h1>
        </div>
        <div class="md:flex-1 md:mx-5 mx-1">
            <input v-model="searchQuery" type="text" placeholder="Поиск заметок"
                   class="w-full rounded-lg border border-color-accent bg-surface px-3 py-1"/>
        </div>
        <div class="gap-2 content-center md:mx-2 md:p-2 p-1">
            <RouterLink to="/login">Профиль</RouterLink>
        </div>
    </div>
</template>
