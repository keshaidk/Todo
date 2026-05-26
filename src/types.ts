export interface Task {
  id: number;
  text: string;
  completed: boolean;
  reminder_date?: string | null; // ISO string or null
  created_at: string;
  updated_at: string;
}

export interface CreateTaskPayload {
  text: string;
  reminder_date?: string | null;
}

export interface EditTaskPayload {
  text?: string;
  completed?: boolean;
  reminder_date?: string | null;
}

export type TaskGroup = 'Overdue' | 'Today' | 'Tomorrow' | 'Upcoming' | 'No Date';
