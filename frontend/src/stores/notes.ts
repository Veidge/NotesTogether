import {defineStore} from "pinia";
import {getNotes, createNote as createNoteRequest, updateNote as updateNoteRequest,
    deleteNote as deleteNoteRequest} from "../services/api.ts";

export interface Note {
    id: number;
    title: string;
    content: string;
    color: string;
    is_archived: boolean;
    created_at: string;
    updated_at: string;
}

type NoteData = Pick<Note, "title" | "content" | "color">;
type NoteChanges = Partial<NoteData>;

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

        async createNote(token: string, noteData: NoteData) {
            const newNote = await createNoteRequest(token, noteData);

            this.listNotes.push(newNote);
            this.selectedNote = newNote;
        },

        async updateNote(token: string, noteId: number, changes: NoteChanges) {
            const updatedNote = await updateNoteRequest(token, noteId, changes);
            const index = this.listNotes.findIndex(note => note.id === noteId);
            if (index !== -1) {
                this.listNotes[index] = updatedNote;
            }

            if (this.selectedNote?.id === noteId) {
                this.selectedNote = updatedNote;
            }
        },

        async deleteNote(token: string, noteId: number) {
            await deleteNoteRequest(token, noteId);
            this.listNotes = this.listNotes.filter(note => note.id !== noteId);
            if (this.selectedNote?.id === noteId) {
                this.selectedNote = this.listNotes[0] ?? null;
            }
        },

        selectNote(note: Note | null) {
            this.selectedNote = note;
        }
    }
});