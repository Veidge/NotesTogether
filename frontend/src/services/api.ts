import type {Note, Tag} from "../stores/notes.ts";

const API_URL = import.meta.env.VITE_API_URL;

export interface ApiUser {
    display_name: string;
    username: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
}

export interface ApiError extends Error {
    status: number;
}

export interface NoteSearchParams {
    search: string;
}

export async function getUser(token: string): Promise<ApiUser> {
    const response = await fetch(`${API_URL}/auth/me`, {
        method: 'GET',
        headers: {
            Authorization: `Bearer ${token}`,
        }
    })
    return handleResponse<ApiUser>(response);
}

export async function login(username: string, password: string): Promise<TokenResponse> {
    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    })
    return handleResponse<TokenResponse>(response);
}

export async function register(displayName: string, username: string, password: string): Promise<ApiUser> {
    const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ display_name: displayName, username, password }),
    })
    return handleResponse<ApiUser>(response);
}

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const errorData = await response.json();
        const error = new Error(
            `Ошибка получения данных: ${response.status} ${response.statusText} - ${errorData.detail}`
        ) as ApiError;
        error.status = response.status;
        throw error;
    }
    if (response.status === 204) {
        return undefined as T;
    }
    return response.json();
}


export async function getNotes(token: string, params?: NoteSearchParams): Promise<Note[]> {
    const query = new URLSearchParams();
    if (params?.search) {
        query.set("search", params.search);
    }
    const response = await fetch(`${API_URL}/notes?${query.toString()}`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`,
        }
    });
    return handleResponse<Note[]>(response);
}

export async function createNote(token: string, noteData: Pick<Note, "title" | "content" | "color">): Promise<Note> {
    const response = await fetch(`${API_URL}/notes`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(noteData)
    });

    return handleResponse<Note>(response);
}

export async function updateNote(token: string, noteId: number,
                                 changes: Partial<Pick<Note, "title" | "content" | "color">>): Promise<Note> {
    const response = await fetch(`${API_URL}/notes/${noteId}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(changes)
    });

    return handleResponse<Note>(response);
}

export async function deleteNote(token: string, noteId: number): Promise<void> {
    const response = await fetch(`${API_URL}/notes/${noteId}`, {
        method: "DELETE",
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    return handleResponse<void>(response);
}

export async function getArchivedNotes(token: string, params?: NoteSearchParams): Promise<Note[]> {
    const query = new URLSearchParams();
    if (params?.search) {
        query.set("search", params.search);
    }
    const response = await fetch(`${API_URL}/notes/archive?${query.toString()}`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
    return handleResponse<Note[]>(response);
}

export async function getTrashedNotes(token: string): Promise<Note[]> {
    const response = await fetch(`${API_URL}/notes/trash`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
    return handleResponse<Note[]>(response);
}

export async function archiveNote(token: string, noteId: number, isArchived: boolean): Promise<void> {
    const response = await fetch(`${API_URL}/notes/${noteId}/archive`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ is_archived: isArchived })
    });
    return handleResponse<void>(response);
}

export async function restoreNote(token: string, noteId: number): Promise<Note> {
    const response = await fetch(`${API_URL}/notes/${noteId}/restore`, {
        method: "PATCH",
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
    return handleResponse<Note>(response);
}

export async function permanentlyDeleteNote(token: string, noteId: number): Promise<void> {
    const response = await fetch(`${API_URL}/notes/${noteId}/permanent`, {
        method: "DELETE",
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
    return handleResponse<void>(response);
}

export async function getTags(token: string): Promise<Tag[]> {
    const response = await fetch(`${API_URL}/tags`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`,
        }
    });
    return handleResponse<Tag[]>(response);
}

export async function createTag(token: string, name: string): Promise<Tag> {
    const response = await fetch(`${API_URL}/tags`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name }),
    });

    return handleResponse<Tag>(response);
}

export async function updateTag(token: string, tagId: number, name: string): Promise<Tag> {
    const response = await fetch(`${API_URL}/tags/${tagId}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ name }),
    });
    return handleResponse<Tag>(response);
}

export async function deleteTag(token: string, tagId: number): Promise<void> {
    const response = await fetch(`${API_URL}/tags/${tagId}`, {
        method: "DELETE",
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
    return handleResponse<void>(response);
}

export async function getNoteTags(token: string, noteId: number): Promise<Tag[]> {
    const response = await fetch(`${API_URL}/notes/${noteId}/tags`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
    return handleResponse<Tag[]>(response);
}

export async function addTagToNote(token: string, noteId: number, tagId: number): Promise<void> {
    const response = await fetch(`${API_URL}/notes/${noteId}/tags/${tagId}`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
    return handleResponse<void>(response);
}

export async function removeTagFromNote(token: string, noteId: number, tagId: number): Promise<void> {
    const response = await fetch(`${API_URL}/notes/${noteId}/tags/${tagId}`, {
        method: "DELETE",
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
    return handleResponse<void>(response);
}