# Pre-Production Checklist

## Security Checklist ✅

### Django Settings
- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` is unique and strong
- [ ] `ALLOWED_HOSTS` contains only your domains
- [ ] `CSRF_TRUSTED_ORIGINS` is configured
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `SECURE_SSL_REDIRECT = True`

### Database
- [ ] PostgreSQL password is strong (16+ chars)
- [ ] Database backups are automated
- [ ] Database connection uses SSL
- [ ] Migrations are all applied
- [ ] Database user has limited privileges

### Redis
- [ ] Redis password is set and strong
- [ ] Redis only accepts localhost/internal connections
- [ ] Redis persistence is enabled (RDB or AOF)

### Environment Variables
- [ ] All secrets in `.env.prod` (not in code)
- [ ] No test/dummy values in production
- [ ] Telegram tokens are production tokens
- [ ] API keys are secure

### SSL/TLS
- [ ] SSL certificate is installed (Let's Encrypt)
- [ ] Certificate auto-renewal is configured
- [ ] HTTP redirects to HTTPS
- [ ] SSL is valid and not expired
- [ ] Mixed content warnings don't appear

### Firewall & Network
- [ ] UFW is enabled on VPS
- [ ] Only necessary ports are open (22, 80, 443)
- [ ] PostgreSQL port is not exposed to internet
- [ ] Redis port is not exposed to internet

### Docker
- [ ] All images built from latest base images
- [ ] No secrets in Dockerfiles
- [ ] Volume paths are correct
- [ ] Resource limits are set
- [ ] Health checks are configured

## Performance Checklist ✅

### Backend
- [ ] `STATIC_ROOT` is configured
- [ ] WhiteNoise is enabled
- [ ] Database indexes are created
- [ ] Slow queries are optimized
- [ ] Caching is configured correctly
- [ ] Celery workers are running

### Frontend
- [ ] Next.js is built in production mode
- [ ] Images are optimized
- [ ] CSS/JS are minified
- [ ] No console errors in browser
- [ ] Page load times are acceptable

### Database
- [ ] PostgreSQL is not on same machine as app (recommended)
- [ ] Database connection pooling is enabled
- [ ] Vacuum and analyze are scheduled
- [ ] Transaction logs are managed

### Nginx
- [ ] Gzip compression is enabled
- [ ] Browser cache headers are set
- [ ] Static files caching is configured
- [ ] Timeouts are appropriate

## Monitoring & Logging ✅

### Logging
- [ ] Application logs are collected
- [ ] Error logs are monitored
- [ ] Log rotation is configured
- [ ] Logs are not too verbose in production

### Monitoring
- [ ] Uptime monitoring is enabled
- [ ] Alert system is configured
- [ ] Metrics are being collected
- [ ] Resource usage is monitored

### Backups
- [ ] Database backups are automated
- [ ] Backups are tested (restore verify)
- [ ] Backups are stored off-site
- [ ] Backup schedule is documented

## Deployment Checklist ✅

### Before Deploy
- [ ] All tests pass (`docker-compose exec backend python manage.py test`)
- [ ] Code is committed and pushed
- [ ] No uncommitted changes
- [ ] Backup of current production is created
- [ ] Team is notified of deployment

### During Deploy
- [ ] Follow DEPLOYMENT.md instructions
- [ ] Monitor logs for errors
- [ ] Verify all services are running
- [ ] Test critical functionality

### After Deploy
- [ ] Check frontend loads correctly
- [ ] Admin panel is accessible
- [ ] API endpoints respond
- [ ] WebSocket connections work
- [ ] Database operations work
- [ ] Telegram bot responds
- [ ] Error tracking is working

## Post-Deploy Verification ✅

```bash
# Check all services
docker-compose -f docker-compose_prod.yml ps

# Test API
curl https://exprivat.com.ua/api/v1/

# Test admin
curl -L https://exprivat.com.ua/admin/

# Check logs
docker-compose -f docker-compose_prod.yml logs --tail=100

# Verify SSL
openssl s_client -connect exprivat.com.ua:443

# Test database
docker-compose -f docker-compose_prod.yml exec -T db psql -U django_user -d django_db -c "SELECT 1"

# Test Redis
docker-compose -f docker-compose_prod.yml exec -T redis redis-cli ping
```

## Rollback Plan

If something goes wrong:

```bash
# 1. Stop current containers
docker-compose -f docker-compose_prod.yml down

# 2. Restore database from backup
docker-compose -f docker-compose_prod.yml up -d db
gunzip -c backups/backup_XXXXXX.sql.gz | \
  docker-compose -f docker-compose_prod.yml exec -T db psql -U django_user django_db

# 3. Checkout previous code
git checkout <previous-commit>

# 4. Start services again
docker-compose -f docker-compose_prod.yml up -d
```

## Documentation

- Update DEPLOYMENT.md with any new information
- Document any issues and solutions
- Record deployment time and status
- Update runbook for on-call engineers

## Sign-off

- [ ] All checklist items completed
- [ ] Deployment authorized by team lead
- [ ] Communication sent to stakeholders
- [ ] Monitoring alerts are active

**Deployed by:** ________________  
**Date:** ________________  
**Version:** ________________  
**Status:** ✅ Successful / ❌ Rolled Back
