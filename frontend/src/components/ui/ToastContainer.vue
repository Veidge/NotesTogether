<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useToastStore } from "../../stores/toast";
import { CheckCircle, AlertCircle, Info, X } from "@lucide/vue";

const toastStore = useToastStore();
const { toasts } = storeToRefs(toastStore);

const icons = {
    success: CheckCircle,
    error: AlertCircle,
    info: Info,
};
</script>

<template>
    <div class="fixed top-4 right-4 z-[100] flex w-[calc(100%-2rem)] max-w-sm flex-col gap-2">
        <TransitionGroup name="toast" tag="div" class="flex flex-col gap-2">
            <div v-for="toast in toasts" :key="toast.id"
                class="flex items-start gap-3 rounded-lg border bg-surface p-3 shadow-lg"
                :class="{
                    'border-green-600/40': toast.type === 'success',
                    'border-red-600/40': toast.type === 'error',
                    'border-blue-600/40': toast.type === 'info',
                }">
                <component :is="icons[toast.type]" :size="20" class="mt-0.5 shrink-0"
                    :class="{
                        'text-green-700': toast.type === 'success',
                        'text-red-700': toast.type === 'error',
                        'text-blue-700': toast.type === 'info',
                    }"/>

                <p class="min-w-0 flex-1 text-sm text-text">{{ toast.message }}</p>
                <button type="button" aria-label="Закрыть уведомление" class="shrink-0 text-text/50 transition hover:text-text"
                    @click="toastStore.removeToast(toast.id)">
                    <X :size="18" />
                </button>
            </div>
        </TransitionGroup>
    </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active,
.toast-move {
    transition: all 0.2s ease;
}

.toast-enter-from,
.toast-leave-to {
    opacity: 0;
    transform: translateX(20px);
}

.toast-leave-active {
    position: absolute;
}
</style>
