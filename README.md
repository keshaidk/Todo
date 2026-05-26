# Telegram To-Do Mini App

A modern, production-ready Telegram Mini App for task management and reminders.

## ✨ Features

- 📝 **Task Management**: Create, edit, complete, and delete tasks
- 🔔 **Smart Reminders**: Set reminders and receive Telegram notifications
- 🗓️ **Smart Grouping**: Automatic task grouping (Overdue, Today, Tomorrow, Later)
- 🌓 **Theme Support**: Dark and light themes with system sync
- ✅ **Task Progress**: Track completion status with beautiful animations
- 🎨 **Modern UI**: Apple/Google Keep style design with Tailwind CSS
- 📱 **Responsive**: Perfect on all device sizes
- 🔐 **Secure**: Telegram authentication with signature verification
- ⚡ **Fast**: Optimized for speed with Vite and React 19
- 🧪 **Tested**: Comprehensive test coverage

## 🏗️ Architecture

```
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── api.ts           # API client
│   │   ├── telegram.ts      # Telegram integration
│   │   ├── types.ts         # TypeScript types
│   │   └── App.tsx          # Main app
│   └── vite.config.ts
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── api.py               # API endpoints
│   ├── auth.py              # Authentication
│   ├── bot.py               # Telegram bot
│   ├── tests/               # Test suite
│   └── requirements.txt
└── docker-compose.yml
```

## 🛠️ Tech Stack

### Frontend
- **React 19** - UI framework
- **Vite** - Build tool
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **date-fns** - Date manipulation
- **Lucide Icons** - Icons
- **Axios** - HTTP client

### Backend
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database
- **python-telegram-bot** - Telegram API
- **APScheduler** - Task scheduling
- **Pydantic** - Data validation

## 📋 Requirements

- Python 3.11+
- Node.js 18+
- Telegram account
- Bot token from @BotFather

## 🚀 Quick Start

### 1. Get Telegram Bot Token

1. Message [@BotFather](https://t.me/botfather)
2. Create a new bot: `/newbot`
3. Copy your **BOT_TOKEN**

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env

# Update .env with your BOT_TOKEN
EDITOR .env

# Run tests
pytest

# Start server
python main.py
```

Server runs at `http://localhost:8000`

### 3. Frontend Setup

```bash
# Install dependencies
npm install

# Create .env.local
echo "VITE_API_URL=http://localhost:8000/api" > .env.local

# Run development server
npm run dev

# Build for production
npm run build
```

Frontend runs at `http://localhost:5173`

## 📚 API Documentation

Once backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

```
POST   /api/tasks              # Create task
GET    /api/tasks              # Get all tasks
GET    /api/tasks/{id}         # Get task details
PUT    /api/tasks/{id}         # Update task
DELETE /api/tasks/{id}         # Delete task
POST   /api/tasks/{id}/complete  # Mark as complete
GET    /api/health             # Health check
```

All endpoints require `X-Init-Data` header (Telegram authentication)

## 🔐 Security

- **Telegram Authentication**: All requests verified with Telegram's bot token
- **Input Validation**: Pydantic schemas validate all inputs
- **CORS Protection**: Restricted to known origins (configurable)
- **SQL Injection Prevention**: SQLAlchemy parameterized queries
- **Rate Limiting**: Recommended via reverse proxy (nginx, Cloudflare)

## 🐳 Docker

### Using Docker Compose

```bash
# Create .env file
cp .env.example .env
nano .env  # Add your BOT_TOKEN

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

Services:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8080`

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_api.py::test_create_task -v
```

### Frontend Tests

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

## 📝 Configuration

### Environment Variables

**Backend (.env)**:
```
BOT_TOKEN=your_bot_token_here
WEBAPP_URL=https://your-domain.com/todo
LOG_LEVEL=INFO
```

**Frontend (.env.local)**:
```
VITE_API_URL=http://localhost:8000/api
```

## 📦 Deployment

### Heroku

```bash
# Create app
heroku create your-todo-app

# Set environment variables
heroku config:set BOT_TOKEN=your_token
heroku config:set WEBAPP_URL=https://your-todo-app.herokuapp.com

# Deploy
git push heroku main
```

### Docker Registry

```bash
# Build images
docker build -f Dockerfile.backend -t your-registry/todo-backend:latest .
docker build -f Dockerfile.frontend -t your-registry/todo-frontend:latest .

# Push
docker push your-registry/todo-backend:latest
docker push your-registry/todo-frontend:latest

# Deploy to your server
docker-compose -f docker-compose.prod.yml up -d
```

## 🎯 Development

### Project Structure

- `/backend/tests` - Backend tests
- `/.github/workflows` - CI/CD pipelines
- `/src/components` - React components
- `/backend/models.py` - Database models
- `/backend/api.py` - API endpoints

### Code Quality

```bash
# Lint backend
flake8 backend/
black backend/

# Format code
black backend/ src/

# Type checking (frontend)
npm run type-check
```

## 🐛 Troubleshooting

### Bot not sending reminders
- Check bot token in .env
- Verify database has reminder_date set
- Check logs: `docker-compose logs backend`

### CORS errors
- Verify VITE_API_URL matches API_BASE in config.py
- Add your domain to ALLOWED_ORIGINS in config.py

### Auth errors
- Ensure init_data is being sent in headers
- Check Telegram WebApp integration

## 📖 API Examples

### Create Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "X-Init-Data: your_init_data" \
  -d '{"text": "Buy milk", "reminder_date": "2024-12-25T10:00:00"}'
```

### Get Tasks

```bash
curl http://localhost:8000/api/tasks \
  -H "X-Init-Data: your_init_data"
```

## 📄 License

MIT - See LICENSE file

## 👤 Author

Created as a modern, production-ready Telegram Mini App template.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📞 Support

For issues and questions, please create an issue on GitHub.

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

# dockerfile
docker compose up -d --build