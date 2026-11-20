<script setup lang="ts">
import { ref, watch } from "vue";
import { useNotesStore } from "../../stores/notes";
import { useAuthStore } from "../../stores/auth";
import { Trash2Icon } from "@lucide/vue";

const isOpen = defineModel<boolean>({ required: true });
const notesStore = useNotesStore();
const authStore = useAuthStore()

const newTagName = ref("");
const isCreating = ref(false);
const errorMessage = ref("");

const editingTagId = ref<number | null>(null);
const editingTagName = ref("");
const isUpdating = ref(false);

watch(isOpen, async (opened) => {
    if (opened && authStore.token) {
        newTagName.value = "";
        errorMessage.value = "";
        try {
            await notesStore.fetchTags(authStore.token);
        } catch (error) {
            console.error("Не удалось загрузить теги:", error);
            errorMessage.value = "Не удалось загрузить теги.";
        }
    }
});

async function handleCreateTag() {
    const name = newTagName.value.trim();
    if (!name || !authStore.token || isCreating.value) return;
    isCreating.value = true;
    errorMessage.value = "";

    try {
        await notesStore.createTag(authStore.token, name);
        newTagName.value = "";
    } catch (error) {
        console.error("Не удалось создать тег:", error);
        errorMessage.value = "Не удалось создать тег.";
    } finally {
        isCreating.value = false;
    }
}

async function handleDeleteTag(tagId: number) {
    if (!authStore.token) return;
    errorMessage.value = "";
    try {
        await notesStore.deleteTag(authStore.token, tagId);
    } catch (error) {
        console.error("Не удалось удалить тег:", error);
        errorMessage.value = "Не удалось удалить тег.";
    }
}

function startEditing(tagId: number, name: string) {
    editingTagId.value = tagId;
    editingTagName.value = name;
    errorMessage.value = "";
}

function cancelEditing() {
    editingTagId.value = null;
    editingTagName.value = "";
}

async function handleUpdateTag() {
    const name = editingTagName.value.trim();
    if (!name || !authStore.token || editingTagId.value === null || isUpdating.value) {
        return;
    }

    isUpdating.value = true;
    errorMessage.value = "";
    try {
        await notesStore.updateTag(authStore.token, editingTagId.value, name);
        cancelEditing();
    } catch (error) {
        console.error("Не удалось изменить тег:", error);
        errorMessage.value = "Не удалось изменить тег.";
    } finally {
        isUpdating.value = false;
    }
}
</script>

<template>
    <Teleport to="body">
        <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
            @click.self="isOpen = false">
            <div class="w-full max-w-lg max-h-[85vh] rounded-xl border border-text bg-surface p-6 shadow-xl flex flex-col gap-4">
                <h2 class="font-logo text-2xl">Управление тегами</h2>
                <form class="flex gap-2" @submit.prevent="handleCreateTag">
                    <input v-model="newTagName" type="text" maxlength="25" placeholder="Название нового тега"
                        class="min-w-0 flex-1 rounded-lg border border-text/40 bg-background/50 px-3 py-2 outline-none focus:border-text"/>
                    <button type="submit" class="px-4 py-2 rounded-lg bg-accent/60 hover:bg-accent transition-colors cursor-pointer disabled:opacity-50"
                        :disabled="isCreating || !newTagName.trim()">
                        {{ isCreating ? "..." : "Добавить" }}
                    </button>
                </form>

                <p v-if="errorMessage" class="text-sm text-red-700">{{ errorMessage }}</p>
                <div class="flex flex-col gap-2 min-h-0">
                    <h3 class="font-heading font-semibold text-lg">Список тегов</h3>
                    <div class="flex flex-col gap-2 max-h-64 overflow-y-auto pr-1">

                        <div v-for="tag in notesStore.tags" :key="tag.id"
                            class="flex items-center justify-between shrink-0 rounded-lg border border-text/20 px-3 py-2 gap-2">

                            <!-- Режим редактирования -->
                            <template v-if="editingTagId === tag.id">
                                <input v-model="editingTagName" type="text" maxlength="25"
                                    class="min-w-0 flex-1 rounded-md border border-text/30 bg-background/50 px-2 py-1 text-sm outline-none focus:border-text"
                                    @keydown.enter.prevent="handleUpdateTag" @keydown.esc="cancelEditing"/>

                                <div class="flex items-center gap-1 shrink-0">
                                    <button type="button" title="Сохранить"
                                        class="rounded-md px-2 py-1 text-sm hover:bg-accent/30 cursor-pointer disabled:opacity-40"
                                        :disabled="isUpdating || !editingTagName.trim()"
                                        @click="handleUpdateTag">
                                        Сохранить
                                    </button>
                                    <button type="button" title="Отменить"
                                        class="rounded-md px-2 py-1 text-sm text-text/60 hover:bg-accent/30 cursor-pointer"
                                        :disabled="isUpdating"
                                        @click="cancelEditing">
                                        Отмена
                                    </button>
                                </div>
                            </template>

                            <!-- Обычный режим -->
                            <template v-else>
                                <span class="min-w-0 truncate">{{ tag.name }}</span>
                                <span v-if="tag.default_tag" class="text-xs text-text/50 shrink-0">Стандартный</span>
                                <div v-else class="flex items-center gap-1 shrink-0">
                                    <button type="button" title="Изменить тег"
                                        class="rounded-md px-2 py-1 text-xs text-text/60 hover:text-text hover:bg-accent/30 cursor-pointer"
                                        @click="startEditing(tag.id, tag.name)">
                                        Изменить
                                    </button>
                                    <button type="button" title="Удалить тег"
                                        class="rounded-md px-2 py-1 text-xs text-text/60 hover:text-red-700 hover:bg-red-700/10 cursor-pointer"
                                        @click="handleDeleteTag(tag.id)">
                                        Удалить
                                    </button>
                                </div>
                            </template>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>
</template>