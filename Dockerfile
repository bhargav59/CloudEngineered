FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Copy only requirements first for better caching
COPY requirements/railway.txt ./requirements/railway.txt

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir -r requirements/railway.txt \
    && find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete \
    && find /usr/local/lib/python3.11/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Copy only necessary project files
COPY manage.py start.sh ./
COPY config/ ./config/
COPY apps/ ./apps/
COPY templates/ ./templates/
COPY static/ ./static/

# Create directories and set permissions
RUN mkdir -p /app/staticfiles /app/media \
    && chmod +x /app/start.sh \
    && adduser --disabled-password --gecos '' --uid 1000 cloudengineered \
    && chown -R cloudengineered:cloudengineered /app

# Switch to non-root user
USER cloudengineered

# Expose port
EXPOSE 8000

# Start via optimized start script
CMD ["./start.sh"]
