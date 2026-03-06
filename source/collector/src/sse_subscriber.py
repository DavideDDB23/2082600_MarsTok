"""
collector/src/sse_subscriber.py — Persistent SSE subscriptions for telemetry topics.

One coroutine per topic maintains a long-lived SSE connection to the simulator.
On disconnect it reconnects automatically after a short delay.

URL pattern: GET /api/telemetry/stream/<topic/path/with/slashes>
The simulator route is expected to use a path wildcard (FastAPI `{topic:path}`).
"""
from __future__ import annotations

import asyncio
import json
import logging

import httpx

from .config import TELEMETRY_TOPICS, Settings
from .normalizer import normalize
from .publisher import publish_event

logger = logging.getLogger(__name__)

_RECONNECT_DELAY = 3  # seconds on connection drop


async def _subscribe_one(topic: str, exchange, settings: Settings) -> None:
    """
    Maintain a persistent SSE connection to a single telemetry topic.
    Reconnects automatically if the connection is lost.

    The topic path is appended as-is to the URL (forward slashes preserved)
    because the simulator captures it as a path wildcard parameter.
    """
    url = f"{settings.simulator_base_url}/api/telemetry/stream/{topic}"

    while True:
        try:
            logger.info("Subscribing to SSE topic: %s", topic)
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line.startswith("data:"):
                            continue
                        payload_str = line[len("data:"):].strip()
                        if not payload_str:
                            continue
                        try:
                            raw = json.loads(payload_str)
                            # The payload carries the topic name in its "topic" field;
                            # fall back to the subscribed topic path if absent.
                            source_id = raw.get("topic", topic)
                            event     = normalize(raw, source_id)
                            await publish_event(exchange, event)
                        except Exception as exc:
                            logger.warning(
                                "Error processing SSE message from '%s': %s",
                                topic, exc,
                            )
        except Exception as exc:
            logger.warning(
                "SSE connection dropped for '%s' (%s). Reconnecting in %ds ...",
                topic, exc, _RECONNECT_DELAY,
            )
            await asyncio.sleep(_RECONNECT_DELAY)


async def subscribe_all_topics(exchange, settings: Settings) -> None:
    """Launch one persistent SSE subscription per telemetry topic (all concurrent)."""
    logger.info("Starting SSE subscriptions for %d topics ...", len(TELEMETRY_TOPICS))
    await asyncio.gather(
        *[_subscribe_one(t, exchange, settings) for t in TELEMETRY_TOPICS],
        return_exceptions=True,
    )
