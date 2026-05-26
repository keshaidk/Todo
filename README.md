# Telegram To-Do Mini App

A full-stack Telegram Mini App for task management and reminders.

## Features
- ✨ **Modern UI**: Apple/Google Keep style design with smooth animations.
- 🌓 **Theming**: Syncs with Telegram's dark/light theme.
- ⭐️ **Animated Background**: Starry night background for dark mode.
- 🗓️ **Task Grouping**: Automatic grouping into Overdue, Today, Tomorrow, etc.
- 🔔 **Reminders**: Integrated with Telegram Bot API for push notifications.
- 📱 **Haptic Feedback**: Feels like a native app.

## Tech Stack
- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons, Date-fns.
- **Backend**: FastAPI (Python), SQLAlchemy, SQLite.
- **Bot**: `python-telegram-bot` with `APScheduler` for notifications.

## Project Structure
```text
├── src/                # React Frontend
│   ├── components/     # UI Components (DarkBackground, etc.)
│   ├── App.tsx         # Main Logic & UI
│   └── types.ts        # TypeScript Interfaces
├── backend/            # FastAPI Backend & Bot
│   ├── main.py         # API & Bot logic combined
│   └── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Telegram Bot Setup
1. Message [@BotFather](https://t.me/botfather) on Telegram.
2. Create a new bot and get your **API Token**.
3. Enable Inline Mode (optional) and set the Web App URL.

### 2. Backend Setup
1. Navigate to the `backend/` directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables:
   - `BOT_TOKEN`: Your Telegram Bot API Token.
   - `WEBAPP_URL`: The URL where your frontend is hosted (use ngrok for local testing).
4. Run the server:
   ```bash
   python main.py
   ```

### 3. Frontend Setup
1. Install dependencies:
   ```bash
   npm install
   ```
2. Update `API_BASE_URL` in `src/App.tsx` if you have a public backend URL.
3. Start the development server:
   ```bash
   npm run dev
   ```
4. For Telegram to see it, you must use HTTPS. Use `ngrok` or similar to tunnel your local port (usually 5173).

## Deployment

### Local Testing with ngrok
1. Run backend (port 8000) and frontend (port 5173).
2. Tunnel both:
   ```bash
   ngrok http 8000
   ngrok http 5173
   ```
3. Update `WEBAPP_URL` in the bot settings to your ngrok frontend URL.

### Production
- **Frontend**: Deploy to Vercel, Netlify, or GitHub Pages.
- **Backend**: Deploy to Render, Railway, or PythonAnywhere.
- **Database**: The current setup uses SQLite. For production, switch to PostgreSQL by changing `DATABASE_URL`.

## Notes
- To receive push notifications, the user must have started the bot (`/start`).
- The frontend uses `localStorage` for quick demo purposes, but the code is structured to easily integrate with the provided FastAPI endpoints.
