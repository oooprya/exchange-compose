#!/bin/sh
set -e

echo "Waiting for postgres..."
while ! nc -z ${SQL_HOST:-db} ${DB_PORT:-5432}; do
  sleep 1
done
echo "PostgreSQL started"

# Don't flush database in production
if [ "$DEBUG" = "1" ]; then
  echo "Running in DEBUG mode..."
else
  echo "Running in PRODUCTION mode..."
fi

# Apply migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

exec "$@"