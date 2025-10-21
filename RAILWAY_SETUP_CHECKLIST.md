# ✅ Railway Setup Checklist

## Pre-Deployment Checklist

### 1. GitHub Repository ✅
- [x] All code committed and pushed
- [x] Large files removed from history
- [x] Secrets cleaned from commits
- [x] `Dockerfile` optimized for Railway
- [x] `start.sh` with error handling
- [x] `railway.json` configuration created

---

## Railway Dashboard Setup

### 2. Create Railway Project
- [ ] Go to https://railway.app
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose `bhargav59/CloudEngineered` repository
- [ ] Select `main` branch

### 3. Add PostgreSQL Database
- [ ] In Railway Dashboard → Your Project
- [ ] Click "+ New" → "Database" → "PostgreSQL"
- [ ] Railway auto-creates `DATABASE_URL` environment variable
- [ ] Wait for database to provision (~30 seconds)

### 4. Configure Environment Variables

Go to: Railway Dashboard → Your Project → Variables

#### Required Variables (MUST SET):

```env
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
```

**SECRET_KEY** (Generate a secure key):
```bash
# Run this in terminal to generate:
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
Copy output and set:
```env
SECRET_KEY=<paste-generated-key-here>
```

**ALLOWED_HOSTS** (Get from Railway after first deploy):
```env
ALLOWED_HOSTS=your-app-name.up.railway.app
```
*(Replace `your-app-name` with actual Railway domain)*

#### Optional Variables:

**AI Services** (if using OpenRouter):
```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Email Configuration** (if using Gmail):
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
```

**Stripe** (if using payments):
```env
STRIPE_PUBLIC_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

**Google AdSense** (if using ads):
```env
ADSENSE_CLIENT_ID=ca-pub-your-id
ADSENSE_ENABLED=True
```

**Sentry** (for error tracking):
```env
SENTRY_DSN=https://your-sentry-dsn
```

### 5. Deploy Configuration
- [ ] Railway should auto-detect `railway.json`
- [ ] Verify: Settings → Build → Builder = "DOCKERFILE"
- [ ] Verify: Settings → Deploy → Runtime = "V2"
- [ ] Verify: Restarts enabled = "ON_FAILURE"

### 6. First Deployment
- [ ] Railway auto-deploys after GitHub connection
- [ ] Monitor build logs (can take 10-20 minutes for heavy dependencies)
- [ ] Wait for "✅ Deployment successful" message

### 7. Post-Deployment Verification

**Check Logs**:
- [ ] Railway Dashboard → Deployments → View Logs
- [ ] Look for: `📍 Using PORT: 8000`
- [ ] Look for: `✅ Database connected successfully!`
- [ ] Look for: `✅ Migrations completed successfully`
- [ ] Look for: `✅ Static files collected`
- [ ] Look for: `🚀 Starting Gunicorn server...`

**Test Application**:
- [ ] Click on Railway-provided domain (e.g., `https://your-app.up.railway.app`)
- [ ] Homepage loads successfully
- [ ] Admin panel accessible: `/admin/`
- [ ] Login with default credentials:
  - Username: `admin`
  - Password: `admin123`
  - **CHANGE THIS IMMEDIATELY!**

### 8. Security Configuration

**Change Admin Password**:
- [ ] Login to admin panel
- [ ] Go to Users → admin
- [ ] Click "Change password"
- [ ] Set strong password

**Update Environment Variables**:
- [ ] Regenerate `SECRET_KEY` (different from dev)
- [ ] Set `DEBUG=False` (production)
- [ ] Set proper `ALLOWED_HOSTS`

### 9. Optional: Custom Domain

**In Railway Dashboard**:
- [ ] Settings → Domains → Add Domain
- [ ] Enter your domain (e.g., `cloudengineered.com`)

**In DNS Provider**:
- [ ] Add CNAME record:
  ```
  Type: CNAME
  Name: @ (or www)
  Value: your-app.up.railway.app
  TTL: 3600
  ```

**Update ALLOWED_HOSTS**:
```env
ALLOWED_HOSTS=your-app.up.railway.app,cloudengineered.com,www.cloudengineered.com
```

### 10. Monitoring Setup

**Enable Metrics**:
- [ ] Railway Dashboard → Metrics
- [ ] Monitor: CPU, Memory, Network, Requests

**Setup Alerts** (Optional):
- [ ] Railway Discord webhook
- [ ] Email notifications for failures

### 11. Performance Testing

**Test Endpoints**:
- [ ] Homepage: `https://your-app.up.railway.app/`
- [ ] API: `https://your-app.up.railway.app/api/`
- [ ] Admin: `https://your-app.up.railway.app/admin/`
- [ ] Health check: `https://your-app.up.railway.app/health/`

**Load Testing** (Optional):
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 https://your-app.up.railway.app/
```

---

## Troubleshooting Common Issues

### Issue 1: Build Timeout
**Symptom**: Build fails after 10 minutes with timeout error

**Cause**: Heavy dependencies (torch, transformers) take too long to install

**Solutions**:
1. **Option A**: Remove heavy ML dependencies (if not needed):
   - Edit `requirements/base.txt`
   - Comment out: `torch`, `transformers`, `selenium`, `spacy`
   - Commit and push

2. **Option B**: Extend build timeout (Railway Pro plan):
   - Railway Dashboard → Settings → Build
   - Set timeout to 30 minutes

3. **Option C**: Use pre-built wheels:
   ```txt
   # In requirements/production.txt
   --find-links https://download.pytorch.org/whl/torch_stable.html
   torch==2.1.0+cpu
   ```

### Issue 2: Database Connection Failed
**Symptom**: Logs show `psycopg2.OperationalError: could not connect to server`

**Cause**: Database not provisioned or URL incorrect

**Solutions**:
1. Verify PostgreSQL plugin added
2. Check `DATABASE_URL` is set automatically
3. Restart deployment

### Issue 3: Static Files Not Loading
**Symptom**: CSS/JS files return 404 errors

**Cause**: Static files not collected or WhiteNoise not configured

**Solutions**:
1. Check logs for "✅ Static files collected"
2. Verify `STATIC_ROOT` and `STATIC_URL` in settings
3. Ensure `whitenoise` in `requirements/production.txt`
4. Restart application

### Issue 4: ALLOWED_HOSTS Error
**Symptom**: `Invalid HTTP_HOST header` error

**Cause**: Railway domain not in `ALLOWED_HOSTS`

**Solution**:
```env
ALLOWED_HOSTS=your-actual-app-name.up.railway.app
```
Get exact domain from Railway Dashboard → Settings → Domains

### Issue 5: 502 Bad Gateway
**Symptom**: Railway shows "Application failed to respond"

**Cause**: Application not binding to correct PORT

**Solutions**:
1. Check logs for `📍 Using PORT: <number>`
2. Verify `start.sh` uses `$PORT` variable
3. Ensure Gunicorn binds to `0.0.0.0:$PORT`

---

## Quick Reference: Railway CLI Commands

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs -f

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Restart app
railway restart

# Check status
railway status

# Open app in browser
railway open
```

---

## Environment Variables Quick Copy

**Minimal Configuration** (copy to Railway Variables):

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<generate-with-python-command>
DEBUG=False
ALLOWED_HOSTS=<your-railway-domain>.up.railway.app
```

**With AI Features**:

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<generate-with-python-command>
DEBUG=False
ALLOWED_HOSTS=<your-railway-domain>.up.railway.app
OPENROUTER_API_KEY=sk-or-v1-your-key
```

**Full Production**:

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<generate-with-python-command>
DEBUG=False
ALLOWED_HOSTS=<your-railway-domain>.up.railway.app
OPENROUTER_API_KEY=sk-or-v1-your-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
STRIPE_SECRET_KEY=sk_live_your_key
SENTRY_DSN=https://your-sentry-dsn
```

---

## Success Criteria

Your deployment is successful when:
- ✅ Build completes without errors
- ✅ Application accessible via Railway domain
- ✅ Admin panel loads and login works
- ✅ Database migrations applied
- ✅ Static files serving correctly
- ✅ No errors in Railway logs
- ✅ Health check returns 200 OK
- ✅ Response time < 2 seconds

---

## Next Steps After Successful Deployment

1. **Security Hardening**:
   - Change admin password
   - Rotate SECRET_KEY
   - Enable 2FA for Railway account
   - Review Django security checklist

2. **Performance Optimization**:
   - Enable Redis for caching
   - Configure CDN for static files
   - Optimize database queries
   - Add database indexes

3. **Monitoring**:
   - Setup Sentry error tracking
   - Configure uptime monitoring
   - Enable Railway metrics alerts
   - Setup log aggregation

4. **Backup Strategy**:
   - Configure automated database backups
   - Document recovery procedures
   - Test restore process

5. **Documentation**:
   - Update README with production URL
   - Document environment variables
   - Create runbook for common tasks

---

**🎉 Your CloudEngineered application is now live on Railway!**

Visit: `https://<your-app>.up.railway.app`

Admin: `https://<your-app>.up.railway.app/admin/`
- Username: `admin`
- Password: `admin123` (CHANGE THIS!)

---

**Need Help?**
- Railway Docs: https://docs.railway.app
- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/
- Railway Discord: https://discord.gg/railway
