interface EmptyStateProps {
  theme: 'light' | 'dark';
  hasSearch: boolean;
}

export default function EmptyState({ theme, hasSearch }: EmptyStateProps) {
  const isDark = theme === 'dark';

  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="mb-4 text-6xl">
        {hasSearch ? '🔍' : '📋'}
      </div>
      <h3
        className={`text-lg font-semibold mb-1 ${isDark ? 'text-white/80' : 'text-slate-600'}`}
      >
        {hasSearch ? 'Ничего не найдено' : 'Пока нет задач'}
      </h3>
      <p className={`text-sm ${isDark ? 'text-white/40' : 'text-slate-400'}`}>
        {hasSearch
          ? 'Попробуйте изменить поисковый запрос'
          : 'Создайте первую задачу и начните планировать!'}
      </p>
    </div>
  );
}
