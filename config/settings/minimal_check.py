"""
Minimal settings for CloudEngineered platform for error checking and basic setup.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Use SQLite for minimal setup
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Remove problematic middleware and apps for minimal setup
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Minimal installed apps - remove problematic ones
THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_filters',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Disable allauth authentication backend to avoid circular import
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Simple cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# AI Configuration - Use mock mode for testing
AI_MOCK_MODE = True

# Disable AI features for now
AI_SETTINGS = {
    'USE_OPENROUTER': False,
    'MOCK_MODE': True,
}

# Simple email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Disable Celery
CELERY_TASK_ALWAYS_EAGER = True