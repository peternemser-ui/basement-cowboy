# Deployment Guide

This guide covers deploying Basement Cowboy to various environments.

## Table of Contents

- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Monitoring](#monitoring)

## Local Development

### Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/basement-cowboy.git
cd basement-cowboy
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run setup wizard
python scripts/setup_wizard.py

# Start development server
python run.py
```

### Development Mode

Enable debug mode for development:

```bash
export FLASK_DEBUG=true
python run.py
```

## Docker Deployment

### Using Docker Compose (Recommended)

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./output:/app/output
      - ./config:/app/config
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - WORDPRESS_URL=${WORDPRESS_URL}
      - WORDPRESS_USERNAME=${WORDPRESS_USERNAME}
      - WORDPRESS_PASSWORD=${WORDPRESS_PASSWORD}
    restart: unless-stopped
```

**Commands:**

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f app

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build --force-recreate
```

### Standalone Docker

```bash
# Build image
docker build -t basement-cowboy .

# Run container
docker run -d \
  --name basement-cowboy \
  -p 5000:5000 \
  -v $(pwd)/output:/app/output \
  -e OPENAI_API_KEY=sk-... \
  -e WORDPRESS_URL=https://example.com \
  basement-cowboy
```

## Production Deployment

### Environment Variables

Set these environment variables for production:

```bash
# Required
FLASK_DEBUG=false
SECRET_KEY=your-secure-random-key  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"

# OpenAI
OPENAI_API_KEY=sk-your-key

# WordPress
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=your-username
WORDPRESS_PASSWORD=your-app-password

# Optional
SCRAPER_MAX_ARTICLES=100
SCRAPER_DELAY=1.0
```

### Using Gunicorn (Production WSGI Server)

```bash
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

**Gunicorn Configuration (`gunicorn.conf.py`):**

```python
bind = "0.0.0.0:5000"
workers = 4
threads = 2
timeout = 120
accesslog = "output/logs/access.log"
errorlog = "output/logs/error.log"
loglevel = "info"
```

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/basement-cowboy
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/basement-cowboy/app/static;
        expires 30d;
    }
}
```

### SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

## Cloud Platforms

### DigitalOcean App Platform

1. Connect GitHub repository
2. Set environment variables
3. Configure build command: `pip install -r requirements.txt`
4. Set run command: `gunicorn -w 2 run:app`

### Heroku

```bash
# Create app
heroku create basement-cowboy

# Set config
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set WORDPRESS_URL=https://...

# Deploy
git push heroku main
```

**Procfile:**
```
web: gunicorn run:app
```

### AWS (EC2)

1. Launch EC2 instance (Ubuntu recommended)
2. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   ```
3. Clone and setup application
4. Configure Nginx and SSL
5. Create systemd service:

```ini
# /etc/systemd/system/basement-cowboy.service
[Unit]
Description=Basement Cowboy
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/basement-cowboy
Environment="PATH=/home/ubuntu/basement-cowboy/venv/bin"
ExecStart=/home/ubuntu/basement-cowboy/venv/bin/gunicorn -w 4 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable basement-cowboy
sudo systemctl start basement-cowboy
```

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT/basement-cowboy

# Deploy
gcloud run deploy basement-cowboy \
  --image gcr.io/PROJECT/basement-cowboy \
  --platform managed \
  --set-env-vars "OPENAI_API_KEY=sk-..."
```

## Monitoring

### Health Check Endpoint

The application includes a health check endpoint:

```http
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Logging

Configure logging in production:

```python
# In production config
LOG_LEVEL = "INFO"
LOG_FILE = "output/logs/app.log"
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
```

### Metrics

Track key metrics:
- Articles scraped per day
- API response times
- Error rates
- OpenAI API costs

### Uptime Monitoring

Recommended services:
- UptimeRobot (free tier available)
- Pingdom
- AWS CloudWatch

## Backup & Recovery

### Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/basement-cowboy"
DATE=$(date +%Y%m%d)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup articles and config
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz \
  output/news_articles \
  config \
  .env

# Keep last 7 days
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete
```

### Restore

```bash
# Stop application
sudo systemctl stop basement-cowboy

# Restore backup
tar -xzf backup_20240115.tar.gz -C /path/to/basement-cowboy

# Start application
sudo systemctl start basement-cowboy
```

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Set strong SECRET_KEY
- [ ] Keep API keys in environment variables
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Backup strategy in place
- [ ] Monitor for errors
- [ ] Restrict admin access
