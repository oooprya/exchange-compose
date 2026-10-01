.PHONY: help dev prod build up down logs shell migrate createsuperuser static backup restore test clean

# Development
.PHONY: help dev
help:
	@echo "Exchange-Compose - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Setup development environment"
	@echo "  make build            - Build Docker images"
	@echo "  make test             - Run bot tests"
	@echo "  make up               - Start all containers"
	@echo "  make down             - Stop all containers"
	@echo "  make logs             - View logs (all services)"
	@echo ""
	@echo "Django:"
	@echo "  make migrate          - Run database migrations"
	@echo "  make createsuperuser  - Create admin user"
	@echo "  make static           - Collect static files"
	@echo "  make shell            - Django shell"
	@echo ""
	@echo "Database:"
	@echo "  make backup           - Backup database"
	@echo "  make restore          - Restore from backup"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Remove containers and volumes"
	@echo "  make clean-all        - Remove everything including images"

dev:
	@echo "🚀 Setting up development environment..."
	docker-compose build
	docker-compose up -d
	sleep 5
	docker-compose exec -T backend python manage.py migrate --noinput
	docker-compose exec -T backend python manage.py collectstatic --noinput
	@echo "✅ Development environment ready!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "Admin: http://localhost:8000/admin"

build:
	@echo "🏗️  Building Docker images..."
	docker-compose build

test:
	cd bot && python -m pytest -q

up:
	@echo "🚀 Starting containers..."
	docker-compose up -d
	@echo "✅ Services started"

down:
	@echo "🛑 Stopping containers..."
	docker-compose down

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

migrate:
	@echo "🔄 Running migrations..."
	docker-compose exec -T backend python manage.py migrate --noinput

createsuperuser:
	@echo "👤 Creating superuser..."
	docker-compose exec backend python manage.py createsuperuser

static:
	@echo "📦 Collecting static files..."
	docker-compose exec -T backend python manage.py collectstatic --noinput

shell:
	@echo "🐍 Starting Django shell..."
	docker-compose exec backend python manage.py shell

backup:
	@echo "📦 Creating database backup..."
	docker-compose exec -T db pg_dump -U django_user django_db | gzip > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql.gz
	@echo "✅ Backup created"

restore:
	@echo "❌ This command needs a backup file parameter"
	@echo "Usage: make restore FILE=backups/backup_XXXXXX.sql.gz"

clean:
	@echo "🧹 Removing containers and volumes..."
	docker-compose down -v
	@echo "✅ Cleaned"

clean-all:
	@echo "🧹 Removing everything..."
	docker-compose down -v
	docker rmi exchange-compose_backend exchange-compose_frontend nginx:latest
	@echo "✅ All removed"

prod-build:
	@echo "🏗️  Building production images..."
	docker-compose -f docker-compose_prod.yml build

prod-up:
	@echo "🚀 Starting production containers..."
	docker-compose -f docker-compose_prod.yml up -d

prod-down:
	@echo "🛑 Stopping production containers..."
	docker-compose -f docker-compose_prod.yml down

prod-logs:
	docker-compose -f docker-compose_prod.yml logs -f
