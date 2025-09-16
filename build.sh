#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # exit on error

# Install dependencies
pip install -r requirements/production.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Create cache table if needed
python manage.py createcachetable

# Load initial data (optional)
# python manage.py loaddata initial_data.json

echo "Build completed successfully!"