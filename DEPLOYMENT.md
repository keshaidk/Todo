# Deployment Guide

This guide covers deploying the Telegram To-Do Mini App to various platforms.

## Prerequisites

- Docker (for container deployment)
- GitHub account (for CI/CD)
- Domain name with SSL certificate
- Telegram Bot Token from @BotFather

## Docker Deployment

### Local Docker

```bash
# Build images
docker build -f Dockerfile.backend -t todo-backend:latest .
docker build -f Dockerfile.frontend -t todo-frontend:latest .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Registry (Docker Hub, ECR, GCR)

```bash
# Build and tag
docker build -f Dockerfile.backend -t your-registry/todo-backend:1.0.0 .
docker build -f Dockerfile.frontend -t your-registry/todo-frontend:1.0.0 .

# Push to registry
docker push your-registry/todo-backend:1.0.0
docker push your-registry/todo-frontend:1.0.0
```

## Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Free or paid Heroku account

### Deployment Steps

```bash
# Create Heroku app
heroku create your-todo-app

# Add buildpacks
heroku buildpacks:add heroku/python
heroku buildpacks:add heroku/nodejs

# Set environment variables
heroku config:set BOT_TOKEN=your_bot_token_here
heroku config:set WEBAPP_URL=https://your-todo-app.herokuapp.com
heroku config:set LOG_LEVEL=INFO

# Deploy
git push heroku main

# View logs
heroku logs --tail

# Scale dynos (if needed)
heroku ps:scale web=2
```

### Procfile Configuration

The `Procfile` should contain:
```
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
release: python backend/models.py
```

## AWS Deployment

### Using Elastic Container Service (ECS)

1. **Create ECR repositories**:
```bash
aws ecr create-repository --repository-name todo-backend
aws ecr create-repository --repository-name todo-frontend
```

2. **Push images**:
```bash
docker tag todo-backend:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/todo-backend:latest
docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/todo-backend:latest

docker tag todo-frontend:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/todo-frontend:latest
docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/todo-frontend:latest
```

3. **Create ECS cluster and services** via AWS Console

### Using EC2

```bash
# Connect to EC2 instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Clone repository
git clone https://github.com/your-repo/todo-app.git
cd todo-app

# Create .env file
sudo nano .env

# Run with Docker Compose
sudo docker-compose up -d

# Setup Nginx reverse proxy
sudo apt-get install -y nginx
sudo nano /etc/nginx/sites-available/default

# Restart Nginx
sudo systemctl restart nginx
```

**Nginx Configuration**:
```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:8080;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
    }
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## Google Cloud Run

### Prerequisites
- Google Cloud account
- Cloud Run enabled
- gcloud CLI installed

### Deployment

```bash
# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and push backend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/todo-backend

# Deploy backend
gcloud run deploy todo-backend \
  --image gcr.io/YOUR_PROJECT_ID/todo-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars BOT_TOKEN=your_bot_token,WEBAPP_URL=https://your-domain.com

# Build and push frontend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/todo-frontend

# Deploy frontend
gcloud run deploy todo-frontend \
  --image gcr.io/YOUR_PROJECT_ID/todo-frontend \
  --platform managed \
  --region us-central1
```

## Railway.app Deployment

### Steps

1. Create GitHub repository (if not already)
2. Sign up on [railway.app](https://railway.app)
3. Connect GitHub account
4. Create new project and select repository
5. Configure environment variables:
   - `BOT_TOKEN`
   - `WEBAPP_URL`
   - `LOG_LEVEL`
6. Deploy!

## Vercel + Backend Separation

### Frontend on Vercel

```bash
# Create vercel.json
cat > vercel.json << 'EOF'
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "env": {
    "VITE_API_URL": "https://your-api.example.com/api"
  }
}
EOF

# Deploy
vercel --prod
```

### Backend on Railway or Render

Create `.railway.json` or `render.yaml` as needed.

## GitHub Actions CI/CD

The repository includes `.github/workflows/ci.yml` which:
1. Runs tests on every push
2. Builds Docker images
3. Can deploy to Docker Hub or registry

### Setup

1. Create GitHub repository secrets:
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`
   - `BOT_TOKEN`
   - `WEBAPP_URL`

2. Customize `.github/workflows/ci.yml` for your deployment target

3. Push to trigger workflow

## Monitoring & Logging

### Using Docker logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Using external services
- **Sentry**: Error tracking
  ```python
  import sentry_sdk
  sentry_sdk.init("your-sentry-dsn")
  ```

- **LogRocket**: Frontend monitoring
  ```typescript
  import LogRocket from "logrocket";
  LogRocket.init("your-app-id");
  ```

- **Datadog**: Full-stack monitoring
  - Install agent on host
  - Configure environment variables

## Database Backup

### SQLite backup
```bash
# Backup
cp todo.db todo.db.backup

# Restore
cp todo.db.backup todo.db
```

### Automated daily backup
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/todo"
mkdir -p $BACKUP_DIR
cp /data/todo.db $BACKUP_DIR/todo-$(date +%Y%m%d-%H%M%S).db
EOF

# Add to crontab
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

## SSL/TLS Certificate

### Using Let's Encrypt with Certbot

```bash
sudo apt-get install certbot python3-certbot-nginx

sudo certbot certonly --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Troubleshooting

### Bot not receiving updates
1. Verify BOT_TOKEN is correct
2. Check bot polling is running: `docker-compose logs backend`
3. Ensure webhook URL is set correctly

### CORS errors
1. Check ALLOWED_ORIGINS includes frontend domain
2. Verify X-Init-Data header is being sent
3. Check browser console for specific errors

### Database errors
1. Check file permissions on todo.db
2. Ensure SQLite isn't corrupted: `sqlite3 todo.db PRAGMA integrity_check;`
3. Check disk space

### High memory usage
1. Check for memory leaks: `docker stats`
2. Increase container memory limits
3. Profile with Python profiler: `python -m cProfile main.py`

## Performance Optimization

### Frontend
- Enable gzip compression in Nginx
- Use CDN for static assets
- Lazy load components
- Optimize bundle size: `npm run build -- --analyze`

### Backend
- Add caching headers
- Enable database connection pooling
- Use async/await properly
- Monitor slow queries

### Infrastructure
- Use managed database (RDS, Cloud SQL) for production
- Enable autoscaling
- Use load balancer (AWS ALB, Google Cloud LB)
- Enable CORS caching

## Security Checklist

- [ ] Bot token stored in environment variables (not in code)
- [ ] HTTPS enabled
- [ ] CORS origins restricted
- [ ] Database credentials not exposed
- [ ] Dependencies updated
- [ ] Input validation enabled
- [ ] Error messages don't leak info
- [ ] Backups automated
- [ ] Monitoring and alerting configured
- [ ] Regular security audits scheduled
