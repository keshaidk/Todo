# Quick Start Guide

## 📦 One-Time Setup

### 1. Get Bot Token
1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Follow prompts to create a new bot
4. Copy your **BOT_TOKEN** (looks like `123456789:ABCdefGHIjklmNOpqrsTUVwxyz...`)

### 2. Backend Setup (5 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "BOT_TOKEN=<paste_your_token_here>" > .env
echo "WEBAPP_URL=https://your-domain.com/todo" >> .env
echo "LOG_LEVEL=INFO" >> .env

# Initialize database and run tests
pytest

# Start server
python main.py
```

**Backend is now running at:** http://localhost:8000

### 3. Frontend Setup (5 minutes)

```bash
# In root directory
npm install

# Create .env.local
echo "VITE_API_URL=http://localhost:8000/api" > .env.local

# Start dev server
npm run dev
```

**Frontend is now running at:** http://localhost:5173

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest -v                    # Run all tests
pytest --cov=.              # With coverage
pytest tests/test_api.py     # Specific file
```

### Frontend Tests
```bash
npm test                     # Run tests
npm run type-check           # TypeScript check
npm run lint                 # ESLint check
```

## 📚 Documentation

- **[README.md](./README.md)** - Full project documentation
- **[API.md](./API.md)** - Complete API reference
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Deployment guides
- **[IMPROVEMENTS.md](./IMPROVEMENTS.md)** - What was improved

## 🐳 Using Docker Compose

```bash
# Create .env
cp .env.example .env
# Edit .env with your BOT_TOKEN

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

**Services:**
- Backend: http://localhost:8000
- Frontend: http://localhost:8080
- API Docs: http://localhost:8000/docs

## 🔍 Verification

### Check Backend
```bash
curl http://localhost:8000/
```

Should return:
```json
{
  "message": "Telegram To-Do Mini App API",
  "version": "1.0.0",
  "docs": "/docs",
  "status": "running"
}
```

### Check Frontend
Open browser: http://localhost:5173

Should show the To-Do app with task list.

## 🚀 Deploy to Production

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed guides on:
- Heroku
- AWS (ECS, EC2)
- Google Cloud Run
- Railway.app
- Docker Registry

## 📝 Key Features

✅ Task management (create, edit, delete, complete)
✅ Smart reminders with Telegram notifications
✅ Automatic task grouping by date
✅ Dark/light theme
✅ Secure Telegram authentication
✅ Responsive design
✅ Fully tested and documented

## ⚡ Commands

### Backend
```bash
# Development
python main.py

# Testing
pytest

# With coverage
pytest --cov=. --cov-report=html

# Linting
flake8 backend/
black backend/
```

### Frontend
```bash
# Development
npm run dev

# Build
npm run build

# Testing
npm test

# Linting
npm run lint

# Type check
npm run type-check
```

## 🐛 Troubleshooting

**CORS Error?**
- Check `BOT_TOKEN` is set correctly
- Verify `VITE_API_URL` matches backend URL
- Check `ALLOWED_ORIGINS` in backend config

**Auth Error?**
- Ensure you're accessing from Telegram Mini App
- For testing, init_data mock is provided

**Port Already in Use?**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

**Tests Failing?**
```bash
# Clean up
rm -rf backend/test.db

# Run tests
pytest -v
```

## 📱 Testing in Telegram

1. **Add Bot to Telegram**
   - Search for your bot name
   - Send `/start` command
   - Click "Open To-Do App" button

2. **Test Features**
   - Create a task
   - Set a reminder
   - Mark as complete
   - Delete task

3. **Mobile Testing**
   - Open in Telegram mobile app
   - Test all features work responsively

## 🎯 Next Steps

1. ✅ Get bot token
2. ✅ Run backend
3. ✅ Run frontend
4. ✅ Test locally
5. ✅ Set Telegram webhook
6. ✅ Deploy to production

## 📞 Support

For issues:
1. Check logs: `docker-compose logs`
2. Read docs: [README.md](./README.md), [API.md](./API.md)
3. Review tests: `pytest -v`
4. Check Telegram bot: [@BotFather](https://t.me/botfather)

---

**Happy coding! 🚀**
