# ==========================================
# Stage 1: Base Builder Stage
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY services/ ./services/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# ==========================================
# Stage 2: Shared Production Runtime Base
# ==========================================
FROM python:3.12-slim AS base-runner

WORKDIR /app

# Run as non-root user (UID 1000) for security compliance
RUN useradd -m -u 1000 appuser && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY services/ ./services/
COPY pyproject.toml README.md ./

USER appuser

# ==========================================
# Stage 3: FastAPI API Service Target
# ==========================================
FROM base-runner AS api

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

CMD ["uvicorn", "services.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ==========================================
# Stage 4: ML Service Target
# ==========================================
FROM base-runner AS ml

CMD ["python", "-m", "services.ml.evaluate"]

# ==========================================
# Stage 5: Event Processor Worker Target
# ==========================================
FROM base-runner AS event-processor

CMD ["python", "-m", "services.event_processor.handler"]

# Default stage when no target is specified
FROM api AS final
