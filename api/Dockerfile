# Use the official Python image
FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ARG CACHE_BUSTER=1

# Create a non-root user called appuser
RUN useradd -m -d /home/appuser -s /bin/bash appuser
 
# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY api/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy API code and deckoviz_ai package
COPY api/ ./
COPY deckoviz_ai/ ./deckoviz_ai/

# Expose the necessary port
EXPOSE 8080
