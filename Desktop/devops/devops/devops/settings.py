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
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database configuration with connection pooling and retry logic
import urllib.parse as urlparse

# Debug: Print environment variables to Railway logs
print("=== DATABASE DEBUG ===")
print(f"PORT: {os.environ.get('PORT')}")
print(f"RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT')}")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"PGHOST: {os.environ.get('PGHOST')}")
print(f"PGDATABASE: {os.environ.get('PGDATABASE')}")
print("=== END DEBUG ===")

# Always set a default database configuration first
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Then override with PostgreSQL if we have the right environment
database_url = os.environ.get('DATABASE_URL')
if database_url:
    print(f"Using DATABASE_URL: {database_url}")
    try:
        url = urlparse.urlparse(database_url)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': url.path[1:] if url.path and len(url.path) > 1 else 'railway',
                'USER': url.username or 'postgres',
                'PASSWORD': url.password or '',
                'HOST': url.hostname or 'localhost',
                'PORT': url.port or 5432,
                'OPTIONS': {
                    'sslmode': 'require',
                    'connect_timeout': 10,
                    'options': '-c default_transaction_isolation=read_committed'
                },
                'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
                'CONN_HEALTH_CHECKS': True,  # Enable connection health checks
                'ATOMIC_REQUESTS': True,  # Wrap each request in a transaction
            }
        }
        print(f"PostgreSQL config: HOST={url.hostname}, DB={url.path[1:] if url.path else 'railway'}")
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {e}")
        # Keep SQLite as fallback
elif os.environ.get('PGHOST') and os.environ.get('PGDATABASE'):
    print("Using PostgreSQL environment variables")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('PGDATABASE'),
            'USER': os.environ.get('PGUSER', 'postgres'),
            'PASSWORD': os.environ.get('PGPASSWORD', ''),
            'HOST': os.environ.get('PGHOST'),
            'PORT': os.environ.get('PGPORT', '5432'),
            'OPTIONS': {
                'sslmode': 'require',
                'connect_timeout': 10,
                'options': '-c default_transaction_isolation=read_committed'
            },
            'CONN_MAX_AGE': 600,
            'CONN_HEALTH_CHECKS': True,
            'ATOMIC_REQUESTS': True,
        }
    }
    print(f"PostgreSQL config: HOST={os.environ.get('PGHOST')}, DB={os.environ.get('PGDATABASE')}")
elif os.environ.get('PORT'):  # We're on Railway but no database URL
    print("On Railway but no database configured - using SQLite temporarily")
    # Keep SQLite for now, but this indicates a setup issue
else:
    print("Using SQLite for local development")

print(f"Final DATABASE ENGINE: {DATABASES['default']['ENGINE']}")
print(f"Final DATABASE NAME: {DATABASES['default']['NAME']}")

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