# backend/Dockerfile

# === Build Stage ===
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/opt/venv -r requirements.txt

# === Production Stage ===
FROM python:3.11-slim

# Install runtime dependencies (Tesseract for OCR, gosu for user switching)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    gosu \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /usr/src/app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy application code
COPY --chown=appuser:appgroup backend/ ./backend/
COPY --chown=appuser:appgroup data/ ./data/

# Create temp directory with proper permissions
RUN mkdir -p /tmp/campaign_analysis && chown appuser:appgroup /tmp/campaign_analysis

# Switch to non-root user
USER appuser

# Expose Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run Flask application
ENV FLASK_APP=backend.app
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
