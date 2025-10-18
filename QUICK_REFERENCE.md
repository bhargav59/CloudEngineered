# CloudEngineered - Quick Reference for Testers

## 🚀 Quick Start

### Start Application
```bash
# Option 1: Start fresh
python manage.py runserver 0.0.0.0:8000

# Option 2: Check if already running
ps aux | grep runserver

# Access via browser
http://localhost:8000
# Or use Codespaces forwarded URL
```

### Admin Access
```bash
# Create superuser
python manage.py createsuperuser

# Access admin panel
http://localhost:8000/admin/
```

---

## 📍 Key URLs to Test

| Feature | URL | Auth Required | Priority |
|---------|-----|---------------|----------|
| **Homepage** | `/` | No | ⭐ High |
| **Categories** | `/tools/categories/` | No | ⭐ High |
| **Category Tools** | `/tools/infrastructure-as-code/` | No | ⭐ High |
| **Tool Detail** | `/tools/infrastructure-as-code/terraform/` | No | ⭐ High |
| **Search** | `/search/?q=docker` | No | ⭐ High |
| **Misspelled Search** | `/search/?q=doxker` | No | ⭐ High (Critical Test) |
| **Comparisons List** | `/tools/comparisons/` | No | Medium |
| **Comparison Detail** | `/tools/comparisons/docker-vs-podman/` | No | Medium |
| **Articles List** | `/content/articles/` | No | Medium |
| **Article Detail** | `/content/articles/top-10-devops-tools-2025/` | No | Medium |
| **Write Review** | `/tools/infrastructure-as-code/terraform/review/` | ✅ Yes | Medium |
| **Admin Panel** | `/admin/` | ✅ Superuser | Low |
| **API - Tools** | `/api/tools/` | No | Medium |
| **API - Search** | `/api/search/?q=kubernetes` | No | Medium |

---

## 🧪 Quick Test Commands

### Test All Main Pages
```bash
# Homepage
curl -I http://localhost:8000/
# Expected: HTTP/1.1 200 OK

# Categories
curl -I http://localhost:8000/tools/categories/
# Expected: HTTP/1.1 200 OK

# Search (valid)
curl -I "http://localhost:8000/search/?q=docker"
# Expected: HTTP/1.1 200 OK

# Search (misspelling) - CRITICAL TEST!
curl -I "http://localhost:8000/search/?q=doxker"
# Expected: HTTP/1.1 200 OK (NOT 500!)

# Articles
curl -I http://localhost:8000/content/articles/
# Expected: HTTP/1.1 200 OK

# Comparisons
curl -I http://localhost:8000/tools/comparisons/
# Expected: HTTP/1.1 200 OK
```

### Run Automated Test Script
```bash
# Save as test_webapp.sh
cat > test_webapp.sh << 'EOF'
#!/bin/bash
echo "🧪 CloudEngineered Quick Test"
echo "=============================="

BASE="http://localhost:8000"

# Test homepage
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE/)
[ "$STATUS" = "200" ] && echo "✅ Homepage: PASS" || echo "❌ Homepage: FAIL ($STATUS)"

# Test categories
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE/tools/categories/)
[ "$STATUS" = "200" ] && echo "✅ Categories: PASS" || echo "❌ Categories: FAIL ($STATUS)"

# Test search
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/search/?q=docker")
[ "$STATUS" = "200" ] && echo "✅ Search: PASS" || echo "❌ Search: FAIL ($STATUS)"

# Test misspelling (CRITICAL)
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/search/?q=doxker")
[ "$STATUS" = "200" ] && echo "✅ Misspelling: PASS" || echo "❌ Misspelling: FAIL ($STATUS)"

# Test articles
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE/content/articles/)
[ "$STATUS" = "200" ] && echo "✅ Articles: PASS" || echo "❌ Articles: FAIL ($STATUS)"

# Test comparisons
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE/tools/comparisons/)
[ "$STATUS" = "200" ] && echo "✅ Comparisons: PASS" || echo "❌ Comparisons: FAIL ($STATUS)"

echo ""
echo "✅ Tests Complete!"
EOF

# Run it
chmod +x test_webapp.sh
./test_webapp.sh
```

---

## ✅ What to Check on Every Page

### Visual Checks
- [ ] Page loads (200 status, no 404 or 500)
- [ ] No console errors (Press F12 → Console tab)
- [ ] Font Awesome icons display (not boxes)
- [ ] Images load properly
- [ ] All links work (no broken links)
- [ ] Mobile responsive (resize browser)

### Content Checks
- [ ] No Lorem Ipsum or placeholder text
- [ ] No raw JSON (e.g., `]}}`, `{`)
- [ ] Markdown rendered (not raw `##`, `**`)
- [ ] Code blocks syntax highlighted
- [ ] Lists display properly (bullet/numbered)

### Functional Checks
- [ ] Forms validate correctly
- [ ] Buttons clickable with feedback
- [ ] Search returns results
- [ ] Navigation works
- [ ] Login/logout functional

---

## 🐛 Common Issues - All FIXED ✅

### Issue 1: Font Awesome Icons Not Showing
**Status:** ✅ FIXED  
**Test:** Navigate to homepage or `/tools/categories/`  
**Expected:** All 6 category icons display (no boxes)

### Issue 2: Search Misspelling Crashes (500 Error)
**Status:** ✅ FIXED  
**Test:** Search for "doxker" or "kubernetis"  
**Expected:** Returns 200 OK (not 500), shows "no results" or suggestions

### Issue 3: Article Slugs with Slashes
**Status:** ✅ FIXED  
**Test:** Check all article URLs  
**Expected:** No `/` in slugs (all use `-`)

**Verify with:**
```bash
python manage.py fix_slugs
# Expected output: "0 invalid slugs found"
```

### Issue 4: Raw JSON on Comparison Pages
**Status:** ✅ FIXED  
**Test:** Navigate to `/tools/comparisons/docker-vs-podman/`  
**Expected:** Formatted sections, no raw `{`, `}`, `]`

### Issue 5: Markdown Not Rendering
**Status:** ✅ FIXED  
**Test:** Visit any tool or article page  
**Expected:** Formatted text, not raw markdown (`##`, `**`, etc.)

### Issue 6: Review Form Not Working
**Status:** ✅ FIXED  
**Test:** Click "Write a Review" (requires login)  
**Expected:** Shows review form, can submit successfully

---

## 📊 Performance Targets

| Metric | Target | How to Check |
|--------|--------|--------------|
| **Response Time (cached)** | < 50ms | Use Django Debug Toolbar |
| **Response Time (uncached)** | < 500ms | First page load |
| **Cache Hit Rate** | > 85% | Check Redis stats |
| **Error Rate** | < 0.1% | Monitor error logs |
| **Concurrent Users** | 10,000+ | Load testing (optional) |
| **Page Load Score** | > 90 | Google PageSpeed Insights |

---

## 🔒 Security Checks

### Every Form Should Have:
- [ ] CSRF token present (`{% csrf_token %}` in HTML)
- [ ] Validation on required fields
- [ ] Error messages for invalid input
- [ ] Protection against XSS (HTML escaped)

### Authentication:
- [ ] Login required for write operations
- [ ] Anonymous users redirected to login
- [ ] Admin panel requires superuser
- [ ] API keys not visible in frontend

### Test Security:
```bash
# Check CSRF protection
curl -X POST http://localhost:8000/tools/infrastructure-as-code/terraform/review/
# Expected: 403 Forbidden (CSRF verification failed)

# Check admin requires auth
curl -I http://localhost:8000/admin/
# Expected: 302 redirect to login
```

---

## 📝 Test Data

### Sample Tools (500+ in database)
- **Infrastructure as Code:** Terraform, Ansible, Pulumi, Chef, Puppet
- **Containerization:** Docker, Podman
- **Container Management:** Kubernetes
- **CI/CD:** Jenkins, GitLab CI, GitHub Actions
- **Cloud Platforms:** AWS, Azure, GCP (24 tools)
- **Monitoring:** Prometheus, Grafana, New Relic, Datadog

### Sample Comparisons (25+)
- Docker vs Podman
- Terraform vs Pulumi
- Kubernetes vs Docker Swarm

### Sample Articles (127 published)
- "Top 10 DevOps Tools Every Developer Should Know in 2025"
- "Best CI/CD Tools for Modern DevOps Teams"
- "AWS vs Google Cloud vs Azure: Complete Cloud Comparison"

### Test User Credentials
```bash
# Create test user
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('testuser', 'test@example.com', 'testpass123')

# Use for testing
Username: testuser
Password: testpass123
```

---

## 🆘 Troubleshooting

### If Page Shows Error:
1. **Check Browser Console** (F12 → Console)
   - Look for JavaScript errors
   - Check network tab for failed requests

2. **Check Django Logs**
   - Terminal running `runserver`
   - Look for stack trace

3. **Common Fixes**:
   ```bash
   # Clear cache
   python manage.py clear_cache
   
   # Restart server
   # Press Ctrl+C, then restart
   python manage.py runserver 0.0.0.0:8000
   
   # Check database
   python manage.py check
   
   # Fix slugs
   python manage.py fix_slugs --fix
   ```

### If Static Files Don't Load:
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_URL in settings
echo $STATIC_URL
```

### If Database Errors:
```bash
# Check migrations
python manage.py showmigrations

# Apply migrations
python manage.py migrate

# Reset database (CAUTION: deletes data)
rm db.sqlite3
python manage.py migrate
python setup_initial_data.py
```

---

## 📞 Quick Reference

### Important Files
```
/workspaces/CloudEngineered/
├── TESTING_GUIDE.md          # Full testing documentation
├── test_webapp.sh            # Automated test script
├── manage.py                 # Django management
├── db.sqlite3               # Database
├── requirements/            # Python dependencies
│   ├── base.txt
│   └── development.txt
└── apps/                    # Application code
    ├── core/                # Homepage, search
    ├── tools/               # Tool catalog
    ├── content/             # Articles
    └── api/                 # REST API
```

### Useful Commands
```bash
# Django
python manage.py runserver 0.0.0.0:8000   # Start server
python manage.py test                     # Run tests
python manage.py check                    # Check for issues
python manage.py shell                    # Django shell

# Database
python manage.py migrate                  # Apply migrations
python manage.py makemigrations          # Create migrations
python manage.py dbshell                 # Database shell

# Users
python manage.py createsuperuser         # Create admin
python manage.py changepassword <user>   # Change password

# Utilities
python manage.py fix_slugs               # Fix article slugs
python manage.py clear_cache             # Clear Redis cache
```

---

## 📋 Testing Priority

### High Priority (Test First)
1. ✅ Homepage loads
2. ✅ Search works (including misspellings!)
3. ✅ Tool pages load and display correctly
4. ✅ No 500 errors on any page
5. ✅ Font Awesome icons display

### Medium Priority
1. ✅ Articles render markdown correctly
2. ✅ Comparisons format properly (no raw JSON)
3. ✅ Review system works
4. ✅ API endpoints return JSON

### Low Priority
1. ✅ SEO metadata correct
2. ✅ Analytics tracking
3. ✅ Edge cases and unusual inputs
4. ✅ UI/UX polish

---

## 🎯 Quick Win Tests (5 minutes)

Run these first to verify core functionality:

```bash
#!/bin/bash
# Quick 5-minute test suite

echo "🎯 Quick Win Tests"
echo "=================="

BASE="http://localhost:8000"

# 1. Homepage
curl -s -o /dev/null -w "Homepage: %{http_code}\n" $BASE/

# 2. Categories
curl -s -o /dev/null -w "Categories: %{http_code}\n" $BASE/tools/categories/

# 3. Tool Detail
curl -s -o /dev/null -w "Tool Detail: %{http_code}\n" $BASE/tools/infrastructure-as-code/terraform/

# 4. Search (valid)
curl -s -o /dev/null -w "Search (valid): %{http_code}\n" "$BASE/search/?q=docker"

# 5. Search (misspell) - CRITICAL!
curl -s -o /dev/null -w "Search (misspell): %{http_code}\n" "$BASE/search/?q=doxker"

# 6. Comparison
curl -s -o /dev/null -w "Comparison: %{http_code}\n" $BASE/tools/comparisons/docker-vs-podman/

# 7. Article
curl -s -o /dev/null -w "Article: %{http_code}\n" $BASE/content/articles/top-10-devops-tools-2025/

# 8. API
curl -s -o /dev/null -w "API: %{http_code}\n" $BASE/api/tools/

echo ""
echo "All should show: 200"
echo "If any show 404 or 500, investigate immediately!"
```

---

**Document Version:** 1.0  
**Last Updated:** October 17, 2025  
**Status:** All known issues fixed ✅  

**For full documentation, see:** `TESTING_GUIDE.md`

---

**Happy Testing! 🚀**
