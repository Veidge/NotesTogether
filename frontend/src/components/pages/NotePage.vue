<script setup lang="ts">

import HeaderMain from "../ui/HeaderMain.vue";
</script>

<template>
    <div class="h-[92vh] w-full p-4 flex flex-col">
        <HeaderMain/>
        <div class="flex flex-col flex-1 py-2 rounded-xl border border-text shadow-sm">
            <div class="p-6 flex flex-1 justify-between">
                <div class="w-[20%] flex flex-col gap-2">
                    <div class="w-full h-10 rounded-lg border border-text px-2 content-center mb-4">
                        <h2 class="font-sans text-xl">Заметки</h2>
                    </div>
                    <div class="h-11 rounded-sm border border-text" v-for="note in 8" :key="note">
                        <h2 class="font-heading font-bold px-1">Заметка</h2>
                    </div>
                </div>
                <div class="flex flex-1 flex-col gap-2 mx-5">
                    <div class="w-full h-10 rounded-lg border border-text px-2 content-center mb-4">
                        <h2 class="font-sans text-xl">Заметка 1</h2>
                    </div>
                    <div class="flex-1 rounded-sm border border-black-200 p-4">
                        <h3>Без ничего.</h3>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
