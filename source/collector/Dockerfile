# =============================================================================
# collector/Dockerfile
# Build context: source/   (set in docker-compose.yml)
# =============================================================================
FROM python:3.12-slim

WORKDIR /app

# System deps (httpx needs no extras on slim, but keep curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy shared Pydantic models first (Docker layer cache friendly)
COPY shared/ ./shared/

# Install Python deps
COPY collector/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy service source
COPY collector/src/ ./src/

# Entry point
CMD ["python", "-m", "src.main"]
