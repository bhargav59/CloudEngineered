# Monitoring Configuration Guide

This file contains configuration for Sentry, Google Analytics 4, and other monitoring services.

## 🔍 Sentry Error Tracking

### Setup Instructions
1. Sign up at https://sentry.io
2. Create a new Django project
3. Copy the DSN (Data Source Name)
4. Add to `.env`:
   ```bash
   SENTRY_DSN=https://your-key@your-org.ingest.sentry.io/your-project-id
   ```

### Configuration (Already Implemented)
Location: `config/settings/production.py`

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,  # 10% of transactions
        profiles_sample_rate=0.1,  # 10% of profiles
        send_default_pii=False,  # Don't send personal data
        environment=ENVIRONMENT,
    )
```

### Features Enabled
- ✅ Automatic error tracking
- ✅ Performance monitoring
- ✅ Django integration
- ✅ Celery task tracking
- ✅ Request/response data
- ✅ User context tracking

### Testing Sentry
```python
# Test in Django shell
python manage.py shell

from sentry_sdk import capture_message
capture_message("Test message from CloudEngineered")

# Should appear in Sentry dashboard
```

---

## 📊 Google Analytics 4

### Setup Instructions
1. Go to https://analytics.google.com
2. Create GA4 property
3. Get Measurement ID (format: G-XXXXXXXXXX)
4. Create Measurement Protocol API secret:
   - Admin → Data Streams → Choose your stream
   - Measurement Protocol API secrets → Create
5. Add to `.env`:
   ```bash
   GA4_MEASUREMENT_ID=G-XXXXXXXXXX
   GA4_API_SECRET=your-api-secret-here
   ```

### Configuration (Already Implemented)
Location: `config/settings/base.py`

```python
GA4_MEASUREMENT_ID = config('GA4_MEASUREMENT_ID', default='')
GA4_API_SECRET = config('GA4_API_SECRET', default='')
```

### Service Implementation
Location: `apps/analytics/integrations.py`

The following events are automatically tracked:
- `tool_view` - When users view tools
- `comparison_create` - When comparisons are created
- `review_submit` - When reviews are submitted
- `affiliate_click` - When affiliate links are clicked
- `subscription_start` - When subscriptions start
- `search_query` - Search queries
- `user_registration` - New user signups

### Enable Analytics Middleware
Uncomment in `config/settings/base.py`:
```python
MIDDLEWARE = [
    # ... other middleware
    'apps.analytics.middleware.AnalyticsMiddleware',  # UNCOMMENT THIS
]
```

### Testing GA4
```python
# Test in Django shell
python manage.py shell

from apps.analytics.integrations import GoogleAnalytics4Service
from apps.tools.models import Tool

ga4 = GoogleAnalytics4Service()
tool = Tool.objects.first()

# Test event tracking
ga4.track_tool_view(tool, None)  # None for request if testing
print("Event sent to GA4!")
```

---

## 📈 Performance Monitoring

### Database Query Monitoring
Already implemented in `apps/core/middleware.py`:
- Tracks query count per request
- Monitors database time
- Logs slow queries
- Cache hit rate tracking

### Response Time Tracking
```python
# Every request logs:
{
    'path': '/tools/',
    'method': 'GET',
    'status_code': 200,
    'response_time': '0.118s',
    'db_time': '0.010s',
    'query_count': 13,
    'cache_hit_rate': '75.0%',
    'user': 'username'
}
```

---

## 🔔 Additional Monitoring (Optional)

### 1. New Relic APM
```bash
# Install
pip install newrelic

# Add to .env
NEW_RELIC_LICENSE_KEY=your-key
NEW_RELIC_APP_NAME=CloudEngineered

# In wsgi.py (add at top)
import newrelic.agent
newrelic.agent.initialize()
```

### 2. Datadog
```bash
# Install
pip install ddtrace

# Run with Datadog
ddtrace-run python manage.py runserver

# Or use in production with Gunicorn
ddtrace-run gunicorn config.wsgi:application
```

### 3. Prometheus + Grafana
```bash
# Install
pip install django-prometheus

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django_prometheus',
    # ... other apps
]

# Add middleware
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# Expose metrics at /metrics
```

### 4. AWS CloudWatch (for AWS deployments)
```python
# Install
pip install boto3 watchtower

# In settings/production.py
import watchtower

LOGGING['handlers']['cloudwatch'] = {
    'level': 'INFO',
    'class': 'watchtower.CloudWatchLogHandler',
    'log_group': 'cloudengineered',
    'stream_name': 'django-app',
}
```

---

## 🚨 Alert Configuration

### Sentry Alerts
Configure in Sentry dashboard:
1. Go to Alerts → Create Alert Rule
2. Set conditions:
   - Error rate exceeds threshold
   - New issue is created
   - Issue frequency is high
3. Set notifications:
   - Email
   - Slack
   - PagerDuty

### Custom Alerts
```python
# apps/core/monitoring.py
from django.core.mail import mail_admins
from django.conf import settings

def alert_high_error_rate(error_count, time_period):
    """Send alert when error rate is high"""
    if error_count > 100:  # threshold
        subject = f"High Error Rate Alert: {error_count} errors in {time_period}"
        message = f"""
        CloudEngineered has experienced {error_count} errors in the past {time_period}.
        Please check Sentry dashboard: https://sentry.io/your-project
        """
        mail_admins(subject, message)
```

---

## 📋 Monitoring Checklist

### Initial Setup
- [ ] Create Sentry account and project
- [ ] Add SENTRY_DSN to `.env`
- [ ] Test Sentry integration
- [ ] Create GA4 property
- [ ] Add GA4_MEASUREMENT_ID to `.env`
- [ ] Add GA4_API_SECRET to `.env`
- [ ] Test GA4 events
- [ ] Enable analytics middleware
- [ ] Configure alert rules

### Production Deployment
- [ ] Verify Sentry is capturing errors
- [ ] Check GA4 dashboard for events
- [ ] Monitor response times
- [ ] Set up uptime monitoring
- [ ] Configure backup alerts
- [ ] Test alert notifications
- [ ] Document incident response

### Regular Monitoring
- [ ] Review Sentry errors daily
- [ ] Check GA4 metrics weekly
- [ ] Monitor API rate limits
- [ ] Track database performance
- [ ] Review server logs
- [ ] Check disk space
- [ ] Monitor background jobs

---

## 🔧 Troubleshooting

### Sentry Not Capturing Errors
1. Check SENTRY_DSN is set correctly
2. Verify environment matches (production settings)
3. Test with manual error:
   ```python
   from sentry_sdk import capture_exception
   try:
       1 / 0
   except Exception as e:
       capture_exception(e)
   ```

### GA4 Events Not Showing
1. Check GA4_MEASUREMENT_ID format (G-XXXXXXXXXX)
2. Verify API secret is correct
3. Enable DebugView in GA4
4. Check request/response in Django logs
5. May take 24-48 hours for data to appear

### High Memory Usage
1. Check for memory leaks in Sentry
2. Monitor with:
   ```bash
   htop
   # or
   docker stats
   ```
3. Optimize database queries
4. Enable query caching
5. Consider Redis for sessions

---

## 📊 Monitoring Dashboard URLs

### Production URLs (Update with your actual URLs)
- Sentry: https://sentry.io/organizations/your-org/projects/cloudengineered/
- GA4: https://analytics.google.com/
- Server Health: https://cloudengineered.com/health/
- API Health: https://cloudengineered.com/api/v1/health/
- Admin: https://cloudengineered.com/admin/

### Local Development
- Health Check: http://localhost:8000/health/
- API Health: http://localhost:8000/api/v1/health/
- Admin: http://localhost:8000/admin/

---

## ✅ Quick Start (5 Minutes)

1. **Get Sentry DSN**
   ```bash
   # Sign up at https://sentry.io
   # Create Django project
   # Copy DSN
   echo "SENTRY_DSN=your-dsn" >> .env
   ```

2. **Get GA4 Credentials**
   ```bash
   # Create property at https://analytics.google.com
   # Get Measurement ID
   echo "GA4_MEASUREMENT_ID=G-XXXXXXXXXX" >> .env
   # Create API secret
   echo "GA4_API_SECRET=your-secret" >> .env
   ```

3. **Test Configuration**
   ```bash
   python manage.py shell
   >>> from django.conf import settings
   >>> print(f"Sentry: {bool(settings.SENTRY_DSN)}")
   >>> print(f"GA4: {bool(settings.GA4_MEASUREMENT_ID)}")
   ```

4. **Deploy and Monitor**
   ```bash
   # Deploy to production
   # Check Sentry dashboard
   # Check GA4 real-time reports
   ```

---

**Last Updated:** October 3, 2025
**Status:** ✅ Configuration Ready - Just needs API keys
