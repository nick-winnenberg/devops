# Railway Detection Helper
# This file helps Railway detect this as a Python project

import os
import django
from django.core.wsgi import get_wsgi_application

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devops.settings')

# Initialize Django
django.setup()

# Get WSGI application
application = get_wsgi_application()

if __name__ == "__main__":
    print("Django app detected by Railway")