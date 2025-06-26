# Build stage
FROM python:3.11-bullseye AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy core library source
COPY rag-memo-core-lib/src/rag_memo_core_lib /app/rag_memo_core_lib

# Copy requirements and install API dependencies
COPY rag-memo-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY rag-memo-api/ .

# Production stage
FROM python:3.11-slim-bullseye

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy core library
COPY --from=builder /app/rag_memo_core_lib /app/rag_memo_core_lib

# Copy application code
COPY rag-memo-api/ .

# Create uploads directory
RUN mkdir -p uploads

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 