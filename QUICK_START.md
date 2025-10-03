# 🚀 Quick Start Guide - CloudEngineered Platform

## For Development (Local)

### 1. Install Dependencies
```bash
pip install -r requirements/development.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Load Initial Data
```bash
python setup_initial_data.py
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit: http://localhost:8000

---

## For Production Deployment

### 1. Environment Variables
Update `.env` with production values:
```bash
DEBUG=False
SECRET_KEY=<generate-new-secret-key>
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://localhost:6379/0
SENTRY_DSN=https://...  # Get from sentry.io
GA4_MEASUREMENT_ID=G-XXXXXXXXXX  # Get from analytics.google.com
GA4_API_SECRET=xxxxx  # Get from GA4
```

### 2. Database Setup
```bash
# Create PostgreSQL database
createdb cloudengineered

# Run migrations
python manage.py migrate --settings=config.settings.production

# Load initial data
python setup_initial_data.py
```

### 3. Static Files
```bash
python manage.py collectstatic --settings=config.settings.production
```

### 4. Deploy with Docker
```bash
cd docker
docker-compose up -d
```

### 5. Verify Deployment
- Check health: https://yourdomain.com/health/
- Check API: https://yourdomain.com/api/v1/health/
- Check Sentry: https://sentry.io
- Check GA4: https://analytics.google.com

---

## Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific App Tests
```bash
python manage.py test apps.tools
python manage.py test apps.api
python manage.py test apps.core
```

### Run with Coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # View detailed report
```

---

## Monitoring Setup

### 1. Sentry (5 minutes)
1. Sign up: https://sentry.io
2. Create Django project
3. Copy DSN
4. Add to `.env`: `SENTRY_DSN=https://...`
5. Restart app
6. Verify errors appear in dashboard

### 2. Google Analytics 4 (5 minutes)
1. Create property: https://analytics.google.com
2. Get Measurement ID (G-XXXXXXXXXX)
3. Create API secret: Admin → Data Streams → Measurement Protocol API secrets
4. Add to `.env`:
   ```
   GA4_MEASUREMENT_ID=G-XXXXXXXXXX
   GA4_API_SECRET=your-secret
   ```
5. Restart app
6. Check Real-Time reports

See `MONITORING_SETUP.md` for detailed instructions.

---

## Key Management Commands

### User Management
```bash
# Create superuser
python manage.py createsuperuser

# Change password
python manage.py changepassword username
```

### Database
```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations
```

### Content
```bash
# Load categories and tools
python setup_initial_data.py

# Generate AI content (if API key configured)
python manage.py shell
>>> from apps.automation.ai_content_generator import ContentGenerator
>>> generator = ContentGenerator()
>>> generator.generate_all_missing_descriptions()
```

### Maintenance
```bash
# Clear cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Update GitHub stats
python manage.py shell
>>> from apps.automation.github_monitor import GitHubMonitor
>>> monitor = GitHubMonitor()
>>> monitor.update_all_tools()
```

---

## Useful URLs

### Development
- Homepage: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- API: http://localhost:8000/api/v1/
- API Docs: http://localhost:8000/api/v1/schema/swagger/
- Health: http://localhost:8000/health/

### Production
- Homepage: https://yourdomain.com/
- Admin: https://yourdomain.com/admin/
- API: https://yourdomain.com/api/v1/
- Health: https://yourdomain.com/health/
- Sitemap: https://yourdomain.com/sitemap.xml
- Robots: https://yourdomain.com/robots.txt

---

## Troubleshooting

### Issue: "ImportError" or "ModuleNotFoundError"
**Solution:** Install dependencies
```bash
pip install -r requirements/development.txt
```

### Issue: "Database connection error"
**Solution:** Check DATABASE_URL in .env
```bash
# For development (SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# For production (PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Issue: "Static files not loading"
**Solution:** Collect static files
```bash
python manage.py collectstatic --noinput
```

### Issue: "OpenRouter API errors"
**Solution:** Check API key
```bash
# Test API key
python test_openrouter.py

# Or set mock mode
# In .env: AI_MOCK_MODE=True
```

### Issue: "Template warnings"
**Solution:** Already fixed! If you see any:
```bash
# Clear cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Restart server
```

### Issue: "Test failures"
**Solution:** Run tests to see specific errors
```bash
python manage.py test --verbosity=2
```

---

## Performance Tips

### 1. Enable Redis Caching
```bash
# Install Redis
apt-get install redis-server

# Update .env
REDIS_URL=redis://localhost:6379/0

# Verify
redis-cli ping
```

### 2. Optimize Database
```bash
# Check for missing indexes
python manage.py check

# Analyze query performance
python manage.py shell
>>> from django.db import connection
>>> from django.test.utils import CaptureQueriesContext
>>> with CaptureQueriesContext(connection) as queries:
...     # Run your queries
...     print(f"Query count: {len(queries)}")
```

### 3. Monitor Performance
```bash
# Check slow endpoints
tail -f logs/django.log | grep "response_time"

# Database queries per request
# Look for "query_count" in logs
```

---

## Security Checklist

- [ ] Change DEBUG to False in production
- [ ] Generate new SECRET_KEY for production
- [ ] Set ALLOWED_HOSTS to your domain
- [ ] Enable SSL (SECURE_SSL_REDIRECT=True)
- [ ] Enable secure cookies (SESSION_COOKIE_SECURE=True)
- [ ] Enable CSRF secure cookie (CSRF_COOKIE_SECURE=True)
- [ ] Set HSTS headers (SECURE_HSTS_SECONDS=31536000)
- [ ] Configure firewall (allow only 80, 443)
- [ ] Regular security updates (pip, OS packages)
- [ ] Backup database regularly
- [ ] Monitor error logs daily

---

## Common Tasks

### Add a New Tool
1. Go to Admin: `/admin/tools/tool/add/`
2. Fill in required fields
3. Save
4. (Optional) Generate AI description

### Add a New Category
1. Go to Admin: `/admin/tools/category/add/`
2. Set `is_featured=True` to show on homepage
3. Set `sort_order` for display order

### Create Premium Features
1. Go to Admin: `/admin/monetization/premiumtier/`
2. Create pricing tiers
3. Configure features JSON

### Setup Affiliate Links
1. Go to Admin: `/admin/monetization/affiliateprogram/`
2. Add affiliate network
3. Create program for tool
4. Generate tracking links

---

## Support

- **Documentation:** See `/docs/` folder
- **Issues:** Create GitHub issue
- **Email:** support@cloudengineered.com (configure)
- **Status:** Check `/health/` endpoint

---

## Quick Links

- **Main Documentation:** `README.md`
- **Development Guide:** `DEVELOPMENT_GUIDE.md`
- **Monitoring Setup:** `MONITORING_SETUP.md`
- **Completion Summary:** `PROJECT_COMPLETION_SUMMARY.md`
- **Deployment Checklist:** `PRODUCTION_DEPLOYMENT_CHECKLIST.md`

---

**Need Help?** All detailed instructions are in the respective documentation files!

**Status:** ✅ Production Ready | **Version:** 1.0.0 | **Last Updated:** October 3, 2025
