import type {Note} from "../stores/notes.ts";

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
    return response.json();
}


export async function getNotes(token: string): Promise<Note[]> {
    const response = await fetch(`${API_URL}/notes`, {
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