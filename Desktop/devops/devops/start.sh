#!/bin/bash

# Railway startup script for Django
echo "Starting Django application..."

# Run database migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:$PORT devops.wsgi:application