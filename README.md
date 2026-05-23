# ✅ To-Do Telegram Mini App

Полнофункциональный Telegram Mini App для управления задачами и напоминаниями.

**Стек:** FastAPI + React (Vite + Tailwind CSS) + Telegram Bot API + SQLite

## 🎯 Возможности

- 📝 Создание задач с напоминаниями (дата + время)
- 📅 Группировка задач: Сегодня, Завтра, Просроченные, Без даты, Позже
- ✅ Отметка о выполнении с уведомлением в Telegram
- ✏️ Редактирование задачи по клику
- 🗑 Удаление с подтверждением
- 🔍 Поиск и фильтрация по задачам
- 🌓 Тёмная / светлая тема (адаптируется под настройки Telegram)
- 📱 Адаптивный дизайн в стиле Apple Notes / Google Keep
- 🔔 Push-напоминания прямо в чат Telegram
- 🤖 Команда `/start` с кнопкой запуска Web App

## 📁 Структура проекта

```
.
├── backend/
│   ├── main.py           # FastAPI сервер
│   ├── bot.py            # Telegram бот (python-telegram-bot)
│   ├── models.py         # Модели и работа с SQLite
│   ├── notifier.py       # Уведомления о выполнении задач
│   ├── run.py            # Запуск API + бота вместе
│   ├── requirements.txt  # Python зависимости
│   └── Dockerfile        # Docker-контейнер
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

## 🚀 Быстрый старт (локально)

### 1. Клонирование и установка

```bash
# Установка фронтенда
npm install

# Установка бэкенда
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Создание Telegram бота

1. Открой [@BotFather](https://t.me/BotFather) в Telegram
2. Создай бота командой `/newbot`
3. Скопируй полученный токен (формат: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Настрой кнопку меню для бота:

```
/mybots → выбери бота → Bot Settings → Menu Button
→ Configure menu button → URL кнопки
```

Укажи URL, где будет размещён твой Web App (например, `https://yourapp.onrender.com/todo`)

### 3. Настройка переменных окружения

Создай файл `.env` в папке `backend/`:

```bash
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
WEB_APP_URL=https://yourapp.onrender.com
```

### 4. Запуск

**Фронтенд (разработка):**

```bash
npm run dev
# Откроется на http://localhost:5173
```

**Бэкенд + Бот:**

```bash
cd backend
python run.py
# API: http://localhost:8000
# Бот запустится и начнёт polling
```

### 5. Тестирование Web App с ngrok

Для локального тестирования с Telegram:

```bash
# Терминал 1 — бэкенд
cd backend && python run.py

# Терминал 2 — фронтенд
npm run dev

# Терминал 3 — ngrok для бэкенда
ngrok http 8000

# Терминал 4 — ngrok для фронтенда
ngrok http 5173
```

Обнови `WEB_APP_URL` на ngrok-URL фронтенда, а в BotFather укажи ngrok-URL бэкенда.

## 🌐 Деплой

### Вариант 1: Render (рекомендуется, бесплатный)

1. Залей проект на GitHub
2. Зайди на [render.com](https://render.com)
3. **New → Web Service**
4. Подключи репозиторий
5. Настройки:
   - **Name:** todo-telegram-bot
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt && npm install && npm run build`
   - **Start Command:** `cd backend && python run.py`
   - **Environment Variables:**
     - `BOT_TOKEN` — токен бота
     - `WEB_APP_URL` — URL, который даст Render (например, `https://todo-telegram-bot.onrender.com`)

6. После деплоя скопируй URL из Render и укажи его в BotFather как Menu Button URL.

> ⚠️ **Важно:** Бесплатные инстансы Render засыпают после 15 минут неактивности. Для "прогрева" можно использовать внешний cron-сервис (например, [cron-job.org](https://cron-job.org)) для периодического пинга `/health` эндпоинта.

### Вариант 2: PythonAnywhere

1. Зарегистрируйся на [pythonanywhere.com](https://pythonanywhere.com)
2. Загрузи файлы из `backend/` через Web-интерфейс или Git
3. Создай веб-приложение (Manual Config → Python 3.11)
4. Укажи путь к виртуальному окружению и установи зависимости:

```bash
pip install -r requirements.txt
```

5. В `WSGI configuration file` добавь:

```python
import sys
sys.path.insert(0, '/home/YOUR_USERNAME/todo-backend')

from main import app as application
```

6. Для бота создай Always-On Task или используй консоль:

```bash
python bot.py
```

### Вариант 3: Heroku

```bash
heroku create todo-telegram-miniapp
heroku config:set BOT_TOKEN=YOUR_TOKEN
heroku config:set WEB_APP_URL=https://todo-telegram-miniapp.herokuapp.com
git push heroku main
```

## 🔧 API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/health` | Проверка здоровья |
| `GET` | `/get_tasks` | Получить все задачи пользователя |
| `POST` | `/create_task` | Создать задачу |
| `POST` | `/complete_task/{id}` | Отметить выполнение (toggle) |
| `PUT` | `/edit_task/{id}` | Редактировать задачу |
| `DELETE` | `/delete_task/{id}` | Удалить задачу |

**Аутентификация:** Заголовок `X-Telegram-InitData` с валидными данными от Telegram WebApp SDK.

### Пример тела запроса (create_task):

```json
{
  "user_id": "123456789",
  "text": "Купить молоко",
  "reminder_date": "2026-03-15T18:30:00"
}
```

## 🎨 Дизайн

Приложение стилизовано в духе Apple Notes / Google Keep:

- Чистый минимализм
- Скруглённые карточки задач
- Плавные анимации (hover, переходы, появление)
- Эмодзи-иконки для групп
- Адаптивная тёмная и светлая темы
- Тактильная обратная связь через Telegram HapticFeedback

## 📝 Лицензия

MIT

---

Сделано с ❤️ для Telegram Mini Apps
