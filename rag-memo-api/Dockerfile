# Use a base image that might have better connectivity
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NLTK_DATA=/app/nltk_data \
    TRANSFORMERS_CACHE=/app/transformers_cache \
    HF_HOME=/app/huggingface

# Copy requirements first for better caching
COPY rag-memo-api/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY rag-memo-api/ .

# Create app user and directories
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/uploads /app/logs /app/nltk_data /app/transformers_cache /app/huggingface && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

# Switch to app user
USER appuser

# Pre-download NLTK data to avoid permission issues
RUN python -c "import nltk; nltk.download('stopwords', download_dir='/app/nltk_data'); nltk.download('punkt', download_dir='/app/nltk_data')"

# Health check (using Python)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Start API server
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 