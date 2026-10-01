#!/bin/bash

# Local Development Setup Script

set -e

echo "🚀 Setting up local development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Build all services
echo "🏗️  Building Docker images..."
docker-compose build

# Start all services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Run migrations
echo "🔄 Running migrations..."
docker-compose exec -T backend python manage.py migrate --noinput

# Create superuser (optional)
echo ""
echo "📋 Create Django superuser:"
docker-compose exec backend python manage.py createsuperuser

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec -T backend python manage.py collectstatic --noinput

echo ""
echo "✅ Development environment is ready!"
echo ""
echo "🌐 Access your site:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   Django Admin: http://localhost:8000/admin"
echo "   Adminer (DB): http://localhost:8080 (not in dev)"
echo ""
echo "📊 View logs:"
echo "   All services: docker-compose logs -f"
echo "   Backend only: docker-compose logs -f backend"
echo ""
echo "🛑 Stop services: docker-compose down"
