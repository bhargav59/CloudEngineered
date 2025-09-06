"""
Celery configuration for CloudEngineered platform.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('cloudengineered')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'scan-github-tools': {
        'task': 'apps.automation.tasks.scan_github_for_tools',
        'schedule': 3600.0,  # Every hour
    },
    'generate-trending-content': {
        'task': 'apps.automation.tasks.generate_trending_content',
        'schedule': 21600.0,  # Every 6 hours
    },
    'update-tool-metrics': {
        'task': 'apps.tools.tasks.update_tool_metrics',
        'schedule': 7200.0,  # Every 2 hours
    },
    'send-newsletter': {
        'task': 'apps.content.tasks.send_weekly_newsletter',
        'schedule': 604800.0,  # Weekly
    },
    'cleanup-old-analytics': {
        'task': 'apps.analytics.tasks.cleanup_old_data',
        'schedule': 86400.0,  # Daily
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
