#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🔨 Starting Render build process..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements/production-minimal.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --no-input

# Create superuser if it doesn't exist
echo "👤 Creating superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@cloudengineered.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('✅ Superuser already exists')
END

echo "✅ Build completed successfully!"
