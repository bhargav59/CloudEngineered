"""
CloudEngineered Platform Development Guide

This document provides step-by-step instructions for setting up and developing the CloudEngineered platform.
"""

# CloudEngineered Platform - Complete Setup & Development Guide

## 🎯 Overview

CloudEngineered is a production-ready Django platform for cloud engineering tool reviews with AI-powered content generation. This guide will walk you through the complete setup and development process.

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed
- **PostgreSQL 14+** installed and running
- **Redis 7+** installed and running
- **Git** for version control
- **Node.js 18+** (for Tailwind CSS)
- **API Keys** for OpenAI and Anthropic (optional for AI features)

## 🚀 Quick Setup

### 1. Initial Setup

```bash
# Navigate to the project directory
cd cloudengineered

# Make setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit the .env file with your settings
nano .env
```

**Key environment variables to configure:**

```env
SECRET_KEY=your-very-secret-key-here
DEBUG=True
DB_PASSWORD=your-database-password
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GITHUB_TOKEN=your-github-personal-access-token
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb cloudengineered

# Run migrations
python manage.py migrate

# Initialize platform with sample data
python manage.py init_platform

# Create superuser
python manage.py createsuperuser
```

### 4. Start Development Servers

**Terminal 1 - Django Development Server:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
celery -A config worker -l info
```

**Terminal 3 - Celery Beat Scheduler:**
```bash
celery -A config beat -l info
```

## 🌐 Access Points

After setup, you can access:

- **Main Site**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/docs/ (development only)

## 🏗️ Project Structure

```
cloudengineered/
├── apps/                       # Django applications
│   ├── core/                  # Core functionality
│   ├── users/                 # User management
│   ├── tools/                 # Tool models and views
│   ├── content/               # Articles and content
│   ├── automation/            # AI and automation
│   ├── analytics/             # Custom analytics
│   ├── affiliates/            # Affiliate management
│   └── api/                   # REST API endpoints
├── config/                    # Django configuration
│   ├── settings/              # Environment-specific settings
│   ├── urls.py               # Main URL configuration
│   ├── wsgi.py               # WSGI configuration
│   └── celery.py             # Celery configuration
├── templates/                 # HTML templates
├── static/                    # Static files (CSS, JS, images)
├── requirements/              # Python dependencies
├── docker/                    # Docker configuration
└── scripts/                   # Utility scripts
```

## 🔧 Development Workflow

### Adding New Features

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Development Process**
   - Add models to appropriate app
   - Create views and templates
   - Add URL patterns
   - Write tests
   - Update documentation

3. **Code Quality Checks**
   ```bash
   # Format code
   black .
   
   # Check code quality
   flake8 .
   
   # Run tests
   python manage.py test
   ```

4. **Database Changes**
   ```bash
   # Create migrations
   python manage.py makemigrations
   
   # Apply migrations
   python manage.py migrate
   ```

### Key Development Commands

```bash
# Create new Django app
python manage.py startapp app_name

# Shell access
python manage.py shell

# Database shell
python manage.py dbshell

# Collect static files
python manage.py collectstatic

# Check for issues
python manage.py check

# Create superuser
python manage.py createsuperuser
```

## 🤖 AI Content Generation

### Setting Up AI Services

1. **OpenAI Setup**
   - Get API key from https://platform.openai.com/
   - Add to .env: `OPENAI_API_KEY=your-key`

2. **Anthropic Setup**
   - Get API key from https://console.anthropic.com/
   - Add to .env: `ANTHROPIC_API_KEY=your-key`

### Using AI Features

```bash
# Generate content for a specific tool
python manage.py shell
>>> from apps.automation.tasks import generate_tool_content
>>> generate_tool_content.delay(tool_id=1)

# Scan GitHub for new tools
>>> from apps.automation.tasks import scan_github_for_tools
>>> scan_github_for_tools.delay()
```

## 🐳 Docker Development

### Using Docker Compose

```bash
# Start all services
cd docker
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Services

- **web**: Django application server
- **db**: PostgreSQL database
- **redis**: Redis cache and message broker
- **celery**: Background task worker
- **celery-beat**: Task scheduler
- **nginx**: Reverse proxy (production)

## 📊 Database Models

### Core Models

**User Management:**
- `User`: Extended Django user with professional info
- `UserProfile`: Additional profile data and preferences
- `UserActivity`: Track user actions for analytics

**Tool Management:**
- `Category`: Tool categories (CI/CD, Monitoring, etc.)
- `Tool`: Core tool model with comprehensive metadata
- `ToolComparison`: Side-by-side comparisons
- `ToolReview`: User reviews and ratings

**Content Management:**
- `Article`: Blog posts, reviews, guides
- `Comment`: User comments on content
- `Newsletter`: Email campaigns
- `FAQ`: Frequently asked questions

## 🔄 Automation & Tasks

### Celery Tasks

The platform includes several automated tasks:

```python
# Hourly: Scan GitHub for new tools
scan_github_for_tools.delay()

# Every 6 hours: Generate trending content
generate_trending_content.delay()

# Every 2 hours: Update GitHub stats
update_tool_github_stats.delay()

# Weekly: Send newsletter
send_weekly_newsletter.delay()

# Daily: Cleanup old data
cleanup_old_analytics.delay()
```

### Monitoring Tasks

```bash
# Check Celery worker status
celery -A config inspect active

# Check scheduled tasks
celery -A config inspect scheduled

# Purge all tasks
celery -A config purge
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.tools

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Creates htmlcov/index.html
```

### Test Categories

- **Unit Tests**: Model methods and utilities
- **Integration Tests**: Views and API endpoints
- **Task Tests**: Celery task execution
- **Performance Tests**: Database query optimization

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure secure `SECRET_KEY`
- [ ] Set up SSL certificates
- [ ] Configure production database
- [ ] Set up Redis clustering
- [ ] Configure CDN for static files
- [ ] Set up error monitoring (Sentry)
- [ ] Configure backup strategy
- [ ] Set up monitoring and logging

### Environment Variables for Production

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_HOST=your-db-host
DB_PASSWORD=your-secure-db-password
REDIS_URL=redis://your-redis-host:6379/1
SENTRY_DSN=your-sentry-dsn
USE_S3=True
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
```

## 📈 Performance Optimization

### Database Optimization

```python
# Use select_related for foreign keys
Tool.objects.select_related('category')

# Use prefetch_related for many-to-many
Article.objects.prefetch_related('tags')

# Database indexes are already configured in models
```

### Caching Strategy

```python
# View-level caching
@cache_page(60 * 15)  # 15 minutes
def tool_list(request):
    pass

# Template fragment caching
{% load cache %}
{% cache 500 sidebar %}
    <!-- sidebar content -->
{% endcache %}
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Check database exists
   psql -l | grep cloudengineered
   ```

2. **Redis Connection Error**
   ```bash
   # Check Redis status
   redis-cli ping
   ```

3. **Celery Tasks Not Running**
   ```bash
   # Check worker status
   celery -A config inspect active
   
   # Restart worker
   celery -A config worker -l info
   ```

4. **Static Files Not Loading**
   ```bash
   # Collect static files
   python manage.py collectstatic --clear
   ```

### Debug Mode

```python
# In development, add to settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 📚 API Usage

### Authentication

```bash
# Get API token
curl -X POST http://localhost:8000/api/auth/login/ \
  -d '{"username": "your-username", "password": "your-password"}'
```

### Example API Calls

```bash
# List tools
curl -H "Authorization: Token your-token" \
  http://localhost:8000/api/tools/

# Get tool details
curl -H "Authorization: Token your-token" \
  http://localhost:8000/api/tools/1/

# Search tools
curl -H "Authorization: Token your-token" \
  "http://localhost:8000/api/search/?q=kubernetes"
```

## 🤝 Contributing

### Development Standards

- Follow PEP 8 for Python code style
- Use meaningful variable and function names
- Add docstrings for all classes and functions
- Write tests for new functionality
- Update documentation for new features

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push and create pull request
git push origin feature/new-feature
```

## 📞 Getting Help

- **Documentation**: Check this guide and IMPLEMENTATION.md
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Community**: Join our Discord/Slack (if available)

---

## 🎉 Next Steps

After completing the setup:

1. **Explore the Admin Panel**: Add some tools and categories
2. **Test AI Features**: Generate some content using the AI services
3. **Customize the UI**: Modify templates and add your branding
4. **Set up Analytics**: Configure Google Analytics and monitoring
5. **Deploy to Staging**: Test the deployment process

The platform is now ready for development and customization!
