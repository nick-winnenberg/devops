#!/bin/bash

# Railway startup script for Django with error handling
set -e  # Exit on any error

echo "Starting Django application..."

# Test database connection first
echo "Testing database connection..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devops.settings')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
    print('Database connection successful')
"

# Run database migrations with retry
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (optional)
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found, you may want to create one manually')
"

# Start Gunicorn server with production settings
echo "Starting Gunicorn server..."
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    devops.wsgi:application