import { useState, useEffect, useMemo, useCallback } from 'react';
import { 
  Plus, 
  Trash2, 
  CheckCircle2, 
  Circle, 
  Calendar, 
  Search, 
  Clock, 
  ChevronRight,
  ChevronDown,
  X,
  Moon,
  Sun
} from 'lucide-react';
import { format, isToday, isTomorrow, isPast, parseISO } from 'date-fns';
import { DarkBackground } from './components/DarkBackground';
import { Task, TaskGroup } from './types';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Helper for tailwind classes
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Telegram WebApp Mock/Type
declare global {
  interface Window {
    Telegram: {
      WebApp: any;
    };
  }
}

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [inputText, setInputText] = useState('');
  const [inputDate, setInputDate] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [tg, setTg] = useState<any>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('theme');
    return (saved as 'light' | 'dark') || 'dark';
  });
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    'Overdue': true,
    'Today': true,
    'Tomorrow': true,
    'Upcoming': true,
    'No Date': true
  });

  // Sync theme with document class
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    document.documentElement.style.colorScheme = theme;
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Initialize Telegram WebApp
  useEffect(() => {
    if (window.Telegram?.WebApp) {
      const tgApp = window.Telegram.WebApp;
      tgApp.ready();
      tgApp.expand();
      setTg(tgApp);
    }
  }, []);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    if (tg) tg.HapticFeedback.impactOccurred('light');
  };

  // Load tasks from localStorage (or API)
  useEffect(() => {
    const saved = localStorage.getItem('tasks');
    if (saved) {
      try {
        setTasks(JSON.parse(saved));
      } catch (e) {
        console.error("Failed to parse tasks", e);
      }
    }
  }, []);

  // Save tasks
  useEffect(() => {
    localStorage.setItem('tasks', JSON.stringify(tasks));
  }, [tasks]);

  const addTask = useCallback(() => {
    if (!inputText.trim()) return;

    const newTask: Task = {
      id: Date.now().toString(),
      text: inputText.trim(),
      completed: false,
      reminderDate: inputDate ? new Date(inputDate).toISOString() : undefined,
      createdAt: new Date().toISOString(),
    };

    setTasks(prev => [newTask, ...prev]);
    setInputText('');
    setInputDate('');
    setIsAdding(false);

    if (tg) {
      tg.HapticFeedback.notificationOccurred('success');
    }
  }, [inputText, inputDate, tg]);

  const toggleTask = (id: string) => {
    setTasks(prev => {
      const newTasks = prev.map(t => {
        if (t.id === id) {
          const newState = !t.completed;
          if (newState && tg) {
            tg.HapticFeedback.impactOccurred('medium');
            tg.sendData(JSON.stringify({ type: 'task_completed', task: t.text }));
          }
          return { ...t, completed: newState };
        }
        return t;
      });
      return newTasks;
    });
  };

  const deleteTask = (id: string) => {
    setTasks(prev => prev.filter(t => t.id !== id));
    if (tg) tg.HapticFeedback.impactOccurred('light');
  };

  const editTask = (id: string, newText: string) => {
    setTasks(prev => prev.map(t => t.id === id ? { ...t, text: newText } : t));
  };

  const groupedTasks = useMemo(() => {
    const filtered = tasks.filter(t => 
      t.text.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const groups: Record<TaskGroup, Task[]> = {
      'Overdue': [],
      'Today': [],
      'Tomorrow': [],
      'Upcoming': [],
      'No Date': []
    };

    filtered.forEach(task => {
      if (!task.reminderDate) {
        groups['No Date'].push(task);
        return;
      }

      const date = parseISO(task.reminderDate);
      if (isPast(date) && !isToday(date) && !task.completed) {
        groups['Overdue'].push(task);
      } else if (isToday(date)) {
        groups['Today'].push(task);
      } else if (isTomorrow(date)) {
        groups['Tomorrow'].push(task);
      } else {
        groups['Upcoming'].push(task);
      }
    });

    return groups;
  }, [tasks, searchQuery]);

  const toggleGroup = (group: string) => {
    setExpandedGroups(prev => ({ ...prev, [group]: !prev[group] }));
  };

  const TaskItem = ({ task }: { task: Task }) => (
    <div 
      className={cn(
        "group flex items-center gap-3 p-4 border rounded-2xl mb-2 transition-all duration-300",
        "bg-white dark:bg-white/5 backdrop-blur-sm border-slate-300 dark:border-white/10 shadow-sm shadow-slate-200/70 dark:shadow-none hover:border-slate-400 hover:shadow-md dark:hover:border-white/20 dark:hover:bg-white/[0.08]",
        task.completed && "opacity-60"
      )}
    >
      <button 
        onClick={() => toggleTask(task.id)}
        className="text-blue-500 dark:text-blue-400 hover:scale-110 transition-transform"
      >
        {task.completed ? (
          <CheckCircle2 className="w-6 h-6 fill-current" />
        ) : (
          <Circle className="w-6 h-6" />
        )}
      </button>

      <div className="flex-1 overflow-hidden">
        <input 
          value={task.text}
          onChange={(e) => editTask(task.id, e.target.value)}
          className={cn(
            "bg-transparent border-none focus:ring-0 w-full text-[17px] outline-none transition-colors",
            "text-slate-950 dark:text-slate-50 placeholder:text-slate-500 dark:placeholder:text-slate-500",
            task.completed && "line-through text-slate-400 dark:text-slate-500"
          )}
        />
        {task.reminderDate && (
          <div className="flex items-center gap-1 text-xs font-medium text-slate-600 dark:text-slate-400 mt-1">
            <Clock className="w-3 h-3" />
            {format(parseISO(task.reminderDate), 'MMM d, HH:mm')}
          </div>
        )}
      </div>

      <button 
        onClick={() => deleteTask(task.id)}
        className="opacity-0 group-hover:opacity-100 p-2 text-slate-400 hover:text-red-500 dark:hover:text-red-400 transition-all"
      >
        <Trash2 className="w-5 h-5" />
      </button>
    </div>
  );

  return (
    <div className={cn(
      "min-h-screen font-sans pb-24 selection:bg-blue-500/30 transition-colors duration-500 relative",
      theme === 'dark' ? "bg-[#020617] text-slate-100" : "bg-[#f3f6fb] text-slate-950"
    )}>
      {theme === 'dark' && <DarkBackground />}
      
      {/* Header */}
      <header className={cn(
        "sticky top-0 z-20 px-6 pt-12 pb-6 backdrop-blur-lg border-b transition-colors duration-500",
        theme === 'dark' ? "bg-[#020617]/70 border-white/5" : "bg-white/95 border-slate-300 shadow-sm shadow-slate-200/70"
      )}>
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold tracking-tight">Tasks</h1>
          <div className="flex items-center gap-3">
            <button 
              onClick={toggleTheme}
              className="p-2 rounded-full bg-slate-900 dark:bg-white/10 text-white dark:text-yellow-400 border border-slate-900 dark:border-white/10 transition-all hover:scale-110 active:scale-95 shadow-sm"
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            {tg?.initDataUnsafe?.user?.photo_url && (
              <img 
                src={tg.initDataUnsafe.user.photo_url} 
                alt="Profile" 
                className="w-8 h-8 rounded-full border border-slate-200 dark:border-white/20"
              />
            )}
          </div>
        </div>

        {/* Search */}
        <div className="relative group">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 dark:text-slate-500 group-focus-within:text-blue-500 transition-colors" />
          <input 
            type="text" 
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white dark:bg-white/5 border border-slate-300 dark:border-white/10 rounded-2xl py-3 pl-11 pr-4 text-[16px] outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500 transition-all text-slate-950 dark:text-slate-100 placeholder:text-slate-500 dark:placeholder:text-slate-500 shadow-sm shadow-slate-200/70 dark:shadow-none"
          />
        </div>
      </header>

      {/* Task Groups */}
      <main className="px-6 py-6 max-w-2xl mx-auto">
        {(Object.entries(groupedTasks) as [TaskGroup, Task[]][]).map(([group, groupTasks]) => (
          groupTasks.length > 0 && (
            <div key={group} className="mb-8">
              <button 
                onClick={() => toggleGroup(group)}
                className="flex items-center gap-2 w-full mb-3 text-sm font-extrabold text-slate-700 dark:text-slate-400 uppercase tracking-widest"
              >
                {expandedGroups[group] ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                {group}
                <span className="ml-auto bg-slate-900 dark:bg-white/10 text-white dark:text-slate-300 px-2 py-0.5 rounded-full text-[10px] font-mono">
                  {groupTasks.length}
                </span>
              </button>
              
              {expandedGroups[group] && (
                <div className="space-y-1 animate-in fade-in slide-in-from-top-2 duration-300">
                  {groupTasks.map(task => (
                    <TaskItem key={task.id} task={task} />
                  ))}
                </div>
              )}
            </div>
          )
        ))}

        {tasks.length === 0 && !isAdding && (
          <div className="flex flex-col items-center justify-center py-20 text-slate-600 dark:text-slate-500">
            <div className="w-20 h-20 bg-white dark:bg-white/5 border border-slate-300 dark:border-white/10 rounded-full flex items-center justify-center mb-6 shadow-sm dark:shadow-none">
              <CheckCircle2 className="w-10 h-10 opacity-30" />
            </div>
            <p className="text-xl font-bold mb-1">All caught up!</p>
            <p className="text-sm opacity-80 font-medium">Tap + to add a new task</p>
          </div>
        )}
      </main>

      {/* Floating Action Button / Add Modal */}
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 w-full max-w-md px-6 z-50">
        {isAdding ? (
          <div className="bg-white dark:bg-slate-900/90 backdrop-blur-xl border border-slate-300 dark:border-white/10 rounded-3xl p-6 shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">New Task</h3>
              <button onClick={() => setIsAdding(false)} className="p-1 hover:bg-slate-100 dark:hover:bg-white/10 rounded-full transition-colors">
                <X className="w-5 h-5 text-slate-400" />
              </button>
            </div>
            
            <input 
              autoFocus
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="What needs to be done?"
              className="w-full bg-transparent border-none focus:ring-0 text-lg mb-4 p-0 outline-none text-slate-950 dark:text-white placeholder:text-slate-500 dark:placeholder:text-slate-500"
              onKeyDown={(e) => e.key === 'Enter' && addTask()}
            />

            <div className="flex flex-wrap items-center gap-4 mb-6">
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-blue-500" />
                <input 
                  type="datetime-local" 
                  value={inputDate}
                  onChange={(e) => setInputDate(e.target.value)}
                  className="bg-slate-50 dark:bg-white/5 border border-slate-300 dark:border-white/10 rounded-xl py-2 pl-10 pr-4 text-sm outline-none focus:ring-1 ring-blue-500/50 text-slate-950 dark:text-white"
                />
              </div>
            </div>

            <button 
              onClick={addTask}
              disabled={!inputText.trim()}
              className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:hover:bg-blue-600 text-white font-bold py-3 rounded-2xl transition-all shadow-lg shadow-blue-600/20 active:scale-95"
            >
              Create Task
            </button>
          </div>
        ) : (
          <button 
            onClick={() => {
              setIsAdding(true);
              if (tg) tg.HapticFeedback.impactOccurred('medium');
            }}
            className="w-14 h-14 bg-blue-600 hover:bg-blue-500 text-white rounded-full flex items-center justify-center shadow-2xl shadow-blue-600/40 ml-auto transition-transform active:scale-90"
          >
            <Plus className="w-8 h-8" />
          </button>
        )}
      </div>
    </div>
  );
}
