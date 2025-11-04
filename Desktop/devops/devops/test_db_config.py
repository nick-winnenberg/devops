#!/usr/bin/env python
"""
Test script to verify Django database configuration is valid
"""

import os
import sys
from pathlib import Path

# Add the project directory to Python path  
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devops.settings')

print("=" * 50)
print("TESTING DJANGO DATABASE CONFIGURATION")
print("=" * 50)

try:
    # Import Django and setup
    import django
    django.setup()
    
    # Import settings
    from django.conf import settings
    
    print("✅ Django setup successful")
    print(f"✅ Settings module: {settings.SETTINGS_MODULE}")
    
    # Check DATABASES configuration
    print("\n--- DATABASES Configuration ---")
    databases = getattr(settings, 'DATABASES', {})
    print(f"DATABASES keys: {list(databases.keys())}")
    
    if 'default' in databases:
        default_db = databases['default']
        print(f"✅ Default database found")
        print(f"   ENGINE: {default_db.get('ENGINE', 'NOT SET!')}")
        print(f"   NAME: {default_db.get('NAME', 'NOT SET!')}")
        print(f"   HOST: {default_db.get('HOST', 'localhost')}")
        print(f"   PORT: {default_db.get('PORT', 'default')}")
        print(f"   USER: {default_db.get('USER', 'none')}")
    else:
        print("❌ No 'default' database configuration found!")
        
    # Test database connection
    print("\n--- Database Connection Test ---")
    from django.db import connection
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Database connection successful: {result}")
        
    print("\n--- Django Check ---")
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'check'])
    
    print("\n🎉 ALL TESTS PASSED!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)