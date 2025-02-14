#!/bin/sh

echo "Waiting for the DB..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "DB is ready"

# Lauch command from the command line
exec "$@"
