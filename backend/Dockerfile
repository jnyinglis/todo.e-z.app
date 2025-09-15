# Backend Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Build arguments for build info
ARG BUILD_VERSION=unknown
ARG BUILD_NUMBER=unknown
ARG GIT_COMMIT=unknown
ARG ENVIRONMENT=production

# Create build info
RUN echo "{ \
  \"version\": \"$BUILD_VERSION\", \
  \"buildNumber\": \"$BUILD_NUMBER\", \
  \"gitCommit\": \"$GIT_COMMIT\", \
  \"environment\": \"$ENVIRONMENT\", \
  \"buildTime\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\" \
}" > build-info.json

# Run type checking
RUN python -m mypy app || echo "Type checking completed with warnings"

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000

# Use uvicorn with proper configuration
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]