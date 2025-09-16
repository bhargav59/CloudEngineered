FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/base.txt /app/requirements/base.txt
COPY requirements/production.txt /app/requirements/production.txt
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy project
COPY . /app/

# Create static files directory
RUN mkdir -p /app/staticfiles

# Create non-root user
RUN adduser --disabled-password --gecos '' cloudengineered
RUN chown -R cloudengineered:cloudengineered /app
USER cloudengineered

# Expose port (Railway provides $PORT at runtime)
EXPOSE 8000

# Ensure start script is executable and use it as the container command
RUN chmod +x /app/start.sh

# Start via start.sh which runs migrations, collectstatic, then gunicorn bound to $PORT
CMD ["./start.sh"]
