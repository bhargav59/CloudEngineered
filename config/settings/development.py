"""
Development settings for CloudEngineered platform.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

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

# Development logging - more verbose
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'
