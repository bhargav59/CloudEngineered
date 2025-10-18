"""
Development settings for CloudEngineered platform.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allow Codespaces, localhost, and wildcard for development
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Add Codespaces hostname if available
CODESPACE_NAME = config('CODESPACE_NAME', default='')
if CODESPACE_NAME:
    ALLOWED_HOSTS.append(f'{CODESPACE_NAME}-8000.app.github.dev')

# Development database (can use SQLite for quick development)
if config('USE_SQLITE', default=False, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Development middleware
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Django Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Codespaces support - allow port forwarding
if CODESPACE_NAME:
    # Disable CSRF for Codespaces preview (development only)
    CSRF_TRUSTED_ORIGINS = [
        f'https://{CODESPACE_NAME}-8000.app.github.dev',
        f'https://*.app.github.dev',
    ]

# Development static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Development email backend (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Celery settings for development
CELERY_TASK_ALWAYS_EAGER = config('CELERY_ALWAYS_EAGER', default=False, cast=bool)
CELERY_TASK_EAGER_PROPAGATES = True

# Django Extensions
GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}

# Disable caching in development
if config('DISABLE_CACHE', default=False, cast=bool):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# Development logging - reduce autoreload noise
LOGGING['handlers']['console']['level'] = 'INFO'  # Changed from DEBUG
LOGGING['loggers']['apps']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'INFO'  # Changed from DEBUG

# Silence Django's autoreload file watching messages
LOGGING['loggers']['django.utils.autoreload'] = {
    'handlers': ['console'],
    'level': 'WARNING',  # Only show warnings/errors from autoreload
    'propagate': False,
}
