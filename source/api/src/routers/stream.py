"""
api/src/routers/stream.py — Server-Sent Events (SSE) endpoints

  GET /api/stream/events  → live InternalEvent stream  (Redis channel: mars.events)
  GET /api/stream/alerts  → live Alert stream           (Redis channel: mars.alerts)

Uses sse-starlette for clean SSE handling with proper disconnect detection.
Each request gets its own Redis pub/sub connection that is closed on disconnect.
"""
from __future__ import annotations

import asyncio
import logging

import redis.asyncio as aioredis
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from ..config import settings

router = APIRouter(prefix="/api/stream", tags=["stream"])
logger = logging.getLogger(__name__)

_EVENTS_CHANNEL = "mars.events"
_ALERTS_CHANNEL = "mars.alerts"
_KEEPALIVE_SECS = 15  # send a comment every N seconds to keep the connection alive


async def _redis_channel_generator(channel: str):
    """
    Async generator that subscribes to a Redis pub/sub channel and
    yields SSE-formatted dicts until the client disconnects.
    """
    redis: aioredis.Redis = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    pubsub = redis.pubsub()
    try:
        await pubsub.subscribe(channel)
        logger.info("SSE client subscribed to Redis channel '%s'", channel)

        while True:
            try:
                message = await asyncio.wait_for(
                    pubsub.get_message(ignore_subscribe_messages=True),
                    timeout=_KEEPALIVE_SECS,
                )
            except asyncio.TimeoutError:
                # Send a keepalive comment so the browser doesn't time out
                yield {"comment": "keepalive"}
                continue

            if message is None:
                await asyncio.sleep(0.05)
                continue

            if message["type"] == "message":
                yield {"data": message["data"]}

    except asyncio.CancelledError:
        logger.info("SSE client disconnected from channel '%s'", channel)
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
        await redis.aclose()


async def _combined_generator():
    """
    Mux both mars.events and mars.alerts into a single SSE stream.

    Each message is emitted with a named event type so the client can
    demultiplex with addEventListener():
      - ``event: sensor_update``  for InternalEvent messages
      - ``event: alert``          for AlertSchema messages
    """
    redis: aioredis.Redis = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    pubsub = redis.pubsub()
    try:
        await pubsub.subscribe(_EVENTS_CHANNEL, _ALERTS_CHANNEL)

        while True:
            try:
                message = await asyncio.wait_for(
                    pubsub.get_message(ignore_subscribe_messages=True),
                    timeout=_KEEPALIVE_SECS,
                )
            except asyncio.TimeoutError:
                yield {"comment": "keepalive"}
                continue

            if message is None:
                await asyncio.sleep(0.05)
                continue

            if message["type"] == "message":
                channel = message["channel"]
                if channel == _EVENTS_CHANNEL:
                    yield {"event": "sensor_update", "data": message["data"]}
                elif channel == _ALERTS_CHANNEL:
                    yield {"event": "alert", "data": message["data"]}

    except asyncio.CancelledError:
        logger.info("SSE client disconnected from combined stream")
    finally:
        await pubsub.unsubscribe(_EVENTS_CHANNEL, _ALERTS_CHANNEL)
        await pubsub.aclose()
        await redis.aclose()


@router.get("", summary="Combined live stream: sensor_update + alert events (SSE)")
async def stream_combined():
    """
    Single SSE endpoint that emits both sensor readings and alerts.

    Named event types:
    - ``sensor_update`` → InternalEvent JSON
    - ``alert``         → AlertSchema JSON

    Browser usage::

        const es = new EventSource("/api/stream");
        es.addEventListener("sensor_update", e => ...);
        es.addEventListener("alert", e => ...);
    """
    return EventSourceResponse(_combined_generator())


@router.get("/events", summary="Live sensor event stream (SSE)")
async def stream_events():
    """
    Subscribe to the ``mars.events`` Redis channel and stream every
    InternalEvent JSON as an SSE ``data:`` line.
    """
    return EventSourceResponse(_redis_channel_generator(_EVENTS_CHANNEL))


@router.get("/alerts", summary="Live alert stream (SSE)")
async def stream_alerts():
    """
    Subscribe to the ``mars.alerts`` Redis channel and stream every
    AlertSchema JSON as an SSE ``data:`` line.
    """
    return EventSourceResponse(_redis_channel_generator(_ALERTS_CHANNEL))
