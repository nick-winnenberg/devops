#!/usr/bin/env python
"""
Debug script to check Railway environment variables and database configuration
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devops.settings')

print("=== RAILWAY DATABASE DEBUG ===")
print(f"PORT: {os.environ.get('PORT', 'Not set')}")
print(f"RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'Not set')}")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')}")
print(f"PGHOST: {os.environ.get('PGHOST', 'Not set')}")
print(f"PGPORT: {os.environ.get('PGPORT', 'Not set')}")
print(f"PGDATABASE: {os.environ.get('PGDATABASE', 'Not set')}")
print(f"PGUSER: {os.environ.get('PGUSER', 'Not set')}")
print(f"PGPASSWORD: {'***SET***' if os.environ.get('PGPASSWORD') else 'Not set'}")

try:
    # Initialize Django
    django.setup()
    
    # Import settings
    from django.conf import settings
    
    print("\n=== DJANGO DATABASE CONFIG ===")
    db_config = settings.DATABASES['default']
    print(f"ENGINE: {db_config.get('ENGINE', 'Not set')}")
    print(f"NAME: {db_config.get('NAME', 'Not set')}")
    print(f"USER: {db_config.get('USER', 'Not set')}")
    print(f"HOST: {db_config.get('HOST', 'Not set')}")
    print(f"PORT: {db_config.get('PORT', 'Not set')}")
    
    print("\n=== TESTING DATABASE CONNECTION ===")
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Database connection successful: {result}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== DEBUG COMPLETE ===")