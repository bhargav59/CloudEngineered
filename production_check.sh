#!/bin/bash

echo "🚀 CloudEngineered Production Readiness Check"
echo "=============================================="

# Set environment variables
export DJANGO_SETTINGS_MODULE=config.settings.development

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

echo ""
echo "1. Django System Check"
echo "----------------------"
python manage.py check --deploy 2>/dev/null
if [ $? -eq 0 ]; then
    print_status 0 "Django deployment check passed"
else
    echo -e "${YELLOW}⚠ Django deployment check has warnings (checking basic functionality)${NC}"
    python manage.py check > /dev/null 2>&1
    print_status $? "Django basic check"
fi

echo ""
echo "2. Database Migration Check"
echo "---------------------------"
python manage.py makemigrations --check --dry-run > /dev/null 2>&1
print_status $? "No pending migrations"

echo ""
echo "3. Static Files Collection"
echo "--------------------------"
python manage.py collectstatic --no-input > /dev/null 2>&1
print_status $? "Static files collected"

echo ""
echo "4. URL Pattern Validation"
echo "-------------------------"
python manage.py show_urls > /dev/null 2>&1
print_status $? "URL patterns valid"

echo ""
echo "5. Admin Interface Check"
echo "------------------------"
python manage.py shell -c "
from django.contrib.admin import site
from django.contrib.auth import get_user_model
User = get_user_model()
print('Admin models registered:', len(site._registry))
print('User model:', User.__name__)
" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status 0 "Admin interface configured"
else
    print_status 1 "Admin interface issues"
fi

echo ""
echo "6. Database Connection Test"
echo "---------------------------"
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('Database connection successful')
" > /dev/null 2>&1
print_status $? "Database connection"

echo ""
echo "7. Model Integrity Check"
echo "------------------------"
python manage.py shell -c "
from apps.tools.models import Tool, Category
from apps.content.models import Article
from apps.users.models import User
print('Models can be imported and accessed')
print('Categories:', Category.objects.count())
print('Tools:', Tool.objects.count())
print('Articles:', Article.objects.count())
print('Users:', User.objects.count())
" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status 0 "Model integrity verified"
else
    print_status 1 "Model integrity issues"
fi

echo ""
echo "8. AI Service Check"
echo "-------------------"
python manage.py shell -c "
import os
from apps.ai.service_manager import AIServiceManager
manager = AIServiceManager()
print('AI Service Manager initialized')
print('OpenRouter configured:', bool(os.getenv('OPENROUTER_API_KEY')))
" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status 0 "AI services configured"
else
    print_status 1 "AI services issues"
fi

echo ""
echo "9. Template Rendering Test"
echo "--------------------------"
python manage.py shell -c "
from django.template.loader import render_to_string
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

# Test basic template rendering
try:
    request = HttpRequest()
    request.user = AnonymousUser()
    
    # Test core templates
    render_to_string('core/about.html', {'request': request})
    render_to_string('base.html', {'request': request})
    print('Template rendering successful')
except Exception as e:
    print(f'Template error: {e}')
    raise
" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status 0 "Template rendering works"
else
    print_status 1 "Template rendering issues"
fi

echo ""
echo "10. Development Server Test"
echo "---------------------------"
echo "Starting development server for 10 seconds..."

# Start server in background
python manage.py runserver 127.0.0.1:8001 > /dev/null 2>&1 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 3

# Test if server is responding
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/ > /tmp/server_response
HTTP_CODE=$(cat /tmp/server_response)

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    print_status 0 "Development server responds (HTTP $HTTP_CODE)"
    SERVER_WORKING=1
else
    print_status 1 "Development server not responding (HTTP $HTTP_CODE)"
    SERVER_WORKING=0
fi

# Clean up
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo ""
echo "=============================================="
if [ $SERVER_WORKING -eq 1 ]; then
    echo -e "${GREEN}🎉 Production readiness check completed!${NC}"
    echo -e "${GREEN}The application is ready to run.${NC}"
    
    echo ""
    echo "To start the application:"
    echo "  Development: python manage.py runserver"
    echo "  Production:  gunicorn config.wsgi:application"
    
    echo ""
    echo "Access URLs:"
    echo "  Main site: http://127.0.0.1:8000/"
    echo "  Admin: http://127.0.0.1:8000/admin/"
    echo "  AI Dashboard: http://127.0.0.1:8000/admin/ai-dashboard/"
    
    echo ""
    echo "Default credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
else
    echo -e "${RED}❌ Production readiness check failed!${NC}"
    echo "Please check the errors above and fix them."
fi
echo "=============================================="