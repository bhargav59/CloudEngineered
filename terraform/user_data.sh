#!/bin/bash
# CloudEngineered EC2 User Data Script
# This script runs on EC2 instance launch to set up the application

set -e

# Log all output
exec > >(tee /var/log/user-data.log) 2>&1

echo "Starting CloudEngineered setup..."

# Update system packages
yum update -y

# Install required packages
yum install -y \
    docker \
    git \
    python3 \
    python3-pip \
    postgresql \
    postgresql-devel \
    gcc \
    python3-devel \
    nginx \
    certbot \
    python3-certbot-nginx

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create application directory
mkdir -p /opt/cloudengineered
cd /opt/cloudengineered

# Clone repository
git clone https://github.com/bhargav59/CloudEngineered.git .
git checkout main

# Create environment file
cat > .env.prod << EOF
# Django Configuration
DEBUG=False
SECRET_KEY=${SECRET_KEY:-$(openssl rand -hex 32)}
ALLOWED_HOSTS=localhost,127.0.0.1,${PUBLIC_IP:-127.0.0.1},${LOAD_BALANCER_DNS:-127.0.0.1}

# Database Configuration
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=${DB_HOST}
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://${REDIS_HOST}:6379/0

# AWS Configuration
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
AWS_STORAGE_BUCKET_NAME=${S3_BUCKET}
AWS_S3_REGION_NAME=${AWS_REGION}
AWS_S3_CUSTOM_DOMAIN=${S3_BUCKET}.s3.${AWS_REGION}.amazonaws.com

# Static and Media files
STATIC_URL=https://${CLOUDFRONT_DOMAIN}/static/
MEDIA_URL=https://${CLOUDFRONT_DOMAIN}/media/
DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage

# API Keys
OPENAI_API_KEY=${OPENAI_API_KEY:-}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
GITHUB_TOKEN=${GITHUB_TOKEN:-}

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.${AWS_REGION}.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=${SES_SMTP_USER:-}
EMAIL_HOST_PASSWORD=${SES_SMTP_PASSWORD:-}

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSTT_FILTER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Celery
CELERY_BROKER_URL=redis://${REDIS_HOST}:6379/0
CELERY_RESULT_BACKEND=redis://${REDIS_HOST}:6379/0
EOF

# Create logs directory
mkdir -p logs
chmod 755 logs

# Create required directories for static/media files
mkdir -p staticfiles mediafiles
chmod 755 staticfiles mediafiles

# Set proper permissions
chown -R ec2-user:ec2-user /opt/cloudengineered

# Wait for database to be ready
echo "Waiting for database to be ready..."
for i in {1..30}; do
    if psql -h ${DB_HOST} -U ${DB_USER} -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
        echo "Database is ready!"
        break
    fi
    echo "Waiting for database... ($i/30)"
    sleep 10
done

# Create database if it doesn't exist
psql -h ${DB_HOST} -U ${DB_USER} -c "CREATE DATABASE ${DB_NAME};" || echo "Database ${DB_NAME} already exists"

# Build and start application
cd /opt/cloudengineered
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for application to start
echo "Waiting for application to start..."
sleep 30

# Run database migrations
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Load initial data
docker-compose -f docker-compose.prod.yml exec -T web python manage.py setup_initial_data

# Create superuser (optional - requires interactive input)
# docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Configure Nginx
cat > /etc/nginx/sites-available/cloudengineered << EOF
upstream cloudengineered_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name _;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Django application
    location / {
        proxy_pass http://cloudengineered_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Timeout settings
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Health check endpoint
    location /health/ {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable site and remove default
ln -sf /etc/nginx/sites-available/cloudengineered /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t && systemctl reload nginx

# Enable and start Nginx
systemctl enable nginx
systemctl start nginx

# Setup log rotation
cat > /etc/logrotate.d/cloudengineered << EOF
/opt/cloudengineered/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ec2-user ec2-user
    postrotate
        docker-compose -f /opt/cloudengineered/docker-compose.prod.yml exec -T web kill -USR1 \$(cat /tmp/gunicorn.pid 2>/dev/null) 2>/dev/null || true
    endscript
}
EOF

# Setup backup script
cat > /opt/cloudengineered/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/cloudengineered/backups"

mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up database..."
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup media files
echo "Backing up media files..."
aws s3 sync /opt/cloudengineered/mediafiles/ s3://$S3_BUCKET/backups/media/$DATE/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/cloudengineered/backup.sh

# Setup cron job for backups
echo "0 2 * * * /opt/cloudengineered/backup.sh" | crontab -

# Setup monitoring script
cat > /opt/cloudengineered/monitor.sh << 'EOF'
#!/bin/bash
# Basic monitoring script

echo "=== CloudEngineered Health Check ==="
echo "Date: $(date)"

# Check services
echo "Docker containers:"
docker-compose -f /opt/cloudengineered/docker-compose.prod.yml ps

echo -e "\nApplication health:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost/health/

echo -e "\nDisk usage:"
df -h /opt/cloudengineered

echo -e "\nMemory usage:"
free -h

echo -e "\nRecent errors:"
tail -20 /opt/cloudengineered/logs/django.log | grep ERROR || echo "No recent errors"
EOF

chmod +x /opt/cloudengineered/monitor.sh

# Final setup complete
echo "CloudEngineered setup completed successfully!"
echo "Application should be available at: http://${PUBLIC_IP:-127.0.0.1}"
echo ""
echo "To check logs: docker-compose -f /opt/cloudengineered/docker-compose.prod.yml logs -f web"
echo "To restart: docker-compose -f /opt/cloudengineered/docker-compose.prod.yml restart"
echo "To backup: /opt/cloudengineered/backup.sh"
echo "To monitor: /opt/cloudengineered/monitor.sh"