import { useState } from 'react';
import type { Task } from '../types';

interface TaskFormProps {
  onSubmit: (text: string, reminderDate: string | null) => void;
  editingTask?: Task | null;
  onCancel?: () => void;
  theme: 'light' | 'dark';
}

export default function TaskForm({ onSubmit, editingTask, onCancel, theme }: TaskFormProps) {
  const [text, setText] = useState(editingTask?.text || '');
  const [reminderDate, setReminderDate] = useState(editingTask?.reminder_date || '');
  const [showDatePicker, setShowDatePicker] = useState(!!editingTask?.reminder_date);

  const isDark = theme === 'dark';
  const isEditing = !!editingTask;

  const handleSubmit = () => {
    const trimmed = text.trim();
    if (!trimmed) return;
    onSubmit(trimmed, reminderDate || null);
    if (!isEditing) {
      setText('');
      setReminderDate('');
      setShowDatePicker(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const clearDate = () => {
    setReminderDate('');
    setShowDatePicker(false);
  };

  return (
    <div
      className={`
        mb-6 overflow-hidden rounded-2xl border transition-all duration-200
        ${isDark ? 'border-white/10 bg-white/5' : 'border-slate-100 bg-white shadow-sm'}
      `}
    >
      <div className="p-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="📝 Что нужно сделать?"
          rows={2}
          className={`
            w-full resize-none bg-transparent text-base outline-none placeholder:text-slate-400
            ${isDark ? 'text-white placeholder:text-white/30' : 'text-slate-800'}
          `}
          autoFocus
        />

        {showDatePicker && (
          <div className="mt-3 flex items-center gap-2">
            <div className="relative flex-1">
              <input
                type="datetime-local"
                value={reminderDate}
                onChange={(e) => setReminderDate(e.target.value)}
                className={`
                  w-full rounded-xl px-3 py-2 text-sm outline-none border transition-colors
                  ${isDark
                    ? 'border-white/10 bg-white/5 text-white [color-scheme:dark]'
                    : 'border-slate-200 bg-slate-50 text-slate-700'
                  }
                  focus:ring-2 focus:ring-blue-400
                `}
              />
            </div>
            <button
              onClick={clearDate}
              className={`rounded-xl p-2 transition-colors ${
                isDark ? 'hover:bg-white/10 text-white/50' : 'hover:bg-slate-100 text-slate-400'
              }`}
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
      </div>

      <div
        className={`
          flex items-center justify-between px-4 py-2
          ${isDark ? 'border-t border-white/5 bg-white/[0.02]' : 'border-t border-slate-50 bg-slate-50/50'}
        `}
      >
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowDatePicker(!showDatePicker)}
            className={`
              inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-sm font-medium transition-all
              ${showDatePicker
                ? 'bg-blue-500 text-white shadow-sm'
                : isDark
                  ? 'text-white/60 hover:bg-white/10 hover:text-white'
                  : 'text-slate-500 hover:bg-slate-100 hover:text-slate-700'
              }
            `}
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {reminderDate ? '🕐' : '⏰'}
          </button>
        </div>

        <div className="flex items-center gap-2">
          {isEditing && onCancel && (
            <button
              onClick={onCancel}
              className={`
                rounded-xl px-4 py-1.5 text-sm font-medium transition-all
                ${isDark ? 'text-white/60 hover:bg-white/10' : 'text-slate-500 hover:bg-slate-100'}
              `}
            >
              Отмена
            </button>
          )}
          <button
            onClick={handleSubmit}
            disabled={!text.trim()}
            className={`
              rounded-xl px-5 py-1.5 text-sm font-semibold transition-all
              ${text.trim()
                ? 'bg-blue-500 text-white shadow-sm hover:bg-blue-600 active:scale-[0.97]'
                : isDark
                  ? 'bg-white/5 text-white/20 cursor-not-allowed'
                  : 'bg-slate-100 text-slate-300 cursor-not-allowed'
              }
            `}
          >
            {isEditing ? '💾 Сохранить' : '✨ Создать'}
          </button>
        </div>
      </div>
    </div>
  );
}
