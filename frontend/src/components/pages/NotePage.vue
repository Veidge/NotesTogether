<script setup lang="ts">
import HeaderMain from "../ui/HeaderMain.vue";
import { ArrowUpZA } from "@lucide/vue";
import { ArrowDownZA } from "@lucide/vue";
import { CalendarArrowDownIcon } from "@lucide/vue";
import { CalendarArrowUpIcon } from "@lucide/vue";
import {computed, ref, watch} from "vue";
import {Note, useNotesStore} from "../../stores/notes";
import {storeToRefs} from "pinia";
//
// const listNotes = ref([
//     {
//         id: 1,
//         title: "Заметка 1",
//         content: "Текст заметки.",
//         color: "#cf6f16",
//         updated_at: "2026-11-17T14:30:00",
//     },
//     {
//         id: 2,
//         title: "Настроить рабочую среду frontend части",
//         content: "Окружение, структура, перенос backend части. Создание первичной вёрстки для проекта. " +
//             "Подбор палитры, шрифтов.",
//         color: "#46097a",
//         updated_at: "2026-11-17T18:30:30",
//     },
//     {
//         id: 3,
//         title: "Посидеть вечером с кошкой",
//         content: "Осмотр задней лапы, подготовка мисок. Поставить стул для залаза и прыжков.",
//         color: "#3c3f47",
//         updated_at: "2026-11-17T19:55:32",
//     }
// ]);

const notesStore = useNotesStore();
const { listNotes, selectedNote } = storeToRefs(notesStore);
const sortBy = ref<"title" | "updated_at">("updated_at");
const sortDirection = ref<"asc" | "desc">("desc");

function selectNote(note: Note) {
    notesStore.selectNote(note);
}

const sortedNotes = computed(() => {
    return [...listNotes.value].sort((a, b) => {
        if (sortBy.value === 'updated_at') {
            return (new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime()) *
                (sortDirection.value === "asc" ? 1 : -1);
        }
        return a.title.localeCompare(b.title) * (sortDirection.value === "asc" ? 1 : -1);
    });
});

watch(sortedNotes, (notes) => {
    if (notes.length > 0) {
        notesStore.selectNote(notes[0]);
    }
    else {
        notesStore.selectNote(null);
    }
}, { immediate: true });

function sortByTitle() {
    if (sortBy.value === "title") {
        sortDirection.value =
            sortDirection.value === "asc" ? "desc" : "asc";
    }
    else {
        sortBy.value = "title";
        sortDirection.value = "asc";
    }
}

function sortByUpdatedAt() {
    if (sortBy.value === "updated_at") {
        sortDirection.value =
            sortDirection.value === "desc" ? "asc" : "desc";
    }
    else {
        sortBy.value = "updated_at";
        sortDirection.value = "desc";
    }
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
                            <button class="cursor-pointer hover:bg-accent/35 transition-colors p-1 rounded-md"
                                    :class="sortBy === 'updated_at' ? 'bg-accent/75' : ''"
                                    @click="sortByUpdatedAt" >
                                <CalendarArrowUpIcon v-if="sortBy === 'updated_at' && sortDirection === 'asc'"/>
                                <CalendarArrowDownIcon v-else/>
                            </button>
                            <button class="cursor-pointer hover:bg-accent/35 transition-colors p-1 rounded-md"
                                    :class="sortBy === 'title' ? 'bg-accent/75' : ''"
                                    @click="sortByTitle" >
                                <ArrowDownZA v-if="sortBy === 'title' && sortDirection === 'desc'"/>
                                <ArrowUpZA v-else/>
                            </button>
                        </div>
                    </div>
                    <div class="h-11 flex items-center rounded-sm border border-text cursor-pointer hover:bg-accent/35 transition-colors"
                         :class="{ 'bg-accent/75': selectedNote?.id === note.id }"
                         v-for="note in sortedNotes" :key="note.id" @click="selectNote(note)">
                        <div :style="{ backgroundColor: note?.color }" class="w-2 h-full shrink-0"/>
                        <h2 class="font-heading font-bold px-2 wrap-break-word leading-5">{{ note.title }}</h2>
                    </div>
                </div>
                <div class="flex flex-1 flex-col gap-2 mx-5">
                    <div class="w-full h-10 rounded-lg border border-text px-2 content-center mb-4">
                        <h2 class="font-sans text-xl">{{ selectedNote?.title }}</h2>
                    </div>
                    <div class="flex-1 rounded-sm border border-black-200 p-4">
                        <h3>{{ selectedNote?.content }}</h3>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
