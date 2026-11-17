<script setup lang="ts">
import HeaderMain from "../ui/HeaderMain.vue";
import { ArrowUpZA } from "@lucide/vue";
import { ArrowDownZA } from "@lucide/vue";
import { CalendarArrowDownIcon } from "@lucide/vue";
import { CalendarArrowUpIcon } from "@lucide/vue";
import {ref} from "vue";

interface Note {
    id: number;
    title: string;
    content: string;
    color: string;
}

const list_notes = ref([
    {
        id: 1,
        title: "Заметка 1",
        content: "Текст заметки.",
        color: "#cf6f16"
    },
    {
        id: 2,
        title: "Настроить рабочую среду frontend части",
        content: "Окружение, структура, перенос backend части. Создание первичной вёрстки для проекта. " +
            "Подбор палитры, шрифтов.",
        color: "#46097a"
    },
    {
        id: 3,
        title: "Посидеть вечером с кошкой",
        content: "Осмотр задней лапы, подготовка мисок. Поставить стул для залаза и прыжков.",
        color: "#3c3f47"
    }
]);


const selected_note = ref<Note>(list_notes.value[0]);

function selecting_note(note: Note) {
    selected_note.value = note;
}

</script>

<template>
    <div class="h-[92vh] w-full p-4 flex flex-col">
        <HeaderMain/>
        <div class="flex flex-col flex-1 py-2 rounded-xl border border-text shadow-sm">
            <div class="p-6 flex flex-1 justify-between">
                <div class="w-75 flex flex-col gap-2">
                    <div class="flex h-10 rounded-lg border border-text px-2 items-center justify-between mb-4">
                        <h2 class="font-sans text-xl">Заметки</h2>
                        <div class="flex gap-1 items-center">
                            <button class="cursor-pointer hover:bg-accent/35 transition-colors p-1 rounded-md">
                                <CalendarArrowUpIcon />
                            </button>
                            <button class="cursor-pointer hover:bg-accent/35 transition-colors p-1 rounded-md">
                                <ArrowDownZA/>
                            </button>
                        </div>
                    </div>
                    <div class="h-11 flex items-center rounded-sm border border-text cursor-pointer hover:bg-accent/35 transition-colors"
                         :class="{ 'bg-accent/75': selected_note?.id === note.id }"
                         v-for="note in list_notes" :key="note.id" @click="selecting_note(note)">
                        <div :style="{ backgroundColor: note?.color }" class="w-2 h-full shrink-0"/>
                        <h2 class="font-heading font-bold px-2 wrap-break-word leading-5">{{ note.title }}</h2>
                    </div>
                </div>
                <div class="flex flex-1 flex-col gap-2 mx-5">
                    <div class="w-full h-10 rounded-lg border border-text px-2 content-center mb-4">
                        <h2 class="font-sans text-xl">{{ selected_note?.title }}</h2>
                    </div>
                    <div class="flex-1 rounded-sm border border-black-200 p-4">
                        <h3>{{ selected_note?.content }}</h3>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
