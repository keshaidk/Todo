import { useState } from 'react';
import type { Task } from '../types';
import { formatReminder, isOverdue } from '../utils';

interface TaskCardProps {
  task: Task;
  onComplete: (id: number) => void;
  onEdit: (task: Task) => void;
  onDelete: (id: number) => void;
  theme: 'light' | 'dark';
}

export default function TaskCard({ task, onComplete, onEdit, onDelete, theme }: TaskCardProps) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [swiping] = useState(false);

  const isDark = theme === 'dark';
  const overdue = isOverdue(task);

  return (
    <div
      className={`
        group relative mb-2 overflow-hidden rounded-2xl transition-all duration-200
        ${task.completed ? 'opacity-60' : ''}
        ${isDark ? 'bg-white/[0.04] hover:bg-white/[0.07]' : 'bg-white hover:shadow-md'}
        ${swiping ? 'translate-x-[-80px]' : ''}
      `}
    >
      <div className="flex items-start gap-3 px-4 py-3">
        {/* Checkbox */}
        <button
          onClick={() => {
            onComplete(task.id);
            const tg = window.Telegram?.WebApp;
            tg?.HapticFeedback?.notificationOccurred?.(task.completed ? 'warning' : 'success');
          }}
          className={`
            mt-[3px] flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full border-2 transition-all duration-200
            ${task.completed
              ? 'border-green-400 bg-green-400'
              : isDark
                ? 'border-white/20 hover:border-white/40'
                : 'border-slate-300 hover:border-blue-400'
            }
          `}
        >
          {task.completed && (
            <svg className="h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p
            className={`
              text-[15px] leading-snug cursor-pointer
              ${task.completed ? 'line-through opacity-50' : ''}
              ${isDark ? 'text-white' : 'text-slate-800'}
            `}
            onClick={() => onEdit(task)}
          >
            {task.text}
          </p>
          {task.reminder_date && (
            <p
              className={`
                mt-1 text-xs font-medium
                ${overdue && !task.completed
                  ? 'text-red-400'
                  : isDark ? 'text-white/40' : 'text-slate-400'
                }
              `}
            >
              {overdue && !task.completed ? '⚠️ ' : ''}
              {formatReminder(task.reminder_date)}
              {overdue && !task.completed ? ' (просрочено)' : ''}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex flex-shrink-0 items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onEdit(task)}
            className={`rounded-lg p-1.5 transition-colors ${
              isDark ? 'hover:bg-white/10 text-white/50' : 'hover:bg-slate-100 text-slate-400'
            }`}
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className={`rounded-lg p-1.5 transition-colors ${
              isDark ? 'hover:bg-red-500/20 text-white/50 hover:text-red-400' : 'hover:bg-red-50 text-slate-400 hover:text-red-500'
            }`}
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      {/* Delete confirmation */}
      {showDeleteConfirm && (
        <div
          className={`
            absolute inset-0 flex items-center justify-center gap-3 rounded-2xl backdrop-blur-sm
            ${isDark ? 'bg-slate-900/90' : 'bg-white/90'}
          `}
        >
          <span className={`text-sm font-medium ${isDark ? 'text-white' : 'text-slate-700'}`}>
            Удалить?
          </span>
          <button
            onClick={() => {
              onDelete(task.id);
              setShowDeleteConfirm(false);
            }}
            className="rounded-lg bg-red-500 px-3 py-1 text-xs font-semibold text-white hover:bg-red-600 transition-colors"
          >
            Да
          </button>
          <button
            onClick={() => setShowDeleteConfirm(false)}
            className={`rounded-lg px-3 py-1 text-xs font-semibold transition-colors ${
              isDark ? 'bg-white/10 text-white hover:bg-white/20' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Нет
          </button>
        </div>
      )}
    </div>
  );
}
