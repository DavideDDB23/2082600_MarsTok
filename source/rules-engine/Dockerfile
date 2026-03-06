# =============================================================================
# rules-engine/Dockerfile
# Build context: source/   (set in docker-compose.yml)
# =============================================================================
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Shared models
COPY shared/ ./shared/

# Python deps
COPY rules-engine/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Service source (includes alembic/ directory)
COPY rules-engine/src/    ./src/
COPY rules-engine/alembic/ ./alembic/
COPY rules-engine/alembic.ini ./alembic.ini

# Run Alembic migrations, then start the consumer
CMD ["sh", "-c", "alembic upgrade head && python -m src.main"]
