#!/bin/bash

# Development start script for CloudEngineered Django application
echo "🚀 Starting CloudEngineered development server..."

# Kill any existing Django server processes
echo "🛑 Stopping any existing servers..."
pkill -f "manage.py runserver" || true

# Set the Django settings module explicitly
export DJANGO_SETTINGS_MODULE=config.settings.development

# Apply database migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
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

# Create missing templates directory structure if needed
echo "📁 Ensuring template directories exist..."
mkdir -p templates/core

# Check for missing templates and create them
if [ ! -f "templates/core/about.html" ]; then
    echo "Creating about.html template..."
    cat > templates/core/about.html << 'EOL'
{% extends "base.html" %}

{% block title %}About Us - {{ site_name }}{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-4">About CloudEngineered</h1>
    <p class="text-lg text-gray-700">
        CloudEngineered is a platform dedicated to providing comprehensive reviews, comparisons, and guides for cloud engineering and DevOps tools. Our mission is to help developers and engineers make informed decisions about the tools they use every day.
    </p>
</div>
{% endblock %}
EOL
fi

# Start the development server
echo "🌟 Starting Django development server..."
python manage.py runserver 0.0.0.0:8000