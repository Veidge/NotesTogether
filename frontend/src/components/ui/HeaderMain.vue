<script setup lang="ts">

</script>

<template>
    <div class="flex justify-between items-center mb-4 shadow-[0_5px_8px_-2px_rgba(64,58,51,0.25)]">
        <div class="gap-2 content-center">
            <h1 class="font-logo text-3xl px-4 p-2">Notes Together</h1>
        </div>
        <div class="flex-1 mx-5">
            <input type="text" placeholder="Поиск заметок"
                   class="w-full rounded-lg border border-color-accent bg-surface px-3 py-1"/>
        </div>
        <div class="gap-2 content-center mx-2 p-2">
            <RouterLink to="/login">Профиль</RouterLink>
        </div>
    </div>
</template>
