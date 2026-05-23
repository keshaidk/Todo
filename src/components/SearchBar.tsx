import { useState, useRef, useEffect } from 'react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  theme: 'light' | 'dark';
}

export default function SearchBar({ value, onChange, theme }: SearchBarProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [focused, setFocused] = useState(false);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg?.BackButton) {
      if (focused) {
        tg.BackButton.show();
        tg.BackButton.onClick(() => {
          inputRef.current?.blur();
        });
      } else {
        tg.BackButton.hide();
      }
    }
  }, [focused]);

  const isDark = theme === 'dark';

  return (
    <div className="relative mb-4">
      <div
        className={`
          flex items-center gap-3 rounded-2xl px-4 py-3 transition-all duration-200
          ${focused
            ? 'ring-2 ring-blue-400 shadow-lg'
            : 'shadow-sm hover:shadow-md'
          }
          ${isDark ? 'bg-white/10 text-white' : 'bg-white text-slate-800'}
        `}
      >
        <svg
          className={`h-5 w-5 flex-shrink-0 ${isDark ? 'text-white/40' : 'text-slate-400'}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder="Поиск задач..."
          className={`
            flex-1 bg-transparent text-base outline-none placeholder:text-slate-400
            ${isDark ? 'text-white placeholder:text-white/30' : ''}
          `}
        />
        {value && (
          <button
            onClick={() => {
              onChange('');
              inputRef.current?.focus();
            }}
            className={`flex-shrink-0 rounded-full p-1 transition-colors ${
              isDark ? 'hover:bg-white/10 text-white/50' : 'hover:bg-slate-100 text-slate-400'
            }`}
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
