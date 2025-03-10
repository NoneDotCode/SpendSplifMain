#!/bin/sh

DB_HOST=34.91.31.235
DB_PORT=5432

echo "Waiting for db..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done
echo "DB is ready"

# Migrating and collecting statics
python backend/manage.py migrate --noinput
python backend/manage.py collectstatic --noinput

# Launch Gunicorn server
gunicorn backend.config.wsgi:application --bind 0.0.0.0:8000 --timeout 90
