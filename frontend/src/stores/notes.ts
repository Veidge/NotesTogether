import {defineStore} from "pinia";
import {getNotes, createNote as createNoteRequest, updateNote as updateNoteRequest,
    deleteNote as deleteNoteRequest,  getArchivedNotes, getTrashedNotes,
    archiveNote as archiveNoteRequest, restoreNote as restoreNoteRequest,
    permanentlyDeleteNote as permanentlyDeleteNoteRequest, getTags, getNoteTags,
    createTag as createTagRequest, updateTag as updateTagRequest, deleteTag as deleteTagRequest,
    addTagToNote as addTagToNoteRequest, removeTagFromNote as removeTagFromNoteRequest,
    type NoteSearchParams, type NoteUserResponse,
    getNoteUsers, shareNote as shareNoteRequest,
    updateNoteUserRole as updateNoteUserRoleRequest,
    removeNoteUser as removeNoteUserRequest,
} from "../services/api.ts";

export interface Note {
    id: number;
    title: string;
    is_owner: boolean;
    content: string;
    color: string;
    is_archived: boolean;
    created_at: string;
    updated_at: string;
}

export interface Tag {
    id: number;
    name: string;
    default_tag: boolean;
}

type NoteData = Pick<Note, "title" | "content" | "color">;
type NoteChanges = Partial<NoteData>;
export type NoteSection = "notes" | "archive" | "trash";

export const useNotesStore = defineStore("notes", {
    state: () => ({
        listNotes: [] as Note[],
        archivedNotes: [] as Note[],
        trashedNotes: [] as Note[],
        selectedNote: null as Note | null,
        activeSection: "notes" as NoteSection,
        tags: [] as Tag[],
        noteTags: [] as Tag[],
        noteUsers: [] as NoteUserResponse[],
    }),

    actions: {
        async fetchNotes(token: string, params?: NoteSearchParams) {
            if (params) {
                const [notes, archivedNotes] = await Promise.all([
                    getNotes(token, params),
                    getArchivedNotes(token, params)
                ]);

                this.listNotes = notes;
                this.archivedNotes = archivedNotes;

                const currentNote = [...notes, ...archivedNotes].find(
                    note => note.id === this.selectedNote?.id);
                if (currentNote) {
                    this.selectedNote = currentNote;
                }
                else if (this.activeSection === "archive") {
                    this.selectedNote = archivedNotes[0] ?? null;
                }
                else {
                    this.selectedNote = notes[0] ?? null;
                }
            }

            else {
                const [notes, archivedNotes, trashedNotes] = await Promise.all([
                    getNotes(token),
                    getArchivedNotes(token),
                    getTrashedNotes(token)
                ]);

                this.listNotes = notes;
                this.archivedNotes = archivedNotes;
                this.trashedNotes = trashedNotes;

                this.selectedNote = notes[0] ?? archivedNotes[0] ?? trashedNotes[0] ?? null;
                if (notes.length > 0) {
                    this.activeSection = "notes";
                }
                else if (archivedNotes.length > 0) {
                    this.activeSection = "archive";
                }
                else {
                    this.activeSection = "trash";
                }
            }
            this.noteTags = [];
            this.noteUsers = [];
        },

        async createNote(token: string, noteData: NoteData) {
            if (this.activeSection !== "notes") return;
            const newNote = await createNoteRequest(token, noteData);
            this.listNotes.push(newNote);
            this.selectedNote = newNote;
        },

        async updateNote(token: string, noteId: number, changes: NoteChanges) {
            const updatedNote = await updateNoteRequest(token, noteId, changes);
            const noteLists = [this.listNotes, this.archivedNotes, this.trashedNotes];
            for (const notes of noteLists) {
                const index = notes.findIndex(note => note.id === noteId);
                if (index !== -1) {
                    notes[index] = updatedNote;
                    break;
                }
            }
            if (this.selectedNote?.id === noteId) {
                this.selectedNote = updatedNote;
            }
        },

        async deleteNote(token: string, noteId: number) {
            await deleteNoteRequest(token, noteId);
            const source = this.activeSection === "archive" ? this.archivedNotes : this.listNotes;
            const note = source.find(note => note.id === noteId);
            if (note) {
                this.trashedNotes.push(note);
            }
            if (this.selectedNote?.id === noteId) {
                this.selectedNote = null;
            }
            const index = source.findIndex(note => note.id === noteId);
            if (index !== -1) {
                source.splice(index, 1);
            }
        },

        async archiveNote(token: string, noteId: number, isArchived: boolean) {
            await archiveNoteRequest(token, noteId, isArchived);
            const source = isArchived ? this.listNotes : this.archivedNotes;
            const destination = isArchived ? this.archivedNotes : this.listNotes;
            const index = source.findIndex(note => note.id === noteId);

            if (index !== -1) {
                const [note] = source.splice(index, 1);
                if (note) {
                    destination.push({ ...note, is_archived: isArchived });
                }
            }
            if (this.selectedNote?.id === noteId) {
                this.selectedNote = null;
            }
        },

        async restoreNote(token: string, noteId: number) {
            const restoredNote = await restoreNoteRequest(token, noteId);
            this.trashedNotes = this.trashedNotes.filter(note => note.id !== noteId);
            if (restoredNote.is_archived) {
                this.archivedNotes.push(restoredNote);
            } else {
                this.listNotes.push(restoredNote);
            }
            if (this.selectedNote?.id === noteId) {
                this.selectedNote = null;
            }
        },

        async permanentlyDeleteNote(token: string, noteId: number) {
            await permanentlyDeleteNoteRequest(token, noteId);
            this.trashedNotes = this.trashedNotes.filter(note => note.id !== noteId);
            if (this.selectedNote?.id === noteId) {
                this.selectedNote = null;
            }
        },

        selectNote(note: Note | null, section: NoteSection) {
            if (this.selectedNote?.id === note?.id && this.activeSection === section) {
                return;
            }
            this.selectedNote = note;
            this.activeSection = section;
            this.noteTags = [];
            this.noteUsers = [];
        },

        async fetchTags(token: string) {
            this.tags = await getTags(token);
        },

        async fetchNoteTags(token: string, noteId: number) {
            const tags = await getNoteTags(token, noteId);
            if (this.selectedNote?.id === noteId && this.activeSection !== "trash") {
                this.noteTags = tags;
            }
        },

        async createTag(token: string, name: string) {
            const newTag = await createTagRequest(token, name);
            this.tags.push(newTag);
            return newTag;
        },

        async updateTag(token: string, tagId: number, name: string) {
            const updatedTag = await updateTagRequest(token, tagId, name);
            const index = this.tags.findIndex(tag => tag.id === tagId);
            if (index !== -1) {
                this.tags[index] = updatedTag;
            }
            this.noteTags = this.noteTags.map(tag =>
                tag.id === tagId ? updatedTag : tag
            );
        },

        async deleteTag(token: string, tagId: number) {
            await deleteTagRequest(token, tagId);
            this.tags = this.tags.filter(tag => tag.id !== tagId);
            this.noteTags = this.noteTags.filter(tag => tag.id !== tagId);
        },

        async addTagToNote(token: string, noteId: number, tagId: number) {
            await addTagToNoteRequest(token, noteId, tagId);
            const tag = this.tags.find(tag => tag.id === tagId);
            if (tag && !this.noteTags.some(noteTag => noteTag.id === tagId)) {
                this.noteTags.push(tag);
            }
        },

        async removeTagFromNote(token: string, noteId: number, tagId: number) {
            await removeTagFromNoteRequest(token, noteId, tagId);
            this.noteTags = this.noteTags.filter(tag => tag.id !== tagId);
        },

        async fetchNoteUsers(token: string, noteId: number) {
            const users = await getNoteUsers(token, noteId);
            if (this.selectedNote?.id === noteId && this.activeSection !== "trash") {
                this.noteUsers = users;
            }
        },

        async shareNote(token: string, noteId: number, username: string, isEditor: boolean) {
            await shareNoteRequest(token, noteId, username, isEditor);
            await this.fetchNoteUsers(token, noteId);
        },

        async updateNoteUserRole(token: string, noteId: number, userId: number, isEditor: boolean) {
            const updatedUser = await updateNoteUserRoleRequest(token, noteId, userId, isEditor);
            if (this.selectedNote?.id === noteId) {
                const index = this.noteUsers.findIndex(
                    user => user.user_id === userId
                );
                if (index !== -1) {
                    this.noteUsers[index] = updatedUser;
                }
            }
        },

        async removeNoteUser(token: string, noteId: number, userId: number) {
            await removeNoteUserRequest(token, noteId, userId);
            if (this.selectedNote?.id === noteId) {
                this.noteUsers = this.noteUsers.filter(
                    user => user.user_id !== userId
                );
            }
        },
    }
});