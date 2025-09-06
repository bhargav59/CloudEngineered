"""
Testing settings for CloudEngineered platform.
"""

from .base import *

# Test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations during tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Test-specific settings
DEBUG = False
TESTING = True
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use dummy cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable Celery during tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Test email backend
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable logging during tests
LOGGING_CONFIG = None

# Test media files
MEDIA_ROOT = '/tmp/cloudengineered_test_media'

# Static files for tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
