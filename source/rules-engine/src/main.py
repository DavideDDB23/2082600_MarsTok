"""
rules-engine/src/main.py — Entry point for the Rules Engine microservice.

Start-up sequence:
  1. Alembic migrations run (via Dockerfile CMD before this process).
  2. Redis StateStore is initialised.
  3. RabbitMQ consumer loop is started.
"""
from __future__ import annotations

import asyncio
import logging
import sys

from .config import settings
from .consumer import consume_loop
from .state_store import StateStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("rules-engine")


async def main() -> None:
    logger.info("Mars Rules Engine starting up ...")
    logger.info(
        "Config: rabbitmq=%s  redis=%s  postgres=%s",
        settings.rabbitmq_url,
        settings.redis_url,
        settings.postgres_dsn,
    )

    store = StateStore(settings.redis_url, settings.state_ttl)
    try:
        await consume_loop(store)
    finally:
        await store.close()


if __name__ == "__main__":
    asyncio.run(main())
