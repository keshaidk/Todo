import type { Task, CreateTaskPayload, EditTaskPayload } from './types';
import { getInitData } from './telegram';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface TasksResponse {
  tasks: Task[];
  total: number;
  completed_count: number;
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const initData = getInitData();
  
  if (!initData) {
    throw new Error('Not authenticated. Telegram init data missing.');
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Init-Data': initData,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status}`;
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || errorDetail;
    } catch {
      // Parse error failed
    }
    throw new Error(errorDetail);
  }

  if (response.status === 204) {
    return {} as T; // No content
  }

  return response.json();
}

export async function getTasks(): Promise<Task[]> {
  const data = await apiFetch<TasksResponse>('/tasks');
  return data.tasks;
}

export async function createTask(payload: CreateTaskPayload): Promise<Task> {
  return apiFetch<Task>('/tasks', {
    method: 'POST',
    body: JSON.stringify({
      text: payload.text,
      reminder_date: payload.reminder_date || null,
    }),
  });
}

export async function completeTask(id: number): Promise<Task> {
  return apiFetch<Task>(`/tasks/${id}/complete`, { method: 'POST' });
}

export async function updateTask(id: number, payload: EditTaskPayload): Promise<Task> {
  return apiFetch<Task>(`/tasks/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export async function deleteTask(id: number): Promise<void> {
  await apiFetch<void>(`/tasks/${id}`, { method: 'DELETE' });
}

export async function editTask(id: number, payload: EditTaskPayload): Promise<Task> {
  return updateTask(id, payload);
}

export async function checkHealth(): Promise<{ status: string; version: string }> {
  return apiFetch('/health');
}
