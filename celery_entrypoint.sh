#!/bin/sh

DB_HOST=34.91.31.235
DB_PORT=5432

echo "Waiting for db..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done
echo "DB is ready"

# Lauch command from the command line
exec "$@"
