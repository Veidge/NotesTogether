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
                            class="flex items-center justify-between shrink-0 rounded-lg border border-text/20 px-3 py-2">
                            <span>{{ tag.name }}</span>
                            <span v-if="tag.default_tag" class="text-xs text-text/50">Стандартный</span>
                            <button v-else type="button" title="Удалить тег"
                                class="rounded-md p-1.5 text-text/50 hover:text-red-700 hover:bg-red-700/10 transition-colors cursor-pointer"
                                @click="handleDeleteTag(tag.id)">
                                <Trash2Icon :size="16" />
                            </button>
                        </div>

                        <p v-if="notesStore.tags.length === 0" class="text-sm text-text/50">Тегов пока нет</p>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>
</template>