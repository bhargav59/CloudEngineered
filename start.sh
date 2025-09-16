#!/bin/bash

# Railway start script for CloudEngineered Django application
echo "🚀 Starting CloudEngineered application..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/app"

# Apply database migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    print('Creating superuser...')
    User.objects.create_superuser('admin', 'admin@cloudengineered.com', 'admin123')
    print('Superuser created successfully!')
else:
    print('Superuser already exists.')
" 2>/dev/null || echo "Superuser creation skipped (likely already exists)"

# Start the application
echo "🌟 Starting Django application with Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --worker-class gthread \
    --threads 2 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --log-level info \
    --access-logfile - \
    --error-logfile -