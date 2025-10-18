"""
Django base settings for CloudEngineered platform.
This file contains settings common to all environments.
"""

import os
from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_filters',
    'django_extensions',
    # Authentication
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # Commenting out other optional packages for initial setup
    # 'crispy_forms',
    # 'crispy_tailwind',
    # 'imagekit',
    # 'meta',
    # 'health_check',
    # 'health_check.db',
    # 'health_check.cache',
    # 'health_check.storage',
    # 'drf_spectacular',
]

LOCAL_APPS = [
    'apps.core',
    'apps.users',
    'apps.ai',
    'apps.tools',
    'apps.content',
    'apps.analytics',
    'apps.automation',
    'apps.affiliates',
    'apps.monetization',  # New monetization app
    'apps.api',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Required for django-allauth
    'apps.core.throttling.RateLimitMiddleware',  # Rate limiting
    'apps.core.middleware.PerformanceMonitoringMiddleware',  # Performance monitoring
    # Phase 2-3 middleware (commented out until all dependencies are ready)
    # 'apps.analytics.middleware.AnalyticsMiddleware',  # Analytics tracking
    # 'apps.core.seo_optimization.SEOEnhancementMiddleware',  # SEO enhancement
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Use SQLite for development, PostgreSQL for production
USE_SQLITE = config('USE_SQLITE', default=True, cast=bool)

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='cloudengineered'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'OPTIONS': {
                'sslmode': 'prefer',
            },
        }
    }

# Cache settings - Redis for production performance
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'cloudengineered',
        'TIMEOUT': 300,  # 5 minutes default
    },
    'ai_cache': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/2'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 30,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'ai',
        'TIMEOUT': 3600,  # 1 hour for AI content
    },
    'session_cache': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/3'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 20,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'session',
        'TIMEOUT': 86400,  # 24 hours for sessions
    }
}

# Cache configuration for different environments
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = 'cloudengineered'

# Cache timeout settings
CACHE_TIMEOUTS = {
    'tools': 1800,      # 30 minutes
    'categories': 3600,  # 1 hour
    'articles': 1200,    # 20 minutes
    'ai_templates': 7200, # 2 hours
    'ai_generations': 3600, # 1 hour
    'user_stats': 900,   # 15 minutes
    'search_results': 600, # 10 minutes
}

# Celery Configuration for Background Tasks
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# Task routing for different queues
CELERY_TASK_ROUTES = {
    'apps.ai.tasks.*': {'queue': 'ai_tasks'},
    'apps.analytics.tasks.*': {'queue': 'analytics'},
    'apps.core.tasks.*': {'queue': 'general'},
    'apps.tools.tasks.*': {'queue': 'tools'},
}

# Performance monitoring settings
SLOW_REQUEST_THRESHOLD = 1.0  # Log requests slower than 1 second
ENABLE_QUERY_DEBUGGING = True  # Will be overridden by environment-specific settings

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
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Django Sites Framework
SITE_ID = 1

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # 'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# DRF Spectacular (API Documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'CloudEngineered API',
    'DESCRIPTION': 'API for CloudEngineered platform - Cloud tools review and comparison',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Django Allauth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Updated allauth settings for latest version
ACCOUNT_LOGIN_METHODS = {'email'}  # Use email for login (replaces ACCOUNT_AUTHENTICATION_METHOD)
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']  # Required signup fields
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True

# Deprecated settings (keeping for backwards compatibility, but can be removed)
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_USERNAME_REQUIRED = False
# ACCOUNT_AUTHENTICATION_METHOD = 'email'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# Celery settings - using memory for development (switch to Redis in production)
CELERY_TASK_ALWAYS_EAGER = True  # Execute tasks synchronously for development
CELERY_TASK_EAGER_PROPAGATES = True
# CELERY_BROKER_URL = 'redis://localhost:6379/1'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# AI Service Configuration
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY', default='')
GITHUB_TOKEN = config('GITHUB_TOKEN', default='')

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='apikey')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@cloudengineered.io')

# SEO Configuration
META_SITE_PROTOCOL = 'https'
META_SITE_DOMAIN = config('SITE_DOMAIN', default='cloudengineered.io')
META_SITE_TYPE = 'website'
META_SITE_NAME = 'CloudEngineered'
META_INCLUDE_KEYWORDS = ['cloud engineering', 'devops tools', 'tool reviews', 'cloud comparison']

# Logging Configuration
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
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ========================================
# AI SERVICE CONFIGURATION - OPENROUTER ONLY
# ========================================
# Using OpenRouter for all AI services (100+ models from single API)
# This reduces costs and simplifies API key management

# Primary AI Configuration
OPENROUTER_API_KEY = config('OPENROUTER_API_KEY', default='')
OPENROUTER_APP_NAME = config('OPENROUTER_APP_NAME', default='CloudEngineered')
SITE_URL = config('SITE_URL', default='http://localhost:8000')
SITE_NAME = config('SITE_NAME', default='CloudEngineered')

# Google Gemini Configuration (FREE TIER - Primary)
GOOGLE_GEMINI_API_KEY = config('GOOGLE_GEMINI_API_KEY', default='')
AI_PROVIDER = config('AI_PROVIDER', default='GEMINI')
AI_MODEL = config('AI_MODEL', default='gemini-2.0-flash')

# GitHub API for repository statistics
GITHUB_API_TOKEN = config('GITHUB_API_TOKEN', default='')

# AI Service Settings
USE_OPENROUTER = config('USE_OPENROUTER', default=False, cast=bool)  # Use Gemini by default
AI_MOCK_MODE = config('AI_MOCK_MODE', default=False, cast=bool)  # Set to False for production

# Google Analytics 4 (Phase 2-3)
GA4_MEASUREMENT_ID = config('GA4_MEASUREMENT_ID', default='')
GA4_API_SECRET = config('GA4_API_SECRET', default='')

# AI Configuration
AI_SETTINGS = {
    'DEFAULT_SERVICE': 'openrouter',
    'OPENROUTER': {
        'API_KEY': OPENROUTER_API_KEY,
        'APP_NAME': OPENROUTER_APP_NAME,
        'SITE_URL': SITE_URL,
        'DEFAULT_MODEL': 'openai/gpt-4o-mini',
        'FALLBACK_MODELS': [
            'openai/gpt-4o-mini',
            'anthropic/claude-3-haiku',
            'meta-llama/llama-3.1-8b-instruct',
        ],
        'BUDGET_MODELS': [
            'meta-llama/llama-3.1-8b-instruct',
            'mistralai/mistral-7b-instruct',
        ],
        'PREMIUM_MODELS': [
            'openai/gpt-4o',
            'anthropic/claude-3.5-sonnet',
            'meta-llama/llama-3.1-70b-instruct',
        ],
        'MAX_TOKENS': 4096,
        'DEFAULT_TEMPERATURE': 0.7,
        'TIMEOUT': 60,  # seconds
        'RETRY_ATTEMPTS': 3,
        'ENABLE_CACHING': True,
        'CACHE_TTL': 3600,  # 1 hour
    },
    # Legacy configurations (kept for backward compatibility, but all using OpenRouter)
    'ANTHROPIC': {
        'API_KEY': OPENROUTER_API_KEY,  # Using OpenRouter for all providers
        'DEFAULT_MODEL': 'anthropic/claude-3.5-sonnet',
        'MAX_TOKENS': 8000,
        'TIMEOUT': 60,
    },
    'PERPLEXITY': {
        'API_KEY': OPENROUTER_API_KEY,  # Using OpenRouter for all providers
        'DEFAULT_MODEL': 'perplexity/llama-3.1-sonar-large-128k-online',
        'MAX_TOKENS': 4000,
        'TIMEOUT': 60,
    },
    'MULTI_MODEL_ORCHESTRATION': {
        'ENABLED': True,
        'RESEARCH_MODEL': 'openrouter',  # All through OpenRouter
        'DRAFT_MODEL': 'openrouter',     # All through OpenRouter
        'VERIFY_MODEL': 'openrouter',    # All through OpenRouter
    },
    'CONTENT_GENERATION': {
        'ENABLE_ASYNC': True,
        'MAX_CONCURRENT': 5,
        'DEFAULT_QUALITY_THRESHOLD': 0.7,
        'AUTO_REVIEW_THRESHOLD': 0.9,
        'ENABLE_PROFANITY_FILTER': True,
        'ENABLE_PLAGIARISM_CHECK': False,  # Requires additional service
    },
    'COST_CONTROL': {
        'DAILY_LIMIT_USD': 10.0,
        'MONTHLY_LIMIT_USD': 200.0,
        'COST_TRACKING': True,
        'ALERT_THRESHOLD': 0.8,  # Alert at 80% of limit
        'AUTO_FALLBACK_ON_LIMIT': True,
    }
}

# Legacy AI Settings (for backward compatibility)
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')

# Content Generation Settings
CONTENT_GENERATION_ENABLED = config('CONTENT_GENERATION_ENABLED', default=True, cast=bool)
AI_CONTENT_CACHE_TIMEOUT = 3600  # 1 hour

# ========================================
# MONETIZATION CONFIGURATION
# ========================================

# Stripe Configuration
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

# Affiliate Marketing Configuration
AFFILIATE_NETWORKS = {
    'SHAREASALE': {
        'merchant_id': config('SHAREASALE_MERCHANT_ID', default=''),
        'api_token': config('SHAREASALE_API_TOKEN', default=''),
        'api_secret': config('SHAREASALE_API_SECRET', default=''),
    },
    'CJ': {
        'website_id': config('CJ_WEBSITE_ID', default=''),
        'personal_access_token': config('CJ_ACCESS_TOKEN', default=''),
    },
    'AMAZON': {
        'associate_tag': config('AMAZON_ASSOCIATE_TAG', default=''),
        'access_key': config('AMAZON_ACCESS_KEY', default=''),
        'secret_key': config('AMAZON_SECRET_KEY', default=''),
    },
    'IMPACT': {
        'account_sid': config('IMPACT_ACCOUNT_SID', default=''),
        'auth_token': config('IMPACT_AUTH_TOKEN', default=''),
    },
}

# Premium Subscription Tiers
PREMIUM_TIERS = [
    {
        'name': 'Starter',
        'price': 29.00,
        'billing_period': 'monthly',
        'features': [
            'Unlimited tool comparisons',
            'AI-powered recommendations',
            'Email support',
            'Basic analytics',
        ]
    },
    {
        'name': 'Professional',
        'price': 79.00,
        'billing_period': 'monthly',
        'features': [
            'Everything in Starter',
            'Priority support',
            'Advanced analytics',
            'API access',
            'Custom integrations',
            'Team collaboration',
        ]
    },
    {
        'name': 'Enterprise',
        'price': 200.00,
        'billing_period': 'monthly',
        'features': [
            'Everything in Professional',
            'Dedicated account manager',
            'Custom SLAs',
            'White-label options',
            'SSO integration',
            'Advanced security features',
        ]
    },
]

# Sponsored Content Settings
SPONSORED_CONTENT_MIN_BUDGET = 500.00  # Minimum campaign budget
SPONSORED_CONTENT_CPM = 5.00  # Cost per thousand impressions
SPONSORED_CONTENT_CPC = 0.50  # Cost per click

# AI Models Configuration (for database seeding)
DEFAULT_AI_MODELS = [
    {
        'provider': 'OpenRouter',
        'name': 'openai/gpt-4o-mini',
        'display_name': 'GPT-4o Mini',
        'max_tokens': 128000,
        'cost_per_1k_input_tokens': 0.00015,
        'cost_per_1k_output_tokens': 0.0006,
        'is_active': True,
    },
    {
        'provider': 'OpenRouter',
        'name': 'anthropic/claude-3-haiku',
        'display_name': 'Claude 3 Haiku',
        'max_tokens': 200000,
        'cost_per_1k_input_tokens': 0.00025,
        'cost_per_1k_output_tokens': 0.00125,
        'is_active': True,
    },
    {
        'provider': 'OpenRouter', 
        'name': 'meta-llama/llama-3.1-8b-instruct',
        'display_name': 'Llama 3.1 8B',
        'max_tokens': 32768,
        'cost_per_1k_input_tokens': 0.00018,
        'cost_per_1k_output_tokens': 0.00018,
        'is_active': True,
    },
]
