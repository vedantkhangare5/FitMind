# FitMind Production Deployment Guide

This document outlines the standard operating procedure for deploying FitMind to a production environment.

## 1. Prerequisites
- A VPS (Virtual Private Server) running Linux (e.g., Ubuntu 22.04 or 24.04).
- Docker and Docker Compose installed.
- A registered domain name (e.g., `fitmind.app`).
- DNS A Records pointing `fitmind.app` and `api.fitmind.app` to your server's IP address.

## 2. Server Setup
SSH into your server and clone the repository:
```bash
git clone https://github.com/vedantkhangare5/FitMind.git /opt/fitmind
cd /opt/fitmind
```

Create the `.env` file in the root directory:
```bash
cat << 'EOF' > .env
DOMAIN=fitmind.app
APP_ENV=production
JWT_SECRET=your_super_secure_random_string_here
GEMINI_API_KEY=your_gemini_api_key_here
EOF
```
*Note: Generate a secure `JWT_SECRET` using `openssl rand -hex 32`.*

## 3. Initial Deployment
Start the application stack using Docker Compose. The Caddy reverse proxy will automatically provision Let's Encrypt SSL certificates for your domains.

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

Verify the services are running:
```bash
docker-compose -f docker-compose.prod.yml ps
```

## 4. Continuous Deployment (GitHub Actions)
To enable automated deployments when code is merged into `main`:
1. Go to your GitHub Repository -> Settings -> Secrets and variables -> Actions.
2. Add the following repository secrets:
   - `SERVER_HOST`: The IP address of your server.
   - `SERVER_USER`: Your SSH username (e.g., `root` or `ubuntu`).
   - `SSH_PRIVATE_KEY`: The private key used to SSH into the server.

The `.github/workflows/deploy.yml` action will now automatically deploy changes when triggered manually.

## 5. Database Backups
The database is an SQLite file mounted via a Docker volume.
To run an online, safe backup:
```bash
chmod +x scripts/backup_db.sh
./scripts/backup_db.sh
```
It is highly recommended to add this script to your server's cron jobs to run daily:
```bash
crontab -e
# Add the following line to run at 2 AM daily
0 2 * * * /opt/fitmind/scripts/backup_db.sh >> /var/log/fitmind_backup.log 2>&1
```

## 6. Rollback Strategy
If a deployment fails, you can roll back to the previous stable state using git and Docker:

```bash
cd /opt/fitmind
# Find the previous working commit
git log --oneline
# Checkout the stable commit
git checkout <commit-hash>
# Rebuild and restart the containers
docker-compose -f docker-compose.prod.yml up -d --build
```

## 7. Monitoring & Health
To check the backend health and database connectivity:
```bash
curl https://api.fitmind.app/api/health
```
Expected response:
```json
{
  "status": "healthy",
  "database": "healthy",
  "app_name": "FitMind AI",
  "environment": "production",
  "timestamp": "2026-08-19..."
}
```
