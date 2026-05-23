import type { Task, CreateTaskPayload, EditTaskPayload } from './types';
import { getInitData } from './telegram';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const initData = getInitData();
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Telegram-InitData': initData,
      ...options.headers,
    },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export async function getTasks(): Promise<Task[]> {
  return apiFetch<Task[]>('/get_tasks');
}

export async function createTask(payload: CreateTaskPayload): Promise<Task> {
  return apiFetch<Task>('/create_task', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function completeTask(id: number): Promise<Task> {
  return apiFetch<Task>(`/complete_task/${id}`, { method: 'POST' });
}

export async function editTask(id: number, payload: EditTaskPayload): Promise<Task> {
  return apiFetch<Task>(`/edit_task/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export async function deleteTask(id: number): Promise<{ ok: boolean }> {
  return apiFetch<{ ok: boolean }>(`/delete_task/${id}`, { method: 'DELETE' });
}
