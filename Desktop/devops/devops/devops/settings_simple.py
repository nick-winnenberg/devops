"""
PRODUCTION-READY Django Settings for Railway Deployment

This configuration file is specifically designed for Railway cloud deployment
and provides a bulletproof setup that handles both development and production
environments automatically based on the DATABASE_URL environment variable.

Key Features:
    - Automatic PostgreSQL/SQLite database switching
    - Railway-optimized deployment settings
    - Bootstrap 5 and Crispy Forms integration
    - WhiteNoise static file serving
    - Comprehensive security configuration
    - Environment-based configuration management
    - Multi-tenant data isolation support

Environment Variables Required:
    - SECRET_KEY: Django secret key (set in Railway dashboard)
    - DEBUG: Enable/disable debug mode (default: True for development)
    - DATABASE_URL: PostgreSQL connection string (automatically set by Railway)

This file replaces the default settings.py for production deployments and
provides a simplified, reliable configuration that works consistently
across different deployment environments.
"""

import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security - MUST be set in Railway environment variables
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-CHANGE-THIS-IN-PRODUCTION')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Allowed hosts - use environment variable with sensible defaults
ALLOWED_HOSTS_ENV = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,*.up.railway.app')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(',') if host.strip()]

# Django 4.0+ requires scheme in CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS_ENV = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'https://*.up.railway.app'
)
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_ENV.split(',') if origin.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth', 
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_bootstrap5',
    'crispy_forms',
    'crispy_bootstrap5',
    'owners.apps.OwnersConfig',
    'users.apps.UsersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'devops.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'devops.wsgi.application'

# Database - SIMPLE LOGIC
DATABASE_URL = os.environ.get('DATABASE_URL')
print(f"🔍 DATABASE_URL exists: {bool(DATABASE_URL)}")

if DATABASE_URL and 'postgresql' in DATABASE_URL:
    print("🐘 Using PostgreSQL from DATABASE_URL")
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    print("📁 Using SQLite (DATABASE_URL not found)")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

print(f"🎯 Database engine: {DATABASES['default']['ENGINE']}")

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap5",)
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Production security settings
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_HTTPONLY = True
    X_FRAME_OPTIONS = 'DENY'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Authentication settings
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'

# Session security
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SAMESITE = 'Lax'

print("✅ Settings loaded successfully")