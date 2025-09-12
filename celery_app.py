"""
Celery configuration for CloudEngineered platform.
Handles background task processing for performance optimization.
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('cloudengineered')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery configuration
app.conf.update(
    # Task routing
    task_routes={
        'apps.ai.tasks.*': {'queue': 'ai_tasks'},
        'apps.analytics.tasks.*': {'queue': 'analytics'},
        'apps.core.tasks.*': {'queue': 'general'},
    },
    
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task execution
    task_always_eager=False,
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_eager_result=True,
    
    # Result backend
    result_backend='redis://localhost:6379/0',
    result_expires=3600,  # 1 hour
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'update-github-stats': {
            'task': 'apps.tools.tasks.update_github_stats',
            'schedule': 3600.0,  # Every hour
        },
        'generate-ai-content': {
            'task': 'apps.ai.tasks.generate_daily_content',
            'schedule': 86400.0,  # Daily
        },
        'cleanup-old-analytics': {
            'task': 'apps.analytics.tasks.cleanup_old_data',
            'schedule': 86400.0,  # Daily
        },
        'cache-warmup': {
            'task': 'apps.core.tasks.warm_cache',
            'schedule': 1800.0,  # Every 30 minutes
        },
        'performance-analysis': {
            'task': 'apps.analytics.tasks.analyze_performance',
            'schedule': 3600.0,  # Every hour
        },
    },
)