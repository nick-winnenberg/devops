"""
Django settings for devops project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Application definition
INSTALLED_APPS = [
    'owners.apps.OwnersConfig',
    'users.apps.UsersConfig',
    "bootstrap5",
    'crispy_forms',
    "crispy_bootstrap5",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files in production
    'devops.middleware.DatabaseHealthCheckMiddleware',  # Database health monitoring
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
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'devops.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap5",)
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Environment-specific settings
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-g0*j14c7*l++z+x2z2%p()+w+#(7w$p-mj=*dnamylj#9=@q=2')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1','devops.up.railway.app').split(',')

# Database configuration - SIMPLE AND BULLETPROOF
import urllib.parse as urlparse

print("=== DATABASE CONFIGURATION START ===")
print(f"BASE_DIR: {BASE_DIR}")
print(f"PORT env var: {os.environ.get('PORT', 'Not set')}")  
print(f"DATABASE_URL env var: {os.environ.get('DATABASE_URL', 'Not set')}")

# ALWAYS start with a working SQLite configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

print(f"Default SQLite config set: {DATABASES}")

# Try to override with PostgreSQL if we have DATABASE_URL
database_url = os.environ.get('DATABASE_URL')
if database_url and 'postgresql' in database_url:
    print(f"Found PostgreSQL DATABASE_URL, attempting to parse...")
    try:
        import urllib.parse
        url = urllib.parse.urlparse(database_url)
        
        if url.hostname and url.username:
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': url.path[1:] if url.path and len(url.path) > 1 else 'railway',
                    'USER': url.username,
                    'PASSWORD': url.password or '',
                    'HOST': url.hostname,
                    'PORT': url.port or 5432,
                    'OPTIONS': {
                        'sslmode': 'require',
                    },
                    'CONN_MAX_AGE': 600,
                    'CONN_HEALTH_CHECKS': True,
                }
            }
            print(f"✅ PostgreSQL configured successfully")
            print(f"   HOST: {url.hostname}")
            print(f"   DB: {url.path[1:] if url.path else 'railway'}")
        else:
            print(f"❌ PostgreSQL URL incomplete, keeping SQLite")
    except Exception as e:
        print(f"❌ Error parsing PostgreSQL URL: {e}")
        print("Keeping SQLite configuration")

# Final validation
print(f"🎯 FINAL ENGINE: {DATABASES['default']['ENGINE']}")
print(f"🎯 FINAL NAME: {DATABASES['default']['NAME']}")  
print(f"🎯 DATABASES structure: {list(DATABASES.keys())}")
print("=== DATABASE CONFIGURATION COMPLETE ===")

# Logging configuration for Railway
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Production security settings
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email settings
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')