#!/usr/bin/env bash
set -e

echo "Waiting for postgres..."
while ! nc -z ${SQL_HOST:-db} ${DB_PORT:-5432}; do
  sleep 1
done
echo "PostgreSQL started"

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate --noinput

# Start gunicorn
# gunicorn base.wsgi:application --bind 0.0.0.0:8000 --workers 3 --worker-class sync --timeout 60

# Запускаем сервер

# exec gunicorn base.wsgi:application  --bind 0.0.0.0:8000
exec daphne -b 0.0.0.0 -p 8000 --proxy-headers base.asgi:application