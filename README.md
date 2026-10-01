# Exchange-Compose Project

Приватное бюро обмена валют с админ-панелью, Bot сервисом и современным фронтенд-приложением.

## 🗂️ Project Structure

```
exchange-compose/
├── backend/          # Django REST API
├── frontend/         # Next.js фронтенд
├── bot/             # Telegram Bot
├── nginx/           # Reverse proxy & SSL
├── docker-compose.yml        # Development
├── docker-compose_prod.yml   # Production
└── DEPLOYMENT.md     # Полная документация
```

## 🚀 Quick Start (Development)

### На Windows (PowerShell):

```powershell
# 1. Клонируй репозиторий
git clone <your-repo-url>
cd exchange-compose

# 2. Подготовь .env
copy .env.example .env

# 3. Запусти Docker
docker-compose build
docker-compose up -d

# 4. Создай базу и админа
docker-compose exec backend python manage.py migrate --noinput
docker-compose exec backend python manage.py createsuperuser

# 5. Собери статику
docker-compose exec -T backend python manage.py collectstatic --noinput
```

### На Linux/Mac (Bash):

```bash
chmod +x setup-dev.sh
./setup-dev.sh
```

## 📍 Local URLs

| Сервис | URL |
|--------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api/v1/ |
| Django Admin | http://localhost:8000/admin |
| Adminer (БД) | http://localhost:8080 |

## 📝 Common Commands

```bash
# Просмотр логов
docker-compose logs -f backend
docker-compose logs -f frontend

# Миграции БД
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Django shell
docker-compose exec backend python manage.py shell

# Перезагрузка сервиса
docker-compose restart backend

# Остановка всех контейнеров
docker-compose down

# Полная очистка (⚠️ удалит БД)
docker-compose down -v
```

## 🐳 Services

### Backend (Django 5.0)
- REST API с Tastypie
- WebSocket поддержка (Channels)
- Async задачи (Celery + Redis)
- Admin интерфейс (Django Unfold)

### Frontend (Next.js 14)
- React компоненты
- TypeScript
- Server-side rendering
- Static optimization

### Bot (Python)
- Telegram интеграция
- Функции управления заказами

### Database
- PostgreSQL 16
- Redis кеширование

## 🔒 Production Deployment

Полная инструкция в [DEPLOYMENT.md](DEPLOYMENT.md)

```bash
./deploy.sh 85.238.113.16 root
```

## ⚠️ Перед Production

1. Создай `.env.prod` с реальными переменными
2. Измени `SECRET_KEY` на новый
3. Установи SSL (Let's Encrypt через Certbot)
4. Скопируй `redis.conf` на сервер
5. Проверь безопасность в [DEPLOYMENT.md](DEPLOYMENT.md)

## 🛠️ Troubleshooting

### PostgreSQL connection error
```bash
docker-compose logs db
docker-compose restart db
```

### Static files not loading
```bash
docker-compose exec -T backend python manage.py collectstatic --noinput --clear
docker-compose restart backend
```

### Redis issues
```bash
docker-compose exec redis redis-cli ping
docker-compose exec redis redis-cli -a <password>
```

### Порт уже занят
```bash
# Find process
lsof -i :8000
kill -9 <PID>
```

## 📚 Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Полная инструкция по развёртыванию
- [DEPLOYMENT.md - Security](DEPLOYMENT.md#security-best-practices) - Безопасность
- Django: https://docs.djangoproject.com/
- Next.js: https://nextjs.org/docs
- Docker: https://docs.docker.com/

## 👤 Author

Created by: oooprya

## 📄 License

Private project - All rights reserved
