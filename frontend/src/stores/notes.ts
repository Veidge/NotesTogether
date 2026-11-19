import {defineStore} from "pinia";
import {getNotes} from "../services/api.ts";

export interface Note {
    id: number;
    title: string;
    content: string;
    color: string;
    is_archived: boolean;
    created_at: string;
    updated_at: string;
}

export const useNotesStore = defineStore("notes", {
    state: () => ({
        listNotes: [] as Note[],
        selectedNote: null as Note | null
    }),

    actions: {
        async fetchNotes(token: string) {
            const notes = await getNotes(token);
            this.listNotes = notes;
            this.selectedNote = notes.find(note => note.id === this.selectedNote?.id) ?? notes[0] ?? null;
        },

        selectNote(note: Note | null) {
            this.selectedNote = note;
        }
    }
});