# To-Do

```
.
├── backend/
│   ├── main.py
│   ├── bot.py 
│   ├── models.py
│   ├── notifier.py
│   ├── run.py
│   ├── requirements.txt
│   └── Dockerfile
├── src/
│   ├── App.tsx           # Главный компонент
│   ├── main.tsx          # Точка входа
│   ├── types.ts          # TypeScript типы
│   ├── api.ts            # API-клиент
│   ├── telegram.ts       # Telegram WebApp SDK хелперы
│   ├── utils.ts          # Утилиты (группировка, форматирование)
│   ├── index.css         # Глобальные стили (Tailwind CSS v4)
│   └── components/
│       ├── TaskCard.tsx   # Карточка задачи
│       ├── TaskForm.tsx   # Форма создания/редактирования
│       ├── TaskList.tsx   # Список с группировкой
│       ├── SearchBar.tsx  # Поиск
│       ├── ThemeToggle.tsx # Переключатель темы
│       └── EmptyState.tsx # Пустое состояние
├── index.html
├── vite.config.ts        # Vite + Tailwind + single-file плагин
├── Procfile              # Для деплоя на Render / Heroku
├── runtime.txt           # Версия Python
└── README.md
```