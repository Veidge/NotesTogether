<script setup lang="ts">
import HeaderMain from "../ui/HeaderMain.vue";
import {
    ArrowUpZA, ArrowDownZA,
    CalendarArrowDownIcon, CalendarArrowUpIcon,
    PlusIcon, XIcon
} from "@lucide/vue";
import {computed, onMounted, ref, watch, onBeforeUnmount} from "vue";
import type {Note, NoteSection} from '../../stores/notes';
import { useNotesStore } from '../../stores/notes';
import {storeToRefs} from "pinia";
import { useAuthStore } from "../../stores/auth";
import {useRouter} from "vue-router";
import ColorPicker from "../ui/ColorPicker.vue";
import CreateNoteModal from "../ui/CreateNoteModal.vue";
import ManageTagsModal from "../ui/ManageTagsModal.vue";
import SharingPanel from "../ui/SharingPanel.vue";
import { useToastStore } from "../../stores/toast";


const router = useRouter();
const notesStore = useNotesStore();
const authStore = useAuthStore();
const toastStore = useToastStore();

const { listNotes, archivedNotes, trashedNotes, selectedNote, activeSection, noteTags } = storeToRefs(notesStore);
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

const isTagListOpen = ref(false);
const isUpdatingTag = ref(false);
const tagError = ref("");
const isManageTagsModalOpen = ref(false);

const searchQuery = ref("");

let searchTimeout: ReturnType<typeof setTimeout> | undefined;
watch(searchQuery, (value) => {
    if (!authStore.token) return;
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    searchTimeout = setTimeout(async () => {
        try {
            const search = value.trim();
            if (search) {
                await notesStore.fetchNotes(authStore.token!, { search });
            }
            else {
                await notesStore.fetchNotes(authStore.token!);
            }
        }
        catch (error) {
            console.error("Ошибка поиска заметок:", error);
        }
    }, 350);
});

const tagDropdown = ref<HTMLElement | null>(null);

function handleOutsideClick(event: MouseEvent) {
    if (!tagDropdown.value?.contains(event.target as Node)) {
        isTagListOpen.value = false;
    }
}

onMounted(() => {document.addEventListener("click", handleOutsideClick);});
onBeforeUnmount(() => {
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    document.removeEventListener("click", handleOutsideClick);
});


const availableTags = computed(() =>
    notesStore.tags.filter(
        tag => !noteTags.value.some(noteTag => noteTag.id === tag.id)
    )
);

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

watch(
    [selectedNote, activeSection],
    async ([note, section]) => {
        notesStore.noteTags = [];
        if (!note || section === "trash" || !authStore.token) {
            return;
        }

        try {
            await notesStore.fetchNoteTags(authStore.token, note.id);
        } catch (error) {
            console.error("Не удалось загрузить теги заметки: ", error);
        }
    },
    { immediate: true }
);

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
        await authStore.fetchCurrentUser();
        if (!authStore.token) {
            await router.replace({ name: "login" });
            return;
        }
        await Promise.all([
            notesStore.fetchNotes(authStore.token),
            notesStore.fetchTags(authStore.token)
        ]);
    }
    catch (error) {
        if (error instanceof Error && "status" in error && error.status === 401) {
            authStore.logout();
            await router.replace({ name: "login" });
            return;
        }
        console.error("Не удалось загрузить данные: ", error);
    }
});

function selectNote(note: Note, section: NoteSection) {
    notesStore.selectNote(note, section);
}

function sortNotes(notes: Note[]) {
    return [...notes].sort((a, b) => {
        const direction = sortDirection.value === "asc" ? 1 : -1;

        if (sortBy.value === "updated_at") {
            return (
                new Date(a.updated_at).getTime() -
                new Date(b.updated_at).getTime()
            ) * direction;
        }

        return a.title.localeCompare(b.title) * direction;
    });
}

const sortedNotes = computed(() => sortNotes(listNotes.value));
const sortedArchivedNotes = computed(() => sortNotes(archivedNotes.value));
const sortedTrashedNotes = computed(() => sortNotes(trashedNotes.value));


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

async function handleCreateNote(noteData: {title: string; content: string; color: string;}) {
    if (!authStore.token || isCreating.value) return;
    if (!noteData.title.trim() && !noteData.content.trim()) {
        toastStore.addToast("error", "Нельзя создать пустую заметку");
        return;
    }

    isCreating.value = true;
    createError.value = "";

    try {
        await notesStore.createNote(authStore.token, noteData);
        isCreateModalOpen.value = false;
        toastStore.addToast("success", "Заметка создана");
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
        toastStore.addToast("success", "Заметка перемещена в корзину");
    } catch (error) {
        console.error("Не удалось переместить заметку в корзину:", error);
        deleteError.value = "Не удалось переместить заметку в корзину.";
    } finally {
        isDeleting.value = false;
    }
}

async function handleArchiveNote() {
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
        await notesStore.archiveNote(authStore.token, note.id, true);
        toastStore.addToast("success", "Заметка перемещена в архив");
    } catch (error) {
        console.error("Не удалось переместить заметку в архив:", error);
        deleteError.value = "Не удалось переместить заметку в архив.";
    } finally {
        isDeleting.value = false;
    }
}

async function handleUnarchiveNote() {
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
        await notesStore.archiveNote(authStore.token, note.id, false);
        toastStore.addToast("success", "Заметка возвращена из архива");
    } catch (error) {
        console.error("Не удалось вернуть заметку из архива:", error);
        deleteError.value = "Не удалось вернуть заметку из архива.";
    } finally {
        isDeleting.value = false;
    }
}

async function handleRestoreNote() {
    const note = selectedNote.value;
    if (!note || !authStore.token || isDeleting.value) return;
    isDeleting.value = true;
    deleteError.value = "";
    try {
        await notesStore.restoreNote(authStore.token, note.id);
        toastStore.addToast("success", "Заметка восстановлена");
    } catch (error) {
        console.error("Не удалось восстановить заметку:", error);
        deleteError.value = "Не удалось восстановить заметку.";
    } finally {
        isDeleting.value = false;
    }
}

async function handlePermanentlyDeleteNote() {
    const note = selectedNote.value;
    if (!note || !authStore.token || isDeleting.value) return;
    const confirmed = window.confirm(
        `Вы уверены, что хотите безвозвратно удалить заметку «${note.title}»? Восстановить её будет невозможно.`
    );
    if (!confirmed) return;

    isDeleting.value = true;
    deleteError.value = "";
    try {
        await notesStore.permanentlyDeleteNote(authStore.token, note.id);
        toastStore.addToast("success", "Заметка удалена");
    } catch (error) {
        console.error("Не удалось удалить заметку окончательно:", error);
        deleteError.value = "Не удалось удалить заметку окончательно.";
    } finally {
        isDeleting.value = false;
    }
}

async function handleAddTag(tagId: number) {
    if (!authStore.token || !selectedNote.value || isUpdatingTag.value) return;
    isUpdatingTag.value = true;
    tagError.value = "";

    try {
        await notesStore.addTagToNote(authStore.token, selectedNote.value.id, tagId);
    } catch (error) {
        console.error("Не удалось прикрепить тег:", error);
        tagError.value = "Не удалось прикрепить тег.";
    } finally {
        isUpdatingTag.value = false;
    }
}

async function handleRemoveTag(tagId: number) {
    if (!authStore.token || !selectedNote.value || isUpdatingTag.value) return;
    isUpdatingTag.value = true;
    tagError.value = "";

    try {
        await notesStore.removeTagFromNote(authStore.token, selectedNote.value.id, tagId);
    } catch (error) {
        console.error("Не удалось открепить тег:", error);
        tagError.value = "Не удалось открепить тег.";
    } finally {
        isUpdatingTag.value = false;
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
    <div class="min-h-[92dvh] xl:h-[92vh] w-full p-2 sm:p-4 flex flex-col">
        <HeaderMain v-model="searchQuery"/>
        <div class="flex flex-col flex-1 min-h-0 py-2 rounded-xl border border-text shadow-sm">
            <div class="px-2 sm:px-4 py-3 sm:py-6 flex flex-col sm:flex-row flex-1 gap-3 min-h-0 overflow-y-auto xl:overflow-hidden">
                <div class="w-full sm:w-64 xl:w-75 sm:shrink-0 min-h-0 sm:h-full sm:overflow-y-auto flex flex-col gap-3">

                    <!--Заметки-->
                    <div class="h-64 shrink-0 sm:flex-1 sm:h-auto sm:shrink min-h-0 flex flex-col rounded-lg border border-text p-2">                        <div class="flex h-10 shrink-0 items-center justify-between px-1 mb-2">
                            <div class="flex items-center gap-2">
                                <h2 class="font-heading md:text-xl text-lg">Заметки</h2>
                                <button class="p-1 rounded-md hover:bg-accent/35 transition-colors cursor-pointer"
                                    title="Создать заметку" @click="isCreateModalOpen = true">
                                    <PlusIcon :size="20" />
                                </button>
                            </div>

                            <div class="flex gap-1 items-center">
                                <button class="cursor-pointer hover:bg-accent/35 transition-colors p-1 rounded-md"
                                    :class="sortBy === 'updated_at' ? 'bg-accent/75' : ''"
                                    @click="sortByUpdatedAt">
                                    <CalendarArrowUpIcon v-if="sortBy === 'updated_at' && sortDirection === 'asc'"/>
                                    <CalendarArrowDownIcon v-else/>
                                </button>

                                <button class="cursor-pointer hover:bg-accent/35 transition-colors p-1 rounded-md"
                                    :class="sortBy === 'title' ? 'bg-accent/75' : ''"
                                    @click="sortByTitle">
                                    <ArrowDownZA v-if="sortBy === 'title' && sortDirection === 'desc'"/>
                                    <ArrowUpZA v-else/>
                                </button>
                            </div>
                        </div>

                        <div class="flex-1 min-h-0 overflow-y-auto flex flex-col gap-2">
                            <div v-if="sortedNotes.length === 0"
                                 class="flex-1 flex flex-col items-center justify-center text-center text-text/65">
                                <p class="font-heading font-bold text-base">Пока нет заметок</p>
                                <p class="text-sm">Создайте свою первую заметку</p>
                            </div>
                            <div v-for="note in sortedNotes" :key="note.id"
                                class="h-11 shrink-0 flex items-center rounded-sm border border-text cursor-pointer hover:bg-accent/35 transition-colors"
                                :class="{ 'bg-accent/75': selectedNote?.id === note.id && activeSection === 'notes' }"
                                @click="selectNote(note, 'notes')">
                                <div :style="{ backgroundColor: note.color }" class="w-2 h-full shrink-0"/>
                                <h2 class="font-heading font-bold px-2 wrap-break-word leading-5">
                                    {{ note.title }}
                                </h2>
                            </div>
                        </div>
                    </div>

                    <!-- Архив -->
                    <div class="h-28 shrink-0 flex flex-col rounded-lg border border-text p-2">
                        <div class="h-10 shrink-0 flex items-center px-1 mb-2">
                            <h2 class="font-heading md:text-xl text-lg">Архив</h2>
                        </div>

                        <div v-if="sortedArchivedNotes.length === 0"
                             class="flex-1 flex items-center justify-center text-sm text-text/65">
                            Архив пуст
                        </div>
                        <div class="flex-1 min-h-0 overflow-y-auto flex flex-col gap-2">
                            <div v-for="note in sortedArchivedNotes" :key="note.id"
                                class="h-11 shrink-0 flex items-center rounded-sm border border-text cursor-pointer hover:bg-accent/35 transition-colors"
                                :class="{ 'bg-accent/75': selectedNote?.id === note.id && activeSection === 'archive' }"
                                @click="selectNote(note, 'archive')">
                                <div :style="{ backgroundColor: note.color }" class="w-2 h-full shrink-0"/>
                                <h2 class="font-heading font-bold px-2 wrap-break-word leading-5">
                                    {{ note.title }}
                                </h2>
                            </div>
                        </div>
                    </div>

                    <!-- Корзина -->
                    <div class="h-28 shrink-0 flex flex-col rounded-lg border border-text p-2">
                        <div class="h-10 shrink-0 flex items-center px-1 mb-2">
                            <h2 class="font-heading md:text-xl text-lg">Корзина</h2>
                        </div>
                        
                        <div v-if="sortedTrashedNotes.length === 0"
                             class="flex-1 flex items-center justify-center text-sm text-text/65">
                            Корзина пуста
                        </div>
                        <div class="flex-1 min-h-0 overflow-y-auto flex flex-col gap-2">
                            <div v-for="note in sortedTrashedNotes" :key="note.id"
                                class="h-11 shrink-0 flex items-center rounded-sm border border-text cursor-pointer hover:bg-accent/35 transition-colors"
                                :class="{ 'bg-accent/75': selectedNote?.id === note.id && activeSection === 'trash' }"
                                @click="selectNote(note, 'trash')">
                                <div :style="{ backgroundColor: note.color }" class="w-2 h-full shrink-0"/>
                                <h2 class="font-heading font-bold px-2 wrap-break-word leading-5">
                                    {{ note.title }}
                                </h2>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex flex-col min-[1000px]:flex-row flex-1 min-w-0 min-h-0 gap-3">

                    <div class="w-full min-[1000px]:flex-1 min-w-0 min-h-[55vh] min-[1000px]:min-h-0 min-[1000px]:overflow-y-auto flex flex-col gap-2 border-t-2 border-accent/70 pt-3 mt-2 sm:border-0 sm:pt-0 sm:mt-0">
                        <p v-if="selectedNote" class="sm:hidden px-1 text-xs font-medium uppercase tracking-wider text-text/55">
                            Выбранная заметка
                        </p>
                        <div class="w-full min-h-10 rounded-lg border border-text px-2 py-1 flex items-center gap-3">
                            <button v-if="activeSection !== 'trash'" class="w-6 h-6 rounded-sm border border-text/40 shrink-0 cursor-pointer"
                                :style="{ backgroundColor: selectedNote?.color }" title="Изменить цвет заметки"
                                @click="openColorPicker"/>

                            <!-- Заголовок -->
                            <input v-model="editTitle" placeholder="Название заметки" maxlength="50"
                                   class="font-sans text-base sm:text-xl flex-1 min-w-0 outline-none bg-transparent disabled:opacity-70"
                                   :disabled="!selectedNote || activeSection === 'trash'"/>

                            <!-- Действия для обычных заметок -->
                            <button v-if="activeSection === 'notes'"
                                class="shrink-0 px-2 py-1 rounded-md hover:bg-accent/35 transition-colors cursor-pointer disabled:opacity-40"
                                title="Переместить в архив" :disabled="!selectedNote || isDeleting || isSavingColor"
                                @click="handleArchiveNote">
                                В архив
                            </button>

                            <!-- Действия для архива -->
                            <button v-else-if="activeSection === 'archive'"
                                class="shrink-0 px-2 py-1 rounded-md hover:bg-accent/35 transition-colors cursor-pointer disabled:opacity-40"
                                title="Вернуть в заметки" :disabled="!selectedNote || isDeleting || isSavingColor"
                                @click="handleUnarchiveNote">
                                Вернуть
                            </button>

                            <!-- Перемещение в корзину -->
                            <button v-if="activeSection !== 'trash'"
                                class="shrink-0 p-1 rounded-md hover:bg-red-200/70 transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                                title="Переместить в корзину" :disabled="!selectedNote || isDeleting || isSavingColor"
                                @click="handleDeleteNote">
                                <XIcon :size="20" />
                            </button>

                            <!-- Действия для корзины -->
                            <template v-else>
                                <button class="shrink-0 px-2 py-1 rounded-md hover:bg-accent/35 transition-colors cursor-pointer"
                                    title="Восстановить заметку" :disabled="!selectedNote"
                                    @click="handleRestoreNote">
                                    Восстановить
                                </button>
                                <button class="shrink-0 px-2 py-1 rounded-md hover:bg-red-200/70 transition-colors
                                cursor-pointer disabled:cursor-not-allowed disabled:opacity-50"
                                        :title="selectedNote?.is_owner ? 'Удалить окончательно' : 'Удалить невозможно, обратитесь к владельцу'"
                                        :disabled="!selectedNote?.is_owner || isDeleting"
                                    @click="handlePermanentlyDeleteNote">
                                    Удалить
                                </button>
                            </template>
                        </div>

                        <p class="text-xs text-text/60 text-right -mt-3">
                            <span v-if="saveStatus === 'editing'">Есть несохранённые изменения</span>
                            <span v-else-if="saveStatus === 'saving'">Сохранение...</span>
                            <span v-else-if="saveStatus === 'saved'">Сохранено</span>
                            <span v-else-if="saveStatus === 'error'" class="text-red-700">Ошибка сохранения</span>
                        </p>
                        <p v-if="deleteError" class="text-xs text-red-700 text-right -mt-3 mb-1">
                            {{ deleteError }}
                        </p>
                        <div class="note-color-picker relative">

                            <div v-if="isColorPickerOpen && activeSection !== 'trash'"
                                 class="absolute left-0 top-full z-20 mt-2 p-3 rounded-lg border border-text/40 bg-surface shadow-md flex flex-col gap-3 w-fit">
                                <ColorPicker v-model="draftColor" />
                                <div class="flex gap-2">
                                    <button class="px-3 py-1 rounded-md bg-accent/60 hover:bg-accent transition-colors cursor-pointer"
                                        :disabled="isSavingColor"
                                        @click="saveNoteColor">
                                        {{ isSavingColor ? "Сохранение..." : "Применить" }}
                                    </button>

                                    <button class="px-3 py-1 rounded-md hover:bg-accent/35 transition-colors cursor-pointer"
                                        :disabled="isSavingColor"
                                        @click="cancelColorChange">
                                        Отмена
                                    </button>
                                </div>
                                <p v-if="colorSaveError" class="text-sm text-red-700">{{ colorSaveError }}</p>
                            </div>
                        </div>
                        <div v-if="selectedNote && activeSection !== 'trash'" class="min-h-10 flex flex-col items-start gap-2 px-1 mb-2">
                            <div class="flex items-center gap-3 shrink-0">
                                <span class="text-sm text-text/60">Теги:</span>
                            </div>

                            <div class="flex flex-wrap items-center gap-2">
                                <span v-for="tag in noteTags" :key="tag.id"
                                      class="rounded-full bg-accent/20 px-3 py-1 text-xs text-text flex items-center gap-1">
                                    {{ tag.name }}
                                    <button class="rounded-full p-0.5 hover:bg-accent/40 transition-colors cursor-pointer disabled:opacity-40"
                                        title="Открепить тег" :disabled="isUpdatingTag"
                                        @click="handleRemoveTag(tag.id)">
                                        <XIcon :size="12" />
                                    </button>
                                </span>

                                <div class="relative" ref="tagDropdown">
                                    <button
                                        class="w-6 h-6 flex items-center justify-center rounded-full border border-text/30 hover:bg-accent/35 transition-colors cursor-pointer disabled:opacity-40"
                                        title="Добавить тег"
                                        :disabled="isUpdatingTag"
                                        @click.stop="isTagListOpen = !isTagListOpen">
                                        <PlusIcon :size="16" />
                                    </button>

                                    <div v-if="isTagListOpen"
                                         class="absolute left-0 top-full z-30 mt-2 w-52 max-h-60 overflow-y-auto rounded-lg border border-text/30 bg-surface shadow-md p-2">
                                        <p class="text-xs text-text/50 px-2 py-1">Доступные теги</p>
                                        <button v-for="tag in availableTags" :key="tag.id"
                                            class="w-full text-left px-2 py-2 rounded-md text-sm hover:bg-accent/25 transition-colors cursor-pointer disabled:opacity-40"
                                            :disabled="isUpdatingTag"
                                            @click="handleAddTag(tag.id)">
                                            {{ tag.name }}
                                        </button>

                                        <p v-if="availableTags.length === 0" class="px-2 py-2 text-xs text-text/50">Все теги уже добавлены</p>
                                    </div>
                                </div>
                            </div>
                            <button class="self-end shrink-0 text-sm text-text/60 hover:text-text transition-colors cursor-pointer"
                                    @click="isManageTagsModalOpen = true">
                                Управление
                            </button>
                        </div>
                        <div class="min-h-0 flex-1 rounded-sm border border-black-200 p-4">
                            <textarea v-model="editContent"
                                      :disabled="!selectedNote || isDeleting || activeSection === 'trash'"
                                      class="w-full h-full resize-none outline-none bg-transparent font-sans"
                                      placeholder="Начните писать..."/>
                        </div>
                    </div>

                    <SharingPanel v-if="selectedNote && activeSection !== 'trash'" :note-id="selectedNote.id"
                                  :is-owner="selectedNote.is_owner"/>
                </div>
            </div>
        </div>
        <CreateNoteModal
            v-model="isCreateModalOpen"
            :loading="isCreating"
            :error="createError"
            @create="handleCreateNote"
        />
        <ManageTagsModal
            v-model="isManageTagsModalOpen"
        />
    </div>
</template>
