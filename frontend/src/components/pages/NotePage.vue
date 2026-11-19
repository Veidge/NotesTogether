<script setup lang="ts">
import HeaderMain from "../ui/HeaderMain.vue";
import {
    ArrowUpZA, ArrowDownZA,
    CalendarArrowDownIcon, CalendarArrowUpIcon,
    PlusIcon, XIcon
} from "@lucide/vue";
import {computed, onMounted, ref, watch, onBeforeUnmount} from "vue";
import type { Note } from '../../stores/notes';
import { useNotesStore } from '../../stores/notes';
import {storeToRefs} from "pinia";
import { useAuthStore } from "../../stores/auth";
import {useRouter} from "vue-router";
import ColorPicker from "../ui/ColorPicker.vue";
import CreateNoteModal from "../ui/CreateNoteModal.vue";


const router = useRouter();
const notesStore = useNotesStore();
const authStore = useAuthStore();

const { listNotes, selectedNote } = storeToRefs(notesStore);
const sortBy = ref<"title" | "updated_at">("updated_at");
const sortDirection = ref<"asc" | "desc">("desc");

const draftColor = ref("#B69C82");
const isColorPickerOpen = ref(false);
const isSavingColor = ref(false);
const colorSaveError = ref("");

const isCreateModalOpen = ref(false);
const isCreating = ref(false);
const createError = ref("");

const isDeleting = ref(false);
const deleteError = ref("");

function openColorPicker() {
    if (!selectedNote.value) return;

    draftColor.value = selectedNote.value.color;
    colorSaveError.value = "";
    isColorPickerOpen.value = true;
}

function cancelColorChange() {
    isColorPickerOpen.value = false;
    colorSaveError.value = "";
}

async function saveNoteColor() {
    if (!selectedNote.value || !authStore.token) return;

    isSavingColor.value = true;
    colorSaveError.value = "";

    try {
        await notesStore.updateNote(
            authStore.token,
            selectedNote.value.id,
            {color: draftColor.value}
        );

        isColorPickerOpen.value = false;
    } catch (error) {
        console.error("Не удалось изменить цвет заметки:", error);
        colorSaveError.value = "Не удалось сохранить цвет";
    } finally {
        isSavingColor.value = false;
    }
}

watch(selectedNote, (note) => {
    draftColor.value = note?.color ?? "#B69C82";
    isColorPickerOpen.value = false;
});

const editTitle = ref("");
const editContent = ref("");

const saveStatus = ref<"idle" | "editing" | "saving" | "saved" | "error">("idle");

let saveTimer: ReturnType<typeof setTimeout> | undefined;
let pendingSave: {
    noteId: number;
    title: string;
    content: string;
} | null = null;

let isSyncingEditor = false;
let saveQueue = Promise.resolve();

onMounted(async () => {
    if (!authStore.token) {
        await router.replace({ name: "login" });
        return;
    }
    try {
        await notesStore.fetchNotes(authStore.token);
    }
    catch (error) {
        if (error instanceof Error && "status" in error && error.status === 401) {
            authStore.logout();
            await router.replace({ name: "login" });
            return;
        }
        console.error("Не удалось загрузить заметки: ", error);
    }
});

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

function scheduleSave() {
    if (isSyncingEditor || !selectedNote.value) return;

    pendingSave = {
        noteId: selectedNote.value.id,
        title: editTitle.value,
        content: editContent.value
    };

    saveStatus.value = "editing";

    clearTimeout(saveTimer);

    saveTimer = setTimeout(() => {
        void flushSave();
    }, 800);
}

function flushSave() {
    clearTimeout(saveTimer);
    if (!pendingSave || !authStore.token) return saveQueue;
    const changes = pendingSave;
    pendingSave = null;

    saveQueue = saveQueue.then(async () => {
        if (selectedNote.value?.id === changes.noteId) {
            saveStatus.value = "saving";
        }
        try {
            await notesStore.updateNote(
                authStore.token!,
                changes.noteId,
                {
                    title: changes.title,
                    content: changes.content
                }
            );
            if (
                selectedNote.value?.id === changes.noteId &&
                !pendingSave
            ) {
                saveStatus.value = "saved";
            }
        } catch (error) {
            console.error("Не удалось сохранить заметку:", error);
            if (selectedNote.value?.id === changes.noteId) {
                saveStatus.value = "error";
            }
        }
    });
    return saveQueue;
}

async function handleCreateNote(noteData: {
    title: string;
    content: string;
    color: string;
}) {
    if (!authStore.token || isCreating.value) return;

    isCreating.value = true;
    createError.value = "";

    try {
        await notesStore.createNote(authStore.token, noteData);
        isCreateModalOpen.value = false;
    } catch (error) {
        console.error("Не удалось создать заметку:", error);
        createError.value = "Не удалось создать заметку. Попробуйте ещё раз.";
    } finally {
        isCreating.value = false;
    }
}

async function handleDeleteNote() {
    const note = selectedNote.value;
    if (!note || !authStore.token || isDeleting.value || isSavingColor.value) return;
    isDeleting.value = true;
    deleteError.value = "";

    try {
        await flushSave();
        if (saveStatus.value === "error") {
            deleteError.value = "Сначала необходимо сохранить изменения.";
            return;
        }

        await notesStore.deleteNote(authStore.token, note.id);
    } catch (error) {
        console.error("Не удалось переместить заметку в корзину:", error);
        deleteError.value = "Не удалось переместить заметку в корзину.";
    } finally {
        isDeleting.value = false;
    }
}

watch(
    selectedNote,
    (note) => {
        void flushSave();
        isSyncingEditor = true;
        editTitle.value = note?.title ?? "";
        editContent.value = note?.content ?? "";
        saveStatus.value = "idle";
        isSyncingEditor = false;
    },
    { immediate: true }
);

watch(
    [editTitle, editContent],
    scheduleSave,
    { flush: "sync" }
);

onBeforeUnmount(() => {
    void flushSave();
});
</script>

<template>
    <div class="h-[92vh] w-full p-4 flex flex-col">
        <HeaderMain/>
        <div class="flex flex-col flex-1 py-2 rounded-xl border border-text shadow-sm">
            <div class="p-6 flex flex-1 justify-between">
                <div class="w-75 flex flex-col gap-2">
                    <div class="flex h-10 rounded-lg border border-text px-2 items-center justify-between mb-4">
                        <div class="flex items-center gap-2">
                            <h2 class="font-sans text-xl">Заметки</h2>
                            <button class="p-1 rounded-md hover:bg-accent/35 transition-colors cursor-pointer"
                                title="Создать заметку" @click="isCreateModalOpen = true">
                                <PlusIcon :size="20" />
                            </button>
                        </div>
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
                    <div class="w-full min-h-10 rounded-lg border border-text px-2 py-1 mb-4 flex items-center gap-3">
                        <button class="w-6 h-6 rounded-sm border border-text/40 shrink-0 cursor-pointer"
                            :style="{ backgroundColor: selectedNote?.color }" title="Изменить цвет заметки"
                            @click="openColorPicker"/>
                        <input v-model="editTitle" class="font-sans text-xl w-full outline-none bg-transparent"
                            placeholder="Название заметки" maxlength="50"/>
                        <button
                            class="shrink-0 p-1 rounded-md hover:bg-red-200/70 transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                            title="Переместить в корзину" :disabled="!selectedNote || isDeleting || isSavingColor"
                            @click="handleDeleteNote">
                            <XIcon :size="20" />
                        </button>
                    </div>

                    <p class="text-xs text-text/60 text-right -mt-3 mb-1">
                        <span v-if="saveStatus === 'editing'">Есть несохранённые изменения</span>
                        <span v-else-if="saveStatus === 'saving'">Сохранение...</span>
                        <span v-else-if="saveStatus === 'saved'">Сохранено</span>
                        <span v-else-if="saveStatus === 'error'" class="text-red-700">Ошибка сохранения</span>
                    </p>
                    <p v-if="deleteError" class="text-xs text-red-700 text-right -mt-3 mb-1">
                        {{ deleteError }}
                    </p>

                    <div v-if="isColorPickerOpen"
                         class="mb-4 p-3 rounded-lg border border-text/40 bg-surface flex flex-col gap-3 w-fit">
                        <ColorPicker v-model="draftColor" />
                        <div class="flex gap-2">
                            <button
                                class="px-3 py-1 rounded-md bg-accent/60 hover:bg-accent transition-colors cursor-pointer"
                                :disabled="isSavingColor" @click="saveNoteColor">
                                {{ isSavingColor ? "Сохранение..." : "Применить" }}
                            </button>

                            <button class="px-3 py-1 rounded-md hover:bg-accent/35 transition-colors cursor-pointer"
                                :disabled="isSavingColor" @click="cancelColorChange">Отмена</button>
                        </div>
                        <p v-if="colorSaveError" class="text-sm text-red-700">{{ colorSaveError }}</p>
                    </div>
                    <div class="flex-1 rounded-sm border border-black-200 p-4">
                        <textarea v-model="editContent" :disabled="!selectedNote || isDeleting"
                            class="w-full h-full resize-none outline-none bg-transparent font-sans"
                            placeholder="Начните писать..."
                        />
                    </div>
                </div>
            </div>
        </div>
        <CreateNoteModal
            v-model="isCreateModalOpen"
            :loading="isCreating"
            :error="createError"
            @create="handleCreateNote"
        />
    </div>
</template>
