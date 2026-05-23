import type { Task, TaskGroups } from './types';
import { format, isToday, isTomorrow, isPast, parseISO } from 'date-fns';

export function groupTasks(tasks: Task[]): TaskGroups {
  const groups: TaskGroups = {
    today: [],
    tomorrow: [],
    overdue: [],
    no_date: [],
    later: [],
  };

  for (const task of tasks) {
    if (task.completed) continue;

    if (!task.reminder_date) {
      groups.no_date.push(task);
      continue;
    }

    const reminderDate = parseISO(task.reminder_date);

    if (isPast(reminderDate) && !isToday(reminderDate)) {
      groups.overdue.push(task);
    } else if (isToday(reminderDate)) {
      groups.today.push(task);
    } else if (isTomorrow(reminderDate)) {
      groups.tomorrow.push(task);
    } else {
      groups.later.push(task);
    }
  }

  return groups;
}

export function formatReminder(date: string | null): string {
  if (!date) return '';
  try {
    const d = parseISO(date);
    if (isToday(d)) return `Сегодня в ${format(d, 'HH:mm')}`;
    if (isTomorrow(d)) return `Завтра в ${format(d, 'HH:mm')}`;
    return format(d, 'dd.MM.yyyy HH:mm');
  } catch {
    return '';
  }
}

export function isOverdue(task: Task): boolean {
  if (!task.reminder_date || task.completed) return false;
  try {
    const d = parseISO(task.reminder_date);
    return isPast(d) && !isToday(d);
  } catch {
    return false;
  }
}
