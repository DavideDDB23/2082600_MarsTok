"""
rules-engine/src/state_store.py — Redis state cache.

Responsibilities:
  1. Store the latest InternalEvent per source_id under `state:{source_id}`
  2. Publish the event to the `mars.events` Redis pub/sub channel
     (so the API's SSE stream can forward it to the browser)
  3. Publish alert JSON to the `mars.alerts` channel when a rule fires
"""
from __future__ import annotations

import logging

import redis.asyncio as aioredis

from shared.schemas import AlertSchema, InternalEvent

logger = logging.getLogger(__name__)

_STATE_KEY_PREFIX = "state:"
_EVENTS_CHANNEL   = "mars.events"
_ALERTS_CHANNEL   = "mars.alerts"


class StateStore:
    def __init__(self, redis_url: str, state_ttl: int = 3600) -> None:
        self._client: aioredis.Redis = aioredis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        self._ttl = state_ttl

    # ── Latest state ────────────────────────────────────────────────────────

    async def set_state(self, event: InternalEvent) -> None:
        """Cache the latest InternalEvent JSON under `state:{source_id}`."""
        key  = f"{_STATE_KEY_PREFIX}{event.source_id}"
        data = event.model_dump_json()
        await self._client.set(key, data, ex=self._ttl)
        logger.debug("State cached: %s", key)

    async def get_state(self, source_id: str) -> str | None:
        """Return the raw JSON string for a given source_id, or None."""
        return await self._client.get(f"{_STATE_KEY_PREFIX}{source_id}")

    async def get_all_states(self) -> dict[str, str]:
        """Return all cached state values keyed by source_id."""
        keys: list[str] = await self._client.keys(f"{_STATE_KEY_PREFIX}*")
        if not keys:
            return {}
        values = await self._client.mget(*keys)
        prefix_len = len(_STATE_KEY_PREFIX)
        return {
            k[prefix_len:]: v
            for k, v in zip(keys, values)
            if v is not None
        }

    # ── Pub/Sub publishing ───────────────────────────────────────────────────

    async def publish_event(self, event: InternalEvent) -> None:
        """Publish an InternalEvent JSON to the `mars.events` channel."""
        await self._client.publish(_EVENTS_CHANNEL, event.model_dump_json())

    async def publish_alert(self, alert: AlertSchema) -> None:
        """Publish an AlertSchema JSON to the `mars.alerts` channel."""
        await self._client.publish(_ALERTS_CHANNEL, alert.model_dump_json())

    async def close(self) -> None:
        await self._client.aclose()
