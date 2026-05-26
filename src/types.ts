export interface Task {
  id: string;
  text: string;
  completed: boolean;
  reminderDate?: string; // ISO string
  createdAt: string;
}

export type TaskGroup = 'Overdue' | 'Today' | 'Tomorrow' | 'Upcoming' | 'No Date';
