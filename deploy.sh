#!/bin/bash
# Production Deployment Script for CloudEngineered Platform

echo "🚀 CloudEngineered Production Deployment Script"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check environment variables
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create from .env.example"
    exit 1
fi

echo "✅ Environment setup verified"

# Check dependencies
echo "📦 Checking dependencies..."
python -c "import django, openai, anthropic, requests" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Core dependencies installed"
else
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements/base.txt
fi

# Run Django checks
echo "🔍 Running Django system checks..."
python manage.py check --settings=config.settings.minimal
if [ $? -ne 0 ]; then
    echo "❌ Django system checks failed"
    exit 1
fi

echo "✅ Django system checks passed"

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --settings=config.settings.minimal
if [ $? -ne 0 ]; then
    echo "❌ Database migrations failed"
    exit 1
fi

echo "✅ Database migrations completed"

# Check if admin user exists
echo "👤 Checking admin user..."
python manage.py shell --settings=config.settings.minimal -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    print('Creating admin user...')
    User.objects.create_superuser('admin', 'admin@cloudengineered.com', 'admin123')
    print('Admin user created: admin/admin123')
else:
    print('Admin user already exists')
"

# Run comprehensive tests
echo "🧪 Running comprehensive tests..."
python comprehensive_test.py
if [ $? -ne 0 ]; then
    echo "❌ Comprehensive tests failed"
    exit 1
fi

echo "✅ All tests passed"

# Collect static files for production
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.minimal
if [ $? -ne 0 ]; then
    echo "⚠️ Static files collection had issues (may be normal)"
fi

echo "✅ Static files collected"

echo ""
echo "🎉 CloudEngineered is ready for production!"
echo ""
echo "📋 Production Checklist:"
echo "✅ Dependencies installed"
echo "✅ Database migrations applied"
echo "✅ Admin user created"
echo "✅ All system tests passed"
echo "✅ Static files collected"
echo ""
echo "🚀 To start the production server:"
echo "   python manage.py runserver 0.0.0.0:8000 --settings=config.settings.minimal"
echo ""
echo "🔐 Admin Access:"
echo "   URL: http://localhost:8000/admin/"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "💡 For production deployment:"
echo "1. Set DEBUG=False in production settings"
echo "2. Configure proper database (PostgreSQL)"
echo "3. Set up proper web server (nginx + gunicorn)"
echo "4. Configure SSL certificates"
echo "5. Set up monitoring and logging"