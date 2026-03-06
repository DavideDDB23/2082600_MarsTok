"""
api/src/redis_client.py — Singleton async Redis client with FastAPI dependency.

The client is created once at startup (stored on app.state by main.py lifespan)
and retrieved via FastAPI's Depends() mechanism.

Usage:
    from .redis_client import get_redis

    @router.get("/foo")
    async def foo(redis: aioredis.Redis = Depends(get_redis)):
        ...
"""
from __future__ import annotations

import redis.asyncio as aioredis
from fastapi import Request


def get_redis(request: Request) -> aioredis.Redis:
    """
    FastAPI dependency that returns the shared Redis client from ``app.state``.

    The client is initialised in ``main.py``'s lifespan handler and stored as
    ``app.state.redis``.
    """
    return request.app.state.redis
