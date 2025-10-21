# 🚂 Railway Deployment Guide for CloudEngineered

## Quick Deploy to Railway

### 1. Prerequisites
- Railway account (https://railway.app)
- GitHub repository connected to Railway
- PostgreSQL database provisioned on Railway

### 2. Required Environment Variables

Set these in Railway Dashboard → Your Project → Variables:

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-secret-key-here-make-it-long-and-random
DEBUG=False
ALLOWED_HOSTS=your-app.up.railway.app,yourdomain.com

# Database (Railway auto-provides DATABASE_URL)
# DATABASE_URL is automatically set by Railway PostgreSQL plugin

# Static Files
USE_S3=False
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key

# Redis (if using Railway Redis plugin)
REDIS_URL=${REDIS_URL}

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AI Services
OPENROUTER_API_KEY=your-openrouter-api-key
OPENAI_API_KEY=your-openai-key

# Stripe (Optional - for payments)
STRIPE_PUBLIC_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Google AdSense (Optional)
ADSENSE_CLIENT_ID=ca-pub-your-id
ADSENSE_ENABLED=True

# Sentry (Optional - for error tracking)
SENTRY_DSN=your-sentry-dsn
```

### 3. Deploy Configuration

The project includes `railway.json` with optimized settings:
- **Builder**: Dockerfile
- **Runtime**: V2
- **Region**: Asia Southeast (Singapore)
- **Auto-restart**: ON_FAILURE with 10 max retries

### 4. Database Setup

Railway automatically provisions PostgreSQL:
1. Add PostgreSQL plugin to your project
2. Railway sets `DATABASE_URL` automatically
3. Migrations run automatically on deployment

### 5. Build Process

Railway will:
1. ✅ Read `railway.json` configuration
2. ✅ Build Docker image from `Dockerfile`
3. ✅ Install all dependencies from `requirements/production.txt`
4. ✅ Run `start.sh` script which:
   - Waits for database to be ready
   - Runs Django migrations
   - Collects static files
   - Creates superuser (if needed)
   - Starts Gunicorn server

### 6. Port Configuration

Railway provides `$PORT` environment variable dynamically.
The app automatically binds to this port (usually 8000 internally, mapped to 443/80 externally).

### 7. Health Checks

The Dockerfile includes a health check:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3
```

### 8. Deployment Steps

#### Option A: Using Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Deploy
railway up
```

#### Option B: Using Git (Recommended)
```bash
# Commit your changes
git add .
git commit -m "🚀 Deploy to Railway"
git push origin main

# Railway auto-deploys from main branch
```

### 9. Post-Deployment Checks

1. **Check Deployment Logs**:
   ```bash
   railway logs
   ```

2. **Verify Application**:
   - Visit your Railway domain
   - Check admin panel: `https://your-app.up.railway.app/admin/`
   - Test API endpoints

3. **Monitor Performance**:
   - Railway Dashboard → Metrics
   - Check CPU, Memory, Network usage

### 10. Troubleshooting

#### Error: "ModuleNotFoundError: No module named 'django'"
**Solution**: Dependencies not installed. Railway should auto-install from `requirements/production.txt`.
- Check build logs for errors during `pip install`
- Verify `Dockerfile` is copying requirements correctly

#### Error: "gunicorn: not found"
**Solution**: Gunicorn not installed.
- Ensure `requirements/production.txt` includes `gunicorn>=21.0.0`
- Rebuild deployment

#### Error: "Database connection failed"
**Solution**: Database not ready or URL incorrect.
- Check `DATABASE_URL` is set by Railway PostgreSQL plugin
- Verify database is provisioned and running
- Check Railway logs for connection errors

#### Error: "ALLOWED_HOSTS" error
**Solution**: Add your Railway domain to ALLOWED_HOSTS.
```bash
ALLOWED_HOSTS=your-app.up.railway.app,your-custom-domain.com
```

#### Error: Static files not loading
**Solution**: 
- Check `STATIC_ROOT` and `STATIC_URL` settings
- Verify `collectstatic` ran successfully in logs
- Consider using WhiteNoise or S3 for static files

### 11. Custom Domain Setup

1. In Railway Dashboard:
   - Go to Settings → Domains
   - Click "Add Domain"
   - Enter your custom domain

2. Update DNS Records:
   ```
   Type: CNAME
   Name: @ or www
   Value: your-app.up.railway.app
   ```

3. Update Environment Variables:
   ```bash
   ALLOWED_HOSTS=your-app.up.railway.app,yourdomain.com,www.yourdomain.com
   ```

### 12. Scaling Configuration

Edit `railway.json` to scale:
```json
{
  "deploy": {
    "numReplicas": 2,  // Increase for more instances
    "multiRegionConfig": {
      "us-west1": {
        "numReplicas": 1
      },
      "asia-southeast1": {
        "numReplicas": 1
      }
    }
  }
}
```

### 13. Monitoring & Logs

```bash
# View real-time logs
railway logs -f

# View specific service logs
railway logs --service web

# Check deployment status
railway status
```

### 14. Environment-Specific Settings

Railway automatically uses:
- `config.settings.production` (set via `DJANGO_SETTINGS_MODULE`)
- Production-optimized Gunicorn workers (3 workers, 2 threads each)
- WhiteNoise for static file serving
- PostgreSQL database with connection pooling

### 15. Cost Optimization

- **Starter Plan**: $5/month per service
- **Pro Plan**: $20/month with better resources
- **Hobby Plan**: Free tier available (limited resources)

**Tips to reduce costs**:
- Use `sleepApplication: false` only for production
- Optimize worker count (3 workers is reasonable)
- Use CDN for static files (S3 + CloudFront)
- Enable Railway's auto-sleep for dev environments

### 16. Backup Strategy

1. **Database Backups**:
   - Railway auto-backs up PostgreSQL daily
   - Manual backup: Railway Dashboard → Database → Backups

2. **Code Backups**:
   - GitHub repository (already version controlled)
   - Railway keeps deployment history

### 17. Security Best Practices

- ✅ `DEBUG=False` in production
- ✅ Strong `SECRET_KEY` (50+ random characters)
- ✅ HTTPS enforced by Railway
- ✅ Environment variables for secrets (never commit)
- ✅ `ALLOWED_HOSTS` properly configured
- ✅ Regular dependency updates
- ✅ Enable Sentry for error tracking

### 18. Performance Optimization

Current configuration:
- **Workers**: 3 Gunicorn workers
- **Threads**: 2 threads per worker (6 concurrent requests)
- **Timeout**: 120 seconds
- **Keep-alive**: 2 seconds
- **Max requests**: 1000 (worker restarts after)

Adjust in `start.sh` if needed based on traffic.

### 19. CI/CD Integration

Railway auto-deploys on push to `main` branch:
```
main branch push → Railway detects → Build → Deploy → Health check → Live
```

### 20. Support Resources

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/

---

## Quick Reference Commands

```bash
# Deploy
git push origin main

# View logs
railway logs -f

# Run migrations manually
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Open shell
railway run python manage.py shell

# Restart application
railway restart

# Check status
railway status
```

---

## Environment Variables Template

Copy this to Railway Dashboard → Variables:

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<generate-50-char-random-string>
DEBUG=False
ALLOWED_HOSTS=<your-app>.up.railway.app
DATABASE_URL=<auto-set-by-railway>
REDIS_URL=<auto-set-by-railway>
OPENROUTER_API_KEY=<your-key>
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<your-password>
USE_S3=False
SENTRY_DSN=<optional>
STRIPE_SECRET_KEY=<optional>
ADSENSE_CLIENT_ID=<optional>
```

---

**🎉 Your Django application is now ready for Railway deployment!**

For immediate deployment:
```bash
git add .
git commit -m "🚀 Railway deployment configuration"
git push origin main
```

Railway will automatically detect changes and deploy! 🚂✨
