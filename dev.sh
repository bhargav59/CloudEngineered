#!/bin/bash

# Development start script for CloudEngineered
echo "🚀 Starting CloudEngineered development server..."

# Kill any existing Django server processes
pkill -f "manage.py runserver" 2>/dev/null || true

# Set required environment variables
export DJANGO_SETTINGS_MODULE=config.settings.development

# Apply database migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "👤 Checking for admin user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    print('Creating superuser...')
    User.objects.create_superuser('admin', 'admin@cloudengineered.com', 'admin123')
    print('Superuser created successfully!')
else:
    print('Superuser already exists.')
"

# Create initial data if needed
echo "📊 Checking for initial data..."
python manage.py shell -c "
from apps.tools.models import Category, Tool
if Category.objects.count() == 0 or Tool.objects.count() == 0:
    print('No data found. Running setup_initial_data.py...')
    import subprocess
    subprocess.run(['python', 'setup_initial_data.py'])
else:
    print(f'Data exists: {Category.objects.count()} categories, {Tool.objects.count()} tools')
"

echo ""
echo "===================================================="
echo "🚀 CloudEngineered is running!"
echo "===================================================="
echo "🌐 Main site: http://127.0.0.1:8000/"
echo "📊 Admin dashboard: http://127.0.0.1:8000/admin/"
echo "🔑 Username: admin"
echo "🔑 Password: admin123"
echo "🤖 AI Dashboard: http://127.0.0.1:8000/admin/ai-dashboard/"
echo "===================================================="
echo ""

# Run the server with verbosity to catch issues
python manage.py runserver --verbosity 2