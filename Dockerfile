# Production Dockerfile for WörtWeaver
FROM python:3.11-slim

# Prevent Python from writing .pyc files & buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    HOME=/home/appuser

# Install system dependencies (including ca-certificates for downloading translation packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and set work directory
RUN useradd -m -u 10001 appuser
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure appuser owns the application directory and home directory
RUN chown -R appuser:appuser /app /home/appuser

# Switch to non-root user
USER appuser

# Pre-download and install default German -> English translation package during build
RUN python -c "from app import setup_translation_model; setup_translation_model()"

# Expose container port
EXPOSE 5000

# Healthcheck to monitor server availability
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Start server using Gunicorn production config
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
