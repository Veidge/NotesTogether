import {defineStore} from "pinia";

export type ToastType = 'success' | 'info' | 'error';

export interface Toast {
    id: number;
    type: ToastType;
    message: string;
}

const durations: Record<ToastType, number> = {
    success: 3000,
    info: 4000,
    error: 5000,
};

let nextToastId = 0;

const timers = new Map<number, ReturnType<typeof setTimeout>>();

export const useToastStore = defineStore("toast", {
    state: () => ({
        toasts: [] as Toast[],
    }),
    actions: {
        addToast(type: ToastType, message: string) {
            const id = ++nextToastId;
            this.toasts.push({id, type, message});
            const timer = setTimeout(() => {
                this.removeToast(id);
            }, durations[type]);
            timers.set(id, timer);
        },
        removeToast(id: number) {
            const timer = timers.get(id);
            if (timer) {
                clearTimeout(timer);
                timers.delete(id);
            }
            this.toasts = this.toasts.filter((toast) => toast.id !== id);
        },

        clearToast() {
            for (const timer of timers.values()) {
                clearTimeout(timer);
            }
            timers.clear();
            this.toasts = [];
        }
    }
})
