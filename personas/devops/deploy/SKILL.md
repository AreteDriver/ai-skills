---
name: deploy
description: Deployment Checklist & Setup
---

# /deploy - Deployment Checklist & Setup

Deployment guides for various platforms.

## Usage
```
/deploy                  # Analyze project, suggest deployment
/deploy systemd          # Linux systemd service
/deploy docker           # Docker deployment
/deploy cloud            # Cloud deployment guide
```

## What This Skill Does

1. **Analyze Application** - Type, dependencies, requirements
2. **Generate Config** - Deployment configuration files
3. **Create Checklist** - Pre-deployment verification
4. **Document Process** - Step-by-step deployment guide
5. **Add Monitoring** - Health checks, logging

## Systemd Service Deployment

### Service File
```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
Environment="PATH=/opt/myapp/.venv/bin"
ExecStart=/opt/myapp/.venv/bin/python -m myapp serve
Restart=always
RestartSec=5

# Security hardening
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/myapp/data

[Install]
WantedBy=multi-user.target
```

### Deployment Script
```bash
#!/bin/bash
# deploy.sh

set -e

APP_DIR=/opt/myapp
SERVICE=myapp

echo "Deploying myapp..."

# Stop service
sudo systemctl stop $SERVICE || true

# Update code
cd $APP_DIR
git pull origin main

# Update dependencies
.venv/bin/pip install -e .

# Run migrations (if applicable)
# .venv/bin/python -m myapp migrate

# Start service
sudo systemctl start $SERVICE
sudo systemctl status $SERVICE

echo "Deployment complete!"
```

## Docker Deployment

### docker-compose.yml
```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - app-data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=myapp
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - db-data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  app-data:
  db-data:
```

### Deployment Commands
```bash
# Build and deploy
docker compose build
docker compose up -d

# View logs
docker compose logs -f app

# Update deployment
docker compose pull
docker compose up -d --build

# Rollback
docker compose down
docker compose up -d --no-build  # Uses previous image
```

## Deployment Checklist

```markdown
# Deployment Checklist: [App Name]

## Pre-Deployment
- [ ] All tests passing
- [ ] Version bumped
- [ ] CHANGELOG updated
- [ ] Environment variables documented
- [ ] Database migrations ready
- [ ] Backup taken (if applicable)

## Configuration
- [ ] Production .env file ready
- [ ] Secrets rotated (if needed)
- [ ] SSL certificates valid
- [ ] Domain DNS configured

## Deployment
- [ ] Code deployed
- [ ] Dependencies installed
- [ ] Migrations run
- [ ] Static assets built/deployed
- [ ] Service restarted

## Post-Deployment
- [ ] Health check passing
- [ ] Smoke tests passing
- [ ] Logs checked for errors
- [ ] Monitoring alerts configured
- [ ] Rollback plan tested

## Rollback Plan
1. Stop service: `sudo systemctl stop myapp`
2. Checkout previous version: `git checkout v1.2.3`
3. Reinstall deps: `pip install -e .`
4. Start service: `sudo systemctl start myapp`
```

## Health Check Endpoint

```python
# Add to your application
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    checks = {
        "status": "healthy",
        "version": __version__,
        "checks": {}
    }

    # Database check
    try:
        await db.execute("SELECT 1")
        checks["checks"]["database"] = "ok"
    except Exception as e:
        checks["status"] = "unhealthy"
        checks["checks"]["database"] = str(e)

    # Cache check
    try:
        await cache.ping()
        checks["checks"]["cache"] = "ok"
    except Exception as e:
        checks["checks"]["cache"] = str(e)

    status_code = 200 if checks["status"] == "healthy" else 503
    return JSONResponse(checks, status_code=status_code)
```

## Instructions for Claude

When /deploy is invoked:

1. **Analyze application** - Type, dependencies, requirements
2. **Determine target** - Systemd, Docker, cloud, etc.
3. **Generate configs** - Service files, docker-compose, etc.
4. **Create deploy script** - Automated deployment
5. **Add health checks** - Monitoring endpoint
6. **Write checklist** - Pre/post deployment steps
7. **Document rollback** - How to revert if needed
8. **Consider security** - Least privilege, secrets management
