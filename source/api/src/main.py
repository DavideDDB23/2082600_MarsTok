"""
api/src/main.py — FastAPI application factory.

Mounts all routers and manages shared resources (Redis, DB engine)
via lifespan context manager.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import engine
from .routers import actuators, alerts, rules, state, stream

logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    logger.info("API starting up ...")
    app.state.redis = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    logger.info("Redis client connected: %s", settings.redis_url)
    yield
    # ── Shutdown ─────────────────────────────────────────────────────────────
    await app.state.redis.aclose()
    await engine.dispose()
    logger.info("API shut down cleanly.")


app = FastAPI(
    title="Mars Operations API",
    version="1.0.0",
    description="Event-driven IoT automation platform for the Mars habitat.",
    lifespan=lifespan,
)

# ── CORS (allow the Vite dev server and the nginx-served frontend) ────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(state.router)
app.include_router(actuators.router)
app.include_router(rules.router)
app.include_router(alerts.router)
app.include_router(stream.router)


@app.get("/api/health", tags=["health"])
async def health():
    return {"status": "ok"}
