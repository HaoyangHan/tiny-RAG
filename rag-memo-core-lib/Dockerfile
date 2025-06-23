# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy library code
COPY . .

# Install the package in development mode
RUN pip install -e .

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for runtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy library code
COPY . .

# Install the package
RUN pip install -e .

# Create app user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set working directory for library usage
WORKDIR /app

# Default command for worker
CMD ["python", "-m", "rag_memo_core_lib.workers.main"] 