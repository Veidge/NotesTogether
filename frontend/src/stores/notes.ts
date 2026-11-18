import {defineStore} from "pinia";

export interface Note {
    id: number;
    title: string;
    content: string;
    color: string;
    updated_at: string;
}

export const useNotesStore = defineStore("notes", {
    state: () => {
        const listNotes: Note[] = [
            {
                id: 1,
                title: "Заметка 1",
                content: "Текст заметки.",
                color: "#cf6f16",
                updated_at: "2026-11-17T14:30:00",
            },
            {
                id: 2,
                title: "Настроить рабочую среду frontend части",
                content: "Окружение, структура, перенос backend части. Создание первичной вёрстки для проекта. " +
                    "Подбор палитры, шрифтов.",
                color: "#46097a",
                updated_at: "2026-11-17T18:30:30",
            },
            {
                id: 3,
                title: "Посидеть вечером с кошкой",
                content: "Осмотр задней лапы, подготовка мисок. Поставить стул для залаза и прыжков.",
                color: "#3c3f47",
                updated_at: "2026-11-17T19:55:32",
            }
        ];
        return {
            listNotes, selectedNote: listNotes[0] as Note | null
        }

    },

    actions: {
        selectNote(note: Note | null) {
            this.selectedNote = note;
        }
    }
});