# Use the official Python image
FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ARG CACHE_BUSTER=1
 
# Install system dependencies required for Pillow and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libtiff5-dev \
    libopenjp2-7-dev \
    libwebp-dev \
    tk-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install supervisor
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

# Create a non-root user called appuser
RUN useradd -m -d /home/appuser -s /bin/bash appuser
 
# Set working directory
WORKDIR /app

# Copy application code and supervisor config
COPY common/ ./
COPY common/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy script and set executable permission
COPY common/scripts.sh scripts.sh
RUN chmod +x /app/scripts.sh

# Create necessary directories inside the container
RUN mkdir -p /app/logs/redis

# Copy requirements and install dependencies
COPY common/requirements.txt .
RUN pip install -r requirements.txt

# Copy the configs folder even if it's in .gitignore
COPY common/configs/ /app/configs/

# Expose the necessary port
EXPOSE 8000
