#!/bin/bash

# CloudEngineered Platform Setup Script
# This script automates the initial setup of the Django platform

set -e  # Exit on any error

echo "🚀 CloudEngineered Platform Setup"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "This script must be run from the cloudengineered project root directory"
    exit 1
fi

print_status "Starting CloudEngineered platform setup..."

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python $required_version or higher is required. Found: $python_version"
    exit 1
else
    print_status "Python version check passed: $python_version"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing dependencies..."
if [ -f "requirements/development.txt" ]; then
    pip install -r requirements/development.txt
else
    print_error "requirements/development.txt not found"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please edit .env file with your specific configuration"
    else
        print_status "Creating basic .env file..."
        cat > .env << EOF
# Django Settings
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_NAME=cloudengineered
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis Settings
REDIS_URL=redis://localhost:6379/1

# Email Settings (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# API Keys (optional - add when available)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GITHUB_TOKEN=your-github-token-here

# Third-party Services (optional)
SENTRY_DSN=your-sentry-dsn-here
EOF
        print_status ".env file created with default values"
    fi
else
    print_status ".env file already exists"
fi

# Check PostgreSQL connection
print_status "Checking PostgreSQL connection..."
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL client not found. Please install PostgreSQL"
    print_warning "Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    print_warning "macOS: brew install postgresql"
else
    print_status "PostgreSQL client found"
fi

# Check Redis connection
print_status "Checking Redis connection..."
if ! command -v redis-cli &> /dev/null; then
    print_warning "Redis CLI not found. Please install Redis"
    print_warning "Ubuntu/Debian: sudo apt-get install redis-server"
    print_warning "macOS: brew install redis"
else
    if redis-cli ping &> /dev/null; then
        print_status "Redis is running"
    else
        print_warning "Redis is not running. Please start Redis server"
        print_warning "Ubuntu/Debian: sudo systemctl start redis-server"
        print_warning "macOS: brew services start redis"
    fi
fi

# Database setup
print_status "Setting up database..."

# Check if database exists
if command -v psql &> /dev/null; then
    if psql -lqt | cut -d \| -f 1 | grep -qw cloudengineered; then
        print_status "Database 'cloudengineered' already exists"
    else
        print_status "Creating database 'cloudengineered'..."
        createdb cloudengineered 2>/dev/null || print_warning "Could not create database. Please create it manually: createdb cloudengineered"
    fi
fi

# Run Django management commands
print_status "Running Django migrations..."
python manage.py migrate

print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Initialize platform data
print_status "Initializing platform with sample data..."
python manage.py init_platform

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit your .env file with the correct configuration"
# Initialize platform data
print_status "Initializing platform with sample data..."
python manage.py init_platform

# Create superuser prompt
echo ""
print_status "Setup completed successfully!"
echo ""
print_warning "Next steps:"
echo "1. Create a superuser account:"
echo "   python manage.py createsuperuser"
echo ""
echo "2. Start the development server:"
echo "   python manage.py runserver"
echo ""
echo "3. In another terminal, start Celery worker:"
echo "   celery -A config worker -l info"
echo ""
echo "4. In another terminal, start Celery beat:"
echo "   celery -A config beat -l info"
echo ""
echo "5. Access the platform:"
echo "   Main site: http://localhost:8000"
echo "   Admin panel: http://localhost:8000/admin"
echo ""
print_status "Happy coding! 🎉"
