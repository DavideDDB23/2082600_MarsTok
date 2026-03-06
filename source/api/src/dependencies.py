"""
api/src/dependencies.py — Shared FastAPI dependencies.
Re-exports from redis_client for backward compatibility.
"""
from .redis_client import get_redis  # noqa: F401  (public re-export)
