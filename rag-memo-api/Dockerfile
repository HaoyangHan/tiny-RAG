# Build stage
FROM --platform=$BUILDPLATFORM python:3.11-slim-bullseye as builder

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    # Pre-download Spacy model to avoid download during runtime
    SPACY_MODEL=en_core_web_sm \
    # Use Baidu mirror for faster package downloads
    PIP_INDEX_URL=https://mirror.baidu.com/pypi/simple

# Install build dependencies with retry mechanism and minimal packages
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    for i in $(seq 1 3); do \
        apt-get update -y && \
        apt-get install -y --no-install-recommends \
    build-essential \
            curl \
            python3-dev \
            git \
            && break || \
        sleep 5; \
    done

# Upgrade pip and install wheel with retry mechanism
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install --upgrade pip setuptools wheel

# Install dependencies in groups to better utilize caching
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    # Core dependencies first
    grep "^fastapi\|^uvicorn\|^python-multipart\|^pydantic" requirements.txt > core-requirements.txt && \
    pip install -r core-requirements.txt && \
    # Then ML/NLP dependencies
    grep "^numpy\|^scikit-learn\|^nltk\|^spacy\|^langchain" requirements.txt > ml-requirements.txt && \
    pip install -r ml-requirements.txt && \
    # Finally all other dependencies
    pip install -r requirements.txt && \
    # Install Spacy model
    python -m spacy download ${SPACY_MODEL}

# Copy application code
COPY . .

# Production stage
FROM --platform=$TARGETPLATFORM python:3.11-slim-bullseye

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1

# Install runtime dependencies with retry mechanism
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    for i in $(seq 1 3); do \
        apt-get update -y && \
        apt-get install -y --no-install-recommends \
            curl \
            && break || \
        sleep 5; \
    done

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/share/spacy /usr/local/share/spacy

# Copy application code
COPY . .

# Create app user and directories with proper permissions
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/uploads /app/logs && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start API server with optimized settings
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--limit-concurrency", "1000", "--backlog", "2048"] 