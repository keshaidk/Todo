import { useState, useEffect, useCallback } from 'react';
import type { Task } from './types';
import { getUserId, getColorScheme } from './telegram';
import { getTasks, createTask, completeTask, editTask, deleteTask } from './api';
import TaskForm from './components/TaskForm';
import TaskList from './components/TaskList';
import SearchBar from './components/SearchBar';
import ThemeToggle from './components/ThemeToggle';

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>(getColorScheme());
  const [userId] = useState(getUserId());

  const isDark = theme === 'dark';

  // Apply theme to Telegram WebApp
  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.ready();
      tg.expand();
      if (isDark) {
        tg.headerColor = '#0f172a';
        tg.backgroundColor = '#0f172a';
      } else {
        tg.headerColor = '#f8fafc';
        tg.backgroundColor = '#f8fafc';
      }
    }
  }, [isDark]);

  // Listen for Telegram theme changes
  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      const handler = () => {
        setTheme(tg.colorScheme);
      };
      tg.onEvent('themeChanged', handler);
      return () => {
        tg.offEvent('themeChanged', handler);
      };
    }
  }, []);

  // Fetch tasks
  const fetchTasks = useCallback(async () => {
    try {
      setError(null);
      const data = await getTasks();
      setTasks(data);
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки задач');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Handle create task
  const handleCreate = useCallback(async (text: string, reminderDate: string | null) => {
    try {
      const newTask = await createTask({
        user_id: userId,
        text,
        reminder_date: reminderDate,
      });
      setTasks((prev) => [newTask, ...prev]);
      const tg = window.Telegram?.WebApp;
      tg?.HapticFeedback?.notificationOccurred?.('success');
    } catch (err: any) {
      setError(err.message);
    }
  }, [userId]);

  // Handle complete task
  const handleComplete = useCallback(async (id: number) => {
    try {
      const updated = await completeTask(id);
      setTasks((prev) =>
        prev.map((t) => (t.id === id ? updated : t))
      );
    } catch (err: any) {
      setError(err.message);
    }
  }, []);

  // Handle edit task
  const handleEdit = useCallback(async (task: Task) => {
    if (editingTask?.id === task.id) {
      // Already editing - save
      setEditingTask(null);
      try {
        if (task.text !== editingTask.text || task.reminder_date !== editingTask.reminder_date) {
          const updated = await editTask(task.id, {
            text: task.text,
            reminder_date: task.reminder_date,
          });
          setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
        }
      } catch (err: any) {
        setError(err.message);
      }
    } else {
      // Start editing
      setEditingTask(task);
    }
  }, [editingTask]);

  // Handle save edit
  const handleSaveEdit = useCallback(async (text: string, reminderDate: string | null) => {
    if (!editingTask) return;
    try {
      const updated = await editTask(editingTask.id, {
        text,
        reminder_date: reminderDate,
      });
      setTasks((prev) => prev.map((t) => (t.id === editingTask.id ? updated : t)));
      setEditingTask(null);
      const tg = window.Telegram?.WebApp;
      tg?.HapticFeedback?.notificationOccurred?.('success');
    } catch (err: any) {
      setError(err.message);
    }
  }, [editingTask]);

  // Handle delete task
  const handleDelete = useCallback(async (id: number) => {
    try {
      await deleteTask(id);
      setTasks((prev) => prev.filter((t) => t.id !== id));
      if (editingTask?.id === id) setEditingTask(null);
      const tg = window.Telegram?.WebApp;
      tg?.HapticFeedback?.notificationOccurred?.('warning');
    } catch (err: any) {
      setError(err.message);
    }
  }, [editingTask]);

  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  }, []);

  return (
    <div
      className={`min-h-screen transition-colors duration-300 ${
        isDark ? 'bg-slate-900' : 'bg-gradient-to-br from-slate-50 via-white to-blue-50'
      }`}
    >
      <div className="mx-auto max-w-2xl px-4 py-4 pb-24">
        {/* Header */}
        <header className="mb-6 flex items-center justify-between">
          <div>
            <h1
              className={`text-2xl font-bold tracking-tight ${
                isDark ? 'text-white' : 'text-slate-900'
              }`}
            >
              ✅ To-Do
            </h1>
            <p className={`text-xs ${isDark ? 'text-white/40' : 'text-slate-400'}`}>
              Telegram Mini App
            </p>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle theme={theme} onToggle={toggleTheme} />

            {/* Back to bot button */}
            <button
              onClick={() => {
                const tg = window.Telegram?.WebApp;
                if (tg) {
                  tg.close();
                }
              }}
              className={`
                inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-medium
                transition-all active:scale-95
                ${isDark
                  ? 'bg-white/10 text-white/70 hover:bg-white/20'
                  : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                }
              `}
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              В бот
            </button>
          </div>
        </header>

        {/* Error banner */}
        {error && (
          <div className="mb-4 flex items-center gap-2 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600 dark:bg-red-500/10 dark:text-red-400">
            <span>⚠️</span>
            <span className="flex-1">{error}</span>
            <button onClick={() => setError(null)} className="font-semibold hover:underline">
              ✕
            </button>
          </div>
        )}

        {/* Search */}
        <SearchBar value={searchQuery} onChange={setSearchQuery} theme={theme} />

        {/* Task creation / editing form */}
        {editingTask ? (
          <TaskForm
            onSubmit={handleSaveEdit}
            editingTask={editingTask}
            onCancel={() => setEditingTask(null)}
            theme={theme}
          />
        ) : (
          <TaskForm onSubmit={handleCreate} theme={theme} />
        )}

        {/* Task list */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-3">
              <div
                className={`h-8 w-8 animate-spin rounded-full border-3 border-transparent ${
                  isDark ? 'border-t-white/60 border-r-white/20' : 'border-t-blue-400 border-r-blue-200'
                }`}
              />
              <span className={`text-sm ${isDark ? 'text-white/40' : 'text-slate-400'}`}>
                Загрузка задач...
              </span>
            </div>
          </div>
        ) : (
          <TaskList
            tasks={tasks}
            searchQuery={searchQuery}
            onComplete={handleComplete}
            onEdit={handleEdit}
            onDelete={handleDelete}
            theme={theme}
          />
        )}
      </div>
    </div>
  );
}
