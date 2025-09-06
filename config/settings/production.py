"""
Production settings for CloudEngineered platform.
"""

from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

# Security
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='cloudengineered.io', cast=Csv())

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files configuration (AWS S3)
if config('USE_S3', default=False, cast=bool):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

# Database connection pooling
DATABASES['default'].update({
    'CONN_MAX_AGE': 60,
    'OPTIONS': {
        'MAX_CONNS': 20,
        'CONN_HEALTH_CHECKS': True,
    }
})

# Sentry Error Tracking
if config('SENTRY_DSN', default=''):
    sentry_sdk.init(
        dsn=config('SENTRY_DSN'),
        integrations=[
            DjangoIntegration(auto_enabling=True),
            CeleryIntegration(auto_enabling=True),
        ],
        traces_sample_rate=0.1,
        send_default_pii=True,
        environment=config('ENVIRONMENT', default='production'),
    )

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Redis SSL configuration for production
if config('REDIS_SSL', default=False, cast=bool):
    CACHES['default']['OPTIONS']['CONNECTION_POOL_KWARGS'] = {
        'ssl_cert_reqs': None
    }
    CELERY_REDIS_BACKEND_USE_SSL = {
        'ssl_cert_reqs': None
    }
    CELERY_BROKER_USE_SSL = {
        'ssl_cert_reqs': None
    }

# Performance optimizations
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Production logging
LOGGING['handlers']['file']['level'] = 'ERROR'
LOGGING['handlers']['console']['level'] = 'ERROR'

# Disable unnecessary features in production
ALLOWED_INCLUDE_ROOTS = []
