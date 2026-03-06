"""
collector/src/main.py — Entry point for the Collector microservice.

Starts two concurrent ingestion pipelines:
  1. REST polling loop  — polls all 8 REST sensors every POLL_INTERVAL_SECONDS
  2. SSE subscriber     — maintains persistent connections to all 7 telemetry topics

Both pipelines publish normalised InternalEvent objects to the RabbitMQ
`mars.events` fanout exchange.
"""
from __future__ import annotations

import asyncio
import logging
import sys

from .config import settings
from .publisher import connect_rabbitmq
from .rest_poller import polling_loop
from .sse_subscriber import subscribe_all_topics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("collector")


async def main() -> None:
    logger.info("Mars Collector starting up ...")
    logger.info(
        "Config: simulator=%s  rabbitmq=%s  exchange=%s  poll=%ds",
        settings.simulator_base_url,
        settings.rabbitmq_url,
        settings.rabbitmq_exchange,
        settings.poll_interval_seconds,
    )

    _conn, _channel, exchange = await connect_rabbitmq(
        settings.rabbitmq_url,
        settings.rabbitmq_exchange,
    )

    logger.info("Launching ingestion tasks (REST polling + SSE subscriptions) ...")
    await asyncio.gather(
        polling_loop(exchange, settings),
        subscribe_all_topics(exchange, settings),
    )


if __name__ == "__main__":
    asyncio.run(main())
