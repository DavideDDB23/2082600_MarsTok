"""
api/src/routers/state.py — GET /api/state

Returns the latest known InternalEvent for every sensor/topic from Redis.
"""
from __future__ import annotations

import json

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..redis_client import get_redis

router = APIRouter(prefix="/api/state", tags=["state"])

_STATE_KEY_PREFIX = "state:"


@router.get("/", summary="Get latest state for all sources")
async def get_all_states(redis: aioredis.Redis = Depends(get_redis)):
    """
    Return a dict mapping source_id → InternalEvent (latest known reading).
    Sources that have never published are absent.
    """
    keys: list[str] = await redis.keys(f"{_STATE_KEY_PREFIX}*")
    if not keys:
        return {}

    values = await redis.mget(*keys)
    prefix_len = len(_STATE_KEY_PREFIX)
    result = {
        k[prefix_len:]: json.loads(v)
        for k, v in zip(keys, values)
        if v is not None
    }
    return result


@router.get("/{source_id}", summary="Get latest state for a specific source")
async def get_source_state(
    source_id: str,
    redis: aioredis.Redis = Depends(get_redis),
):
    """Return the latest InternalEvent for the given source_id, or 404."""
    raw = await redis.get(f"{_STATE_KEY_PREFIX}{source_id}")
    if raw is None:
        return JSONResponse(
            status_code=404,
            content={"detail": f"No state found for source_id='{source_id}'"},
        )
    return json.loads(raw)
