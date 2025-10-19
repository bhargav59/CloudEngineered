#!/bin/bash
# Manual Setup Script - Run this on EC2 after making repository public
# Usage: ssh -i terraform/cloudengineered-key.pem ec2-user@52.91.65.143 'bash -s' < manual_setup.sh

set -e

echo "=== CloudEngineered Manual Setup ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

cd /opt/cloudengineered || { echo "Creating /opt/cloudengineered"; mkdir -p /opt/cloudengineered; cd /opt/cloudengineered; }

echo "1. Cloning repository..."
if [ ! -d ".git" ]; then
    git clone https://github.com/bhargav59/CloudEngineered.git .
    git checkout main
else
    echo "Repository already cloned, pulling latest changes..."
    git pull
fi

echo ""
echo "2. Getting infrastructure details..."
# These will be passed from Terraform or set manually
DB_HOST="${db_host}"
DB_NAME="${db_name}"
DB_USER="${db_username}"
DB_PASSWORD="${db_password}"
REDIS_HOST="${redis_host}"
S3_BUCKET="${s3_bucket}"
AWS_REGION="${region}"

echo "Database: $DB_HOST"
echo "Redis: $REDIS_HOST"
echo ""

echo "3. Creating environment file..."
cat > .env.prod << 'ENVEOF'
# Django Configuration
DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_HOSTS=localhost,127.0.0.1,$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4),*.elb.amazonaws.com

# Database Configuration
DB_NAME=${DB_NAME:-cloudengineered}
DB_USER=${DB_USER:-cloudengineered}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=${DB_HOST}
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://${REDIS_HOST}:6379/0

# AWS Configuration
AWS_STORAGE_BUCKET_NAME=${S3_BUCKET}
AWS_S3_REGION_NAME=${AWS_REGION}

# Static and Media files
USE_S3=True
STATIC_URL=https://${S3_BUCKET}.s3.${AWS_REGION}.amazonaws.com/static/
MEDIA_URL=https://${S3_BUCKET}.s3.${AWS_REGION}.amazonaws.com/media/

# Celery
CELERY_BROKER_URL=redis://${REDIS_HOST}:6379/0
CELERY_RESULT_BACKEND=redis://${REDIS_HOST}:6379/0
ENVEOF

echo ""
echo "4. Creating required directories..."
mkdir -p logs staticfiles mediafiles
chmod 755 logs staticfiles mediafiles

echo ""
echo "5. Setting permissions..."
chown -R ec2-user:ec2-user /opt/cloudengineered

echo ""
echo "6. Waiting for database to be ready..."
for i in {1..30}; do
    if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
        echo "✅ Database is ready!"
        break
    fi
    echo "Waiting for database... ($i/30)"
    sleep 10
done

echo ""
echo "7. Checking if Docker Compose is installed..."
if [ ! -f "/usr/local/bin/docker-compose" ]; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo ""
echo "8. Building and starting application..."
cd /opt/cloudengineered
docker-compose -f docker-compose.prod.yml down || true
docker-compose -f docker-compose.prod.yml up -d --build

echo ""
echo "9. Waiting for application to start..."
sleep 30

echo ""
echo "10. Running migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

echo ""
echo "11. Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

echo ""
echo "12. Loading initial data..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py setup_initial_data || echo "Initial data already loaded or script not found"

echo ""
echo "13. Configuring Nginx..."
cat > /etc/nginx/conf.d/cloudengineered.conf << 'NGINXEOF'
upstream cloudengineered_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://cloudengineered_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
NGINXEOF

echo ""
echo "14. Starting Nginx..."
systemctl enable nginx
systemctl restart nginx

echo ""
echo "=== ✅ Setup Complete! ==="
echo ""
echo "Application URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "To check status:"
echo "  docker-compose -f /opt/cloudengineered/docker-compose.prod.yml ps"
echo ""
echo "To view logs:"
echo "  docker-compose -f /opt/cloudengineered/docker-compose.prod.yml logs -f web"
echo ""
echo "To create superuser:"
echo "  docker-compose -f /opt/cloudengineered/docker-compose.prod.yml exec web python manage.py createsuperuser"
