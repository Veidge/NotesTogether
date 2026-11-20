<script setup lang="ts">
import { useRouter } from "vue-router";
import { LogOut } from "@lucide/vue";
import { useAuthStore } from "../../stores/auth";

const searchQuery = defineModel<string>({ default: "" });
const authStore = useAuthStore();
const router = useRouter();

function logout() {
    authStore.logout();
    router.replace({ name: "login" });
}
</script>

<template>
    <div class="flex flex-col md:flex-row md:justify-between md:items-center gap-2 md:gap-0 mb-4 pb-2 md:pb-0 shadow-[0_5px_8px_-2px_rgba(64,58,51,0.25)]">
        <div class="flex items-center justify-between md:contents">
            <div class="order-1 gap-2 content-center">
                <h1 class="font-logo md:text-3xl text-xl md:p-4 py-2 px-1">Notes Together</h1>
            </div>
            <div v-if="authStore.user" class="order-2 md:order-3 flex items-center gap-2 md:mx-2 md:p-2 p-1">
                <div class="flex min-w-0 flex-col items-end">
                    <span class="max-w-24 sm:max-w-40 truncate font-medium font-logo">{{ authStore.user.displayName }}</span>
                    <span class="max-w-24 sm:max-w-40 truncate text-xs text-text/50">@{{ authStore.user.username }}</span>
                </div>

                <button type="button" title="Выйти" aria-label="Выйти"
                        class="shrink-0 rounded-lg p-2 text-text/70 transition hover:bg-accent/20 hover:text-text cursor-pointer"
                        @click="logout">
                    <LogOut :size="18"/>
                </button>
            </div>
        </div>
        <div class="order-3 md:order-2 w-[95%] md:w-auto md:flex-1 md:mx-5 mx-auto min-w-0">
            <input v-model="searchQuery" type="text" placeholder="Поиск заметок"
                   class="w-full rounded-lg border border-color-accent bg-surface px-3 py-1"/>
        </div>
    </div>
</template>
