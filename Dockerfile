FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    make \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first for better layer caching
COPY requirements/ ./requirements/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy project files
COPY manage.py start.sh ./
COPY config/ ./config/
COPY apps/ ./apps/
COPY templates/ ./templates/
COPY static/ ./static/

# Create directories
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Make start script executable
RUN chmod +x /app/start.sh

# Create non-root user and set permissions
RUN adduser --disabled-password --gecos '' --uid 1000 cloudengineered \
    && chown -R cloudengineered:cloudengineered /app

# Switch to non-root user
USER cloudengineered

# Expose port (Railway sets $PORT dynamically)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health/', timeout=5)" || exit 1

# Start application
CMD ["./start.sh"]
