"""
collector/src/rest_poller.py — Concurrent REST sensor polling loop.

Polls all REST sensors every POLL_INTERVAL_SECONDS.  Each poll cycle
fires all sensors concurrently via asyncio.gather, normalises the response,
and publishes the resulting InternalEvent to RabbitMQ.
"""
from __future__ import annotations

import asyncio
import logging

import httpx

from .config import REST_SENSORS, Settings
from .normalizer import normalize
from .publisher import publish_event

logger = logging.getLogger(__name__)


async def _poll_one(
    client: httpx.AsyncClient,
    sensor_name: str,
    exchange,
    settings: Settings,
) -> None:
    """Poll a single REST sensor and publish; silently skip on any error."""
    url = f"{settings.simulator_base_url}/api/sensors/{sensor_name}"
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        raw   = response.json()
        event = normalize(raw, sensor_name)
        await publish_event(exchange, event)
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "HTTP %d polling sensor '%s': %s",
            exc.response.status_code, sensor_name, exc,
        )
    except httpx.RequestError as exc:
        logger.warning("Request error polling sensor '%s': %s", sensor_name, exc)
    except Exception as exc:
        logger.warning("Unexpected error polling sensor '%s': %s", sensor_name, exc)


async def polling_loop(exchange, settings: Settings) -> None:
    """
    Main REST polling loop.  Runs forever — polls all sensors concurrently
    then sleeps for POLL_INTERVAL_SECONDS.
    """
    logger.info(
        "REST polling loop started (interval=%ds, sensors=%d).",
        settings.poll_interval_seconds, len(REST_SENSORS),
    )
    async with httpx.AsyncClient() as client:
        while True:
            await asyncio.gather(
                *[_poll_one(client, s, exchange, settings) for s in REST_SENSORS],
                return_exceptions=True,
            )
            await asyncio.sleep(settings.poll_interval_seconds)
