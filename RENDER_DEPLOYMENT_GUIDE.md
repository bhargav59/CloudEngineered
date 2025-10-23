# 🚀 Render.com Deployment Guide for CloudEngineered

## Why Render.com?

✅ **Best for Django**: Native Python support
✅ **Free Tier**: 750 hours/month (always-on for free)
✅ **PostgreSQL**: Free database included
✅ **Auto-Deploy**: Connects to GitHub
✅ **SSL**: Free HTTPS certificate
✅ **Easy Setup**: 5-minute deployment

---

## 📋 Prerequisites

- [x] GitHub account with CloudEngineered repository
- [x] Render.com account (sign up at https://render.com)
- [x] All code pushed to GitHub main branch

---

## 🎯 Step-by-Step Deployment

### **Step 1: Sign Up on Render.com**

1. Go to **https://render.com**
2. Click **"Get Started"**
3. **Sign up with GitHub** (recommended)
4. Authorize Render to access your repositories

---

### **Step 2: Create New Web Service**

1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Connect your **GitHub repository**:
   - If first time: Click "Connect GitHub"
   - Select **"bhargav59/CloudEngineered"**
   - Click **"Connect"**

---

### **Step 3: Configure Web Service**

Fill in the following settings:

#### **Basic Settings:**
```
Name: cloudengineered
Region: Singapore (or closest to you)
Branch: main
Runtime: Python 3
```

#### **Build & Deploy:**
```
Build Command: ./build.sh
Start Command: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2
```

#### **Instance Type:**
```
Plan: Free
```

---

### **Step 4: Add Environment Variables**

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

```env
PYTHON_VERSION=3.11.0
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
AI_FEATURES_ENABLED=False
OPENROUTER_ENABLED=False
CELERY_ENABLED=False
USE_S3=False
```

**Generate SECRET_KEY:**
Run in terminal:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
Add result:
```env
SECRET_KEY=<your-generated-secret-key>
```

**ALLOWED_HOSTS** (will add after getting domain):
```env
ALLOWED_HOSTS=.onrender.com
```

---

### **Step 5: Create PostgreSQL Database**

1. Click **"New +"** → **"PostgreSQL"**
2. Configure:
   ```
   Name: cloudengineered-db
   Region: Singapore (same as web service)
   Plan: Free
   ```
3. Click **"Create Database"**
4. Wait ~30 seconds for provisioning

---

### **Step 6: Link Database to Web Service**

1. Go back to your **Web Service** settings
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add:
   ```
   Key: DATABASE_URL
   Value: (Click "Select Database" → choose "cloudengineered-db" → "Internal Database URL")
   ```

---

### **Step 7: Deploy!**

1. Click **"Create Web Service"** (bottom of page)
2. Render will start building your app
3. Watch the logs for progress

**Expected Build Output:**
```
🔨 Starting Render build process...
📦 Upgrading pip...
📦 Installing Python dependencies...
📁 Collecting static files...
📦 Running database migrations...
  Applying contenttypes.0001_initial... OK
  ... (49 migrations)
👤 Creating superuser...
✅ Superuser created: admin/admin123
✅ Build completed successfully!

==> Starting service with 'gunicorn config.wsgi:application...'
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:10000
[INFO] Using worker: gthread
✅ Deploy live at https://cloudengineered.onrender.com
```

---

### **Step 8: Update ALLOWED_HOSTS**

After deployment, Render gives you a domain like:
```
https://cloudengineered.onrender.com
```

1. Go to **Environment** tab
2. Edit **ALLOWED_HOSTS** variable:
   ```env
   ALLOWED_HOSTS=cloudengineered.onrender.com,.onrender.com
   ```
3. Save changes (auto-redeploys)

---

## 🌐 Access Your Site

### **Your URLs:**

**Homepage:**
```
https://cloudengineered.onrender.com
```

**Admin Panel:**
```
https://cloudengineered.onrender.com/admin/
```

**Login:**
- Username: `admin`
- Password: `admin123`

⚠️ **CHANGE PASSWORD IMMEDIATELY!**

---

## 🔧 Post-Deployment Configuration

### **1. Change Admin Password**

1. Visit `/admin/`
2. Login with default credentials
3. Click **Users** → **admin**
4. Click **"Change password"**
5. Set strong password

### **2. Configure Custom Domain (Optional)**

1. Render Dashboard → Your Service → **Settings**
2. Scroll to **Custom Domain**
3. Click **"Add Custom Domain"**
4. Enter your domain: `cloudengineered.com`
5. Add DNS records in your domain provider:
   ```
   Type: CNAME
   Name: @
   Value: cloudengineered.onrender.com
   ```

### **3. Enable Email (Optional)**

Add to Environment Variables:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 📊 Free Tier Limits

**Web Service:**
- 750 hours/month (31 days = 744 hours) ✅
- 512MB RAM
- Spins down after 15 min inactivity
- Spins up on first request (~30 seconds)

**PostgreSQL:**
- 1GB storage
- Expires after 90 days (can renew)

**Bandwidth:**
- 100GB/month outbound

---

## 🚨 Troubleshooting

### **Build Failed**

**Check logs for:**
```
Error: No module named 'X'
```
**Solution:** Add missing package to `requirements/production-minimal.txt`

### **502 Bad Gateway**

**Cause:** App not starting properly

**Solution:**
1. Check logs for Python errors
2. Verify `DJANGO_SETTINGS_MODULE` is correct
3. Ensure `DATABASE_URL` is set

### **Static Files Not Loading**

**Cause:** Collectstatic failed

**Solution:**
1. Check build logs for "Collecting static files"
2. Verify `whitenoise` in requirements
3. Manual fix: Add to Environment:
   ```env
   DISABLE_COLLECTSTATIC=1
   ```

### **Database Connection Error**

**Cause:** DATABASE_URL not set or incorrect

**Solution:**
1. Verify PostgreSQL database created
2. Check DATABASE_URL environment variable
3. Use "Internal Database URL" not "External"

### **App Spins Down**

**Cause:** Free tier sleeps after 15 min inactivity

**Solution:**
- Upgrade to paid plan ($7/month for always-on)
- Or use cron job to ping every 10 minutes

---

## 🔄 Auto-Deploy from GitHub

**Render automatically redeploys when you push to GitHub!**

```bash
git add .
git commit -m "Update feature"
git push origin main
# Render detects push and redeploys automatically
```

---

## 💰 Cost Breakdown

**Free Tier:**
- Web Service: $0/month (750 hours)
- PostgreSQL: $0/month (1GB, 90 days)
- SSL Certificate: $0
- Bandwidth: $0 (up to 100GB)

**Total: $0/month** 🎉

**Paid Upgrade (Optional):**
- Starter: $7/month (always-on, no sleep)
- PostgreSQL: $7/month (persistent)

---

## ✅ Deployment Checklist

- [ ] Signed up on Render.com
- [ ] Connected GitHub repository
- [ ] Created Web Service
- [ ] Added environment variables
- [ ] Created PostgreSQL database
- [ ] Linked database to web service
- [ ] Deployed successfully
- [ ] Updated ALLOWED_HOSTS
- [ ] Tested homepage loads
- [ ] Logged into admin panel
- [ ] Changed admin password
- [ ] Verified all pages work
- [ ] Checked static files loading

---

## 🎊 Success!

Your CloudEngineered platform is now **LIVE ON THE INTERNET**! 🚀

**Features Working:**
✅ Beautiful homepage with Tailwind CSS
✅ Admin dashboard
✅ User authentication
✅ PostgreSQL database
✅ Static files with WhiteNoise
✅ SSL/HTTPS security
✅ All monetization features
✅ Contact forms
✅ Content management

**Features Disabled (Free Tier):**
❌ AI content generation
❌ Background tasks (Celery)
❌ Redis caching

---

## 📚 Additional Resources

- **Render Docs:** https://render.com/docs
- **Django Deployment:** https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Render Community:** https://community.render.com

---

## 🆘 Need Help?

If you encounter any issues:

1. **Check Render Logs:**
   - Dashboard → Your Service → Logs tab

2. **Common Errors:**
   - Build fails: Check requirements file
   - 502 error: Check Django settings
   - Static files: Check collectstatic ran

3. **Ask for Help:**
   - Render Community Forum
   - Stack Overflow (tag: render.com, django)

---

**🎉 Congratulations! Your site is now live on Render.com!** 🎉

**Next Steps:**
1. Share your URL: `https://cloudengineered.onrender.com`
2. Add content via admin panel
3. Customize your domain
4. Monitor performance in Render dashboard

**Deployment Time:** ~5-10 minutes
**Cost:** $0 (free tier)
**Uptime:** 24/7 (with 15min sleep on inactivity)

Enjoy your live Django application! 🚀✨
