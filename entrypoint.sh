#!/bin/sh

echo "Waiting for db..."
while ! nc -z db 5432; do
    sleep 0.1
done
echo "DB is ready"

# Migrating and collecting statics
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Launch Gunicorn server
gunicorn backend.config.wsgi:application --bind 0.0.0.0:8000
