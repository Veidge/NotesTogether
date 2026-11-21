<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { useNotesStore } from "../../stores/notes";
import { useAuthStore } from "../../stores/auth";
import type { NoteUserResponse } from "../../services/api";
import { useToastStore } from "../../stores/toast";

const props = defineProps<{
    noteId: number;
    isOwner: boolean;
}>();

const notesStore = useNotesStore();
const authStore = useAuthStore();
const toastStore = useToastStore();

const { noteUsers } = storeToRefs(notesStore);

const username = ref("");
const inviteRole = ref<"editor" | "viewer">("editor");

const isLoading = ref(false);
const isInviting = ref(false);

const currentUsername = computed(() => authStore.user?.username);

async function loadUsers() {
    if (!authStore.token) return;
    isLoading.value = true;
    notesStore.noteUsers = [];

    try {
        await notesStore.fetchNoteUsers(authStore.token, props.noteId);
    } catch (error) {
        toastStore.addToast("error", error instanceof Error ? error.message : "Не удалось загрузить список участников.");
    } finally {
        isLoading.value = false;
    }
}

async function inviteUser() {
    const invitedUsername = username.value.trim();
    if (!invitedUsername || !authStore.token) return;
    isInviting.value = true;
    try {
        await notesStore.shareNote(authStore.token, props.noteId, invitedUsername, inviteRole.value === "editor");
        toastStore.addToast("success", "Участник успешно добавлен");
        username.value = "";
    } catch (error) {
        toastStore.addToast("error", error instanceof Error ? error.message : "Не удалось пригласить пользователя.");
    } finally {
        isInviting.value = false;
    }
}

async function changeRole(user: NoteUserResponse, event: Event) {
    if (!authStore.token) return;
    const target = event.target as HTMLSelectElement;
    const isEditor = target.value === "editor";
    try {
        await notesStore.updateNoteUserRole(authStore.token, props.noteId, user.user_id, isEditor);
        toastStore.addToast("success", "Права участника изменены");
    } catch (error) {
        toastStore.addToast("error", error instanceof Error ? error.message : "Не удалось изменить права пользователя.");
        target.value = user.is_editor ? "editor" : "viewer";
    }
}

async function revokeAccess(user: NoteUserResponse) {
    if (!authStore.token) return;
    const confirmed = window.confirm(
        `Отозвать доступ к заметке у пользователя ${user.username}?`
    );

    if (!confirmed) return;
    try {
        await notesStore.removeNoteUser(authStore.token, props.noteId, user.user_id);
        toastStore.addToast("success", "Доступ отозван");
    } catch (error) {
        toastStore.addToast("error", error instanceof Error ? error.message : "Не удалось отозвать доступ.");
    }
}

function getUserRole(user: NoteUserResponse): string {
    if (
        props.isOwner &&
        user.username === currentUsername.value
    ) {
        return "Владелец";
    }

    return user.is_editor ? "Редактор" : "Без права редактирования";
}

watch(
    () => props.noteId,
    () => {
        void loadUsers();
    },
    { immediate: true }
);
</script>

<template>
    <aside class="w-full max-w-xl mx-auto min-w-0 min-[1000px]:mx-0 min-[1000px]:w-60 min-[1000px]:shrink-0 min-h-0 overflow-y-auto flex flex-col gap-4 border-t border-text/15 px-3 sm:px-4 min-[1000px]:border-t-0 min-[1000px]:border-l">
        <div class="flex flex-col gap-1 items-center">
            <h2 class="font-heading text-lg sm:text-xl">Участники заметки</h2>
        </div>

        <div class="grid grid-cols-1 min-[640px]:grid-cols-2 min-[1000px]:grid-cols-1 gap-4">
            <form v-if="isOwner" class="flex flex-col gap-2" @submit.prevent="inviteUser">
                <label class="text-sm font-medium text-text">Пригласить пользователя</label>

                <input v-model="username" type="text" minlength="3" maxlength="25" placeholder="Имя пользователя"
                    class="w-full rounded-lg border border-text/20 bg-surface p-2 text-sm outline-none focus:border-accent"
                    required/>

                <select v-model="inviteRole"
                    class="w-full rounded-lg border border-text/20 bg-surface p-2 text-sm outline-none focus:border-accent">
                    <option value="editor">Редактор</option>
                    <option value="viewer">Без права редактирования</option>
                </select>

                <button type="submit" :disabled="isInviting || !username.trim()"
                    class="rounded-lg bg-accent px-3 py-2 text-sm text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50">
                    {{ isInviting ? "Приглашение..." : "Добавить участника" }}
                </button>
            </form>

            <div class="flex flex-col gap-3">
                <div class="flex items-center justify-between">
                    <h3 class="text-sm font-medium text-text">Участники</h3>

                    <span class="text-xs text-text/50">{{ noteUsers.length }}</span>
                </div>

                <p v-if="isLoading" class="text-sm text-text/50">Загрузка участников...</p>
                <p v-else-if="noteUsers.length === 0" class="text-sm text-text/50">Список участников пуст.</p>
                <div v-for="user in noteUsers" :key="user.user_id" class="min-w-0 flex flex-col gap-2 rounded-lg bg-surface p-3">
                    <div class="flex min-w-0 flex-col gap-0.5">
                        <span class="truncate text-sm font-medium text-text">{{ user.display_name }}</span>
                        <span class="truncate text-xs text-text/50">@{{ user.username }}</span>
                        <span class="mt-1 text-xs text-text/70">{{ getUserRole(user) }}
                            <template v-if="user.username === currentUsername">- Вы</template>
                        </span>
                    </div>

                    <template v-if="isOwner && user.username !== currentUsername">
                        <select :value="user.is_editor ? 'editor' : 'viewer'"
                            class="w-full rounded-md border border-text/15 bg-background px-2 py-1.5 text-xs text-text outline-none focus:border-accent"
                            @change="changeRole(user, $event)">
                            <option value="editor">Редактор</option>
                            <option value="viewer">Без права редактирования</option>
                        </select>

                        <button type="button" class="self-start text-xs text-red-700 transition hover:text-red-900"
                            @click="revokeAccess(user)">
                            Отозвать доступ
                        </button>
                    </template>
                </div>
            </div>
        </div>
    </aside>
</template>
