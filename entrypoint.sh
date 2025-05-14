#!/bin/sh

set -e  # Exit immediately if a command exits with a non-zero status

# Apply database migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "Starting Gunicorn on port ${PORT:-8000}..."
exec gunicorn -w 3 -b 0.0.0.0:${PORT:-8000} DTest.wsgi:application
