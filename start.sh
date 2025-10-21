#!/bin/bash
set -e  # Exit on error

# Railway start script for CloudEngineered Django application
echo "🚀 Starting CloudEngineered application..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/app"

# Set default port if not provided by Railway
export PORT="${PORT:-8000}"

echo "📍 Using PORT: $PORT"

# Wait for database to be ready (optional but recommended)
echo "⏳ Waiting for database..."
python << END
import os
import time
import psycopg2
from urllib.parse import urlparse

max_retries = 30
retry_interval = 2

database_url = os.environ.get('DATABASE_URL')
if database_url:
    result = urlparse(database_url)
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port
            )
            conn.close()
            print("✅ Database is ready!")
            break
        except psycopg2.OperationalError:
            if i < max_retries - 1:
                print(f"⏳ Database not ready, retrying in {retry_interval}s... ({i+1}/{max_retries})")
                time.sleep(retry_interval)
            else:
                print("❌ Database connection failed after maximum retries")
                exit(1)
else:
    print("⚠️  DATABASE_URL not set, skipping database check")
END

# Apply database migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput || {
    echo "❌ Migration failed"
    exit 1
}

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput || {
    echo "⚠️  Static file collection failed, continuing anyway..."
}

# Create superuser if it doesn't exist (optional)
echo "👤 Checking for superuser..."
python manage.py shell << END 2>/dev/null || echo "⚠️  Superuser creation skipped"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    print('Creating superuser...')
    User.objects.create_superuser('admin', 'admin@cloudengineered.com', 'admin123')
    print('✅ Superuser created successfully!')
else:
    print('✅ Superuser already exists.')
END

# Start the application with Gunicorn
echo "🌟 Starting Django application with Gunicorn on port $PORT..."
echo "📊 Workers: 3, Threads per worker: 2"

exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT}" \
    --workers 3 \
    --worker-class gthread \
    --threads 2 \
    --worker-tmp-dir /dev/shm \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance