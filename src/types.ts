export interface Task {
  id: number;
  user_id: string;
  text: string;
  completed: boolean;
  reminder_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskPayload {
  user_id: string;
  text: string;
  reminder_date: string | null;
}

export interface EditTaskPayload {
  text?: string;
  completed?: boolean;
  reminder_date?: string | null;
}

export type TaskGroup = 'today' | 'tomorrow' | 'overdue' | 'no_date' | 'later';

export interface TaskGroups {
  today: Task[];
  tomorrow: Task[];
  overdue: Task[];
  no_date: Task[];
  later: Task[];
}
