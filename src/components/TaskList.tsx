import type { Task } from '../types';
import { groupTasks } from '../utils';
import TaskCard from './TaskCard';
import EmptyState from './EmptyState';

interface TaskListProps {
  tasks: Task[];
  searchQuery: string;
  onComplete: (id: number) => void;
  onEdit: (task: Task) => void;
  onDelete: (id: number) => void;
  theme: 'light' | 'dark';
}

const groupLabels: Record<string, string> = {
  today: '📅 Сегодня',
  tomorrow: '🌅 Завтра',
  overdue: '⚠️ Просроченные',
  no_date: '📌 Без даты',
  later: '🗓 Позже',
};

export default function TaskList({ tasks, searchQuery, onComplete, onEdit, onDelete, theme }: TaskListProps) {
  const isDark = theme === 'dark';

  const filtered = searchQuery.trim()
    ? tasks.filter((t) => t.text.toLowerCase().includes(searchQuery.toLowerCase()))
    : tasks;

  const completedTasks = filtered.filter((t) => t.completed);
  const activeTasks = filtered.filter((t) => !t.completed);

  if (filtered.length === 0) {
    return <EmptyState theme={theme} hasSearch={!!searchQuery.trim()} />;
  }

  const groups = groupTasks(activeTasks);
  const groupOrder = ['today', 'tomorrow', 'overdue', 'no_date', 'later'] as const;

  return (
    <div className="space-y-6">
      {groupOrder.map((key) => {
        const groupItems = groups[key];
        if (groupItems.length === 0) return null;
        return (
          <div key={key} className="space-y-2">
            <h3
              className={`text-xs font-semibold uppercase tracking-widest pl-1 ${
                isDark ? 'text-white/50' : 'text-slate-400'
              }`}
            >
              {groupLabels[key]}
              <span className="ml-2 font-normal normal-case text-xs tracking-normal">
                ({groupItems.length})
              </span>
            </h3>
            <div className="space-y-1">
              {groupItems.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onComplete={onComplete}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  theme={theme}
                />
              ))}
            </div>
          </div>
        );
      })}

      {completedTasks.length > 0 && (
        <div className="space-y-2">
          <details open={completedTasks.length <= 3}>
            <summary
              className={`cursor-pointer text-xs font-semibold uppercase tracking-widest pl-1 ${
                isDark ? 'text-white/50 hover:text-white/70' : 'text-slate-400 hover:text-slate-500'
              }`}
            >
              ✅ Выполнено
              <span className="ml-2 font-normal normal-case text-xs tracking-normal">
                ({completedTasks.length})
              </span>
            </summary>
            <div className="mt-2 space-y-1">
              {completedTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onComplete={onComplete}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  theme={theme}
                />
              ))}
            </div>
          </details>
        </div>
      )}
    </div>
  );
}
