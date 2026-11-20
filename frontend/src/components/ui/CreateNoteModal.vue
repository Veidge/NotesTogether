<script setup lang="ts">
import { ref, watch } from "vue";
import ColorPicker from "./ColorPicker.vue";

interface NoteData {
    title: string;
    content: string;
    color: string;
}

const isOpen = defineModel<boolean>({ required: true });
const props = defineProps<{
    loading?: boolean;
}>();

const emit = defineEmits<{
    create: [noteData: NoteData];
}>();

const title = ref("");
const content = ref("");
const color = ref("#B69C82");

watch(isOpen, (opened) => {
    if (opened) {
        title.value = "";
        content.value = "";
        color.value = "#B69C82";
    }
});

function submitForm() {
    const trimmedTitle = title.value.trim();
    if (!trimmedTitle || props.loading) return;

    emit("create", {
        title: trimmedTitle,
        content: content.value,
        color: color.value
    });
}
</script>

<template>
    <Teleport to="body">
        <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
            @click.self="isOpen = false">
            <form class="create-note-modal w-full max-w-lg rounded-xl border border-text bg-surface p-6 shadow-xl flex flex-col gap-4"
                @submit.prevent="submitForm" novalidate>
                <h2 class="font-logo text-2xl">Новая заметка</h2>
                <div class="flex flex-col gap-1">
                    <label class="font-heading font-semibold text-xl py-2">Название</label>
                    <input v-model="title" type="text" maxlength="50" required autofocus placeholder="Название заметки"
                        class="w-full rounded-lg border border-text/40 bg-background/50 px-3 py-2 outline-none focus:border-text"/>
                </div>

                <div class="flex flex-col gap-1">
                    <label class="font-heading font-semibold text-xl py-2">Содержимое</label>
                    <textarea v-model="content" rows="7" placeholder="Начните писать..."
                        class="w-full resize-y rounded-lg border border-text/40 bg-background/50 px-3 py-2 outline-none focus:border-text"/>
                </div>

                <div class="flex flex-col gap-2">
                    <label class="font-heading font-semibold text-xl py-2">Цвет заметки</label>
                    <div class="flex items-center gap-3 px-1">
                        <div class="w-8 h-8 rounded-sm border border-text/40"
                            :style="{ backgroundColor: color }"/>
                        <ColorPicker v-model="color" />
                    </div>
                </div>
                <div class="flex justify-end gap-2 mt-2">
                    <button type="button" class="px-4 py-2 rounded-lg hover:bg-accent/35 transition-colors cursor-pointer"
                        :disabled="loading" @click="isOpen = false">
                        Отмена
                    </button>
                    <button type="submit" class="px-4 py-2 rounded-lg bg-accent/60 hover:bg-accent transition-colors cursor-pointer"
                        :disabled="loading || !title.trim()">
                        {{ loading ? "Создание..." : "Создать" }}
                    </button>
                </div>
            </form>
        </div>
    </Teleport>
</template>
