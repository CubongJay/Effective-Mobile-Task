#!/bin/bash


# Exit on error
set -e

# Validate required environment variables
required_vars=("DB_NAME" "DB_USER" "DB_PASSWORD" "SECRET_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "ERROR: $var environment variable is not set"
        exit 1
    fi
done

# Wait for database
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
    sleep 0.1
done
echo "PostgreSQL is ready"

# Run migrations
python manage.py migrate --noinput

# Collect static files
# python manage.py collectstatic --noinput

# Start server
exec "$@"