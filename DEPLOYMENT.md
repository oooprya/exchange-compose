# Deployment Guide - Exchange Compose

## 📋 Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Production Deployment (VPS)](#production-deployment-vps)
3. [Troubleshooting](#troubleshooting)
4. [Security Best Practices](#security-best-practices)

---

## Local Development Setup

### Prerequisites
- Docker & Docker Compose installed
- Git
- 2GB RAM minimum
- Ports available: 80, 443, 3000, 5432, 6379, 8000, 8080

### Quick Start

```bash
# 1. Clone repository
git clone <your-repo-url>
cd exchange-compose

# 2. Copy environment file
cp .env.example .env

# 3. Run setup script
chmod +x setup-dev.sh
./setup-dev.sh
```

### Manual Setup

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate --noinput

# Create admin user
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec -T backend python manage.py collectstatic --noinput
```

### Services Running Locally

| Service | URL | Port |
|---------|-----|------|
| Frontend (Next.js) | http://localhost:3000 | 3000 |
| Backend API | http://localhost:8000 | 8000 |
| Django Admin | http://localhost:8000/admin | 8000 |
| PostgreSQL | localhost:5432 | 5432 |
| Redis | localhost:6379 | 6379 |
| Adminer | http://localhost:8080 | 8080 |
| Nginx | http://localhost:80 | 80 |

### Useful Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Run migrations
docker-compose exec backend python manage.py migrate

# Create admin user
docker-compose exec backend python manage.py createsuperuser

# Shell access
docker-compose exec backend python manage.py shell

# Database shell
docker-compose exec db psql -U django_user -d django_db

# Restart services
docker-compose restart backend

# Stop all
docker-compose down

# Stop and remove volumes (⚠️ deletes database)
docker-compose down -v
```

---

## Production Deployment (VPS)

### Prerequisites
- VPS with Ubuntu 22.04 LTS
- Docker & Docker Compose installed on VPS
- Domain name configured (exprivat.com.ua)
- SSL certificate setup (Let's Encrypt)
- SSH access to VPS

### VPS Initial Setup

```bash
# 1. SSH into VPS
ssh root@85.238.113.16

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Create project directory
mkdir -p /srv/exchange-compose
cd /srv/exchange-compose

# 5. Clone repository
git clone <your-repo-url> .

# 6. Setup SSL with Certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

sudo certbot certonly --standalone -d exprivat.com.ua -d www.exprivat.com.ua
```

### Deploy from Local Machine

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh 85.238.113.16 root
```

### Manual Production Deployment

```bash
# On VPS:
cd /srv/exchange-compose

# Pull latest code
git pull origin main

# Update environment variables
nano .env.prod

# Build and start
docker-compose -f docker-compose_prod.yml build
docker-compose -f docker-compose_prod.yml up -d

# Run migrations
docker-compose -f docker-compose_prod.yml exec -T backend python manage.py migrate --noinput

# Create admin user (if first deploy)
docker-compose -f docker-compose_prod.yml exec backend python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose_prod.yml exec -T backend python manage.py collectstatic --noinput

# Check status
docker-compose -f docker-compose_prod.yml ps
```

### Environment Variables

Copy `.env.prod.example` to `.env.prod` and fill in:

```bash
# Critical values to change:
DEBUG=0
SECRET_KEY=<generate-secure-key>
POSTGRES_PASSWORD=<secure-password>
REQUIREPASS=<redis-password>
TOKEN=<telegram-bot-token>
DJANGO_ALLOWED_HOSTS=['IP', 'exprivat.com.ua', 'www.exprivat.com.ua']
```

### Nginx SSL Configuration

The `nginx/nginx.conf` already has SSL setup pointing to Let's Encrypt certificates:
```nginx
ssl_certificate /etc/letsencrypt/live/exprivat.com.ua/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/exprivat.com.ua/privkey.pem;
```

### Monitoring Production

```bash
# Check all containers
docker-compose -f docker-compose_prod.yml ps

# View logs
docker-compose -f docker-compose_prod.yml logs -f backend

# Database backup
docker-compose -f docker-compose_prod.yml exec db pg_dump -U django_user django_db > backup.sql

# Check disk space
docker ps -s
du -sh /var/lib/docker/volumes/*/

# CPU/Memory usage
docker stats
```

---

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps db

# Verify credentials in .env
# Restart database
docker-compose restart db

# Check logs
docker-compose logs db
```

### Redis Connection Issues

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping

# Check Redis password
docker-compose exec redis redis-cli -a <password>

# View Redis logs
docker-compose logs redis
```

### Static Files Not Loading

```bash
# Collect static files
docker-compose exec -T backend python manage.py collectstatic --noinput --clear

# Check permissions
docker-compose exec backend ls -la staticfiles/

# Restart backend
docker-compose restart backend
```

### Celery Tasks Not Running

```bash
# Check worker status
docker-compose ps celery_worker

# View worker logs
docker-compose logs celery_worker

# Restart worker
docker-compose restart celery_worker

# Check Redis connectivity
docker-compose exec backend redis-cli ping
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Out of Disk Space

```bash
# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Clean up build cache
docker builder prune
```

---

## Security Best Practices

### 1. Environment Variables
✅ DO:
- Use `.env.example` for templates
- Use strong passwords (16+ chars, mixed case, numbers, symbols)
- Rotate API keys regularly
- Store secrets in `/etc/exchange/secrets.env` on VPS

❌ DON'T:
- Commit `.env` files to Git
- Use default passwords
- Share secrets in chat/email

### 2. Database Security

```bash
# Use strong PostgreSQL password
# Change default credentials in production
# Enable SSL for database connections
# Regular backups
docker-compose exec db pg_dump -U django_user django_db | gzip > backup_$(date +%Y%m%d).sql.gz
```

### 3. Django Settings

```bash
# Production settings checklist
DEBUG=0                    # Always off in production
ALLOWED_HOSTS=correct      # Set specific domains
SECRET_KEY=long-random     # Generate secure key
SECURE_SSL_REDIRECT=True   # Force HTTPS
SESSION_COOKIE_SECURE=True # Only send over HTTPS
```

### 4. Firewall & Network

```bash
# On VPS (UFW)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 5. Regular Maintenance

```bash
# Weekly backup
0 2 * * 0 cd /srv/exchange-compose && docker-compose -f docker-compose_prod.yml exec -T db pg_dump -U django_user django_db | gzip > backups/backup_$(date +\\%Y\\%m\\%d).sql.gz

# Check for updates
docker-compose pull

# Update Docker images
docker-compose build --pull

# Restart services
docker-compose -f docker-compose_prod.yml restart
```

---

## Useful Resources

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Certbot Documentation](https://certbot.eff.org/)
- [PostgreSQL Backup Guide](https://www.postgresql.org/docs/15/backup.html)

## Support

For issues, check logs first:
```bash
docker-compose logs
docker-compose logs <service-name>
docker-compose exec <service> /bin/bash
```
