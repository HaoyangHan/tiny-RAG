# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy library code
COPY . .

# Build the package
RUN poetry build

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy built package from builder
COPY --from=builder /app/dist/*.whl ./

# Install the package
RUN pip install *.whl && rm *.whl

# Set working directory for library usage
WORKDIR /workspace

CMD ["python3"] 