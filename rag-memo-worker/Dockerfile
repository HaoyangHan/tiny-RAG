# Simple single-stage build
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV DRAMATIQ_BROKER=redis://redis:6379

# Copy requirements first for better caching
COPY rag-memo-worker/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY rag-memo-worker/ .

# Create uploads directory
RUN mkdir -p uploads

# Start the worker
CMD ["dramatiq", "workers.tasks"] 