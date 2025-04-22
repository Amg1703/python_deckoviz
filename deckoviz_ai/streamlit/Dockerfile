FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY deckoviz_ai/streamlit/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the Streamlit port
EXPOSE 8501

# Create a non-root user
RUN useradd -m -d /home/appuser -s /bin/bash appuser
USER appuser

# Run Streamlit
CMD ["streamlit", "run", "deckoviz_ai/streamlit/app.py", "--server.address", "0.0.0.0"]
