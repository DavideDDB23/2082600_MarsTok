"""
api/src/routers/actuators.py — Actuator proxy

Thin proxy to the simulator's actuator API:
  GET  /api/actuators              → list all actuators + their current state
  POST /api/actuators/{name}       → set actuator state (ON / OFF)
"""
from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..config import settings

router = APIRouter(prefix="/api/actuators", tags=["actuators"])
logger = logging.getLogger(__name__)


class ActuatorCommand(BaseModel):
    state: str  # "ON" | "OFF"


@router.get("/", summary="List all actuators and their current state")
async def list_actuators():
    """Proxy GET /api/actuators to the simulator."""
    url = f"{settings.simulator_base_url}/api/actuators"
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Simulator unreachable: {exc}")


@router.post("/{actuator_name}", summary="Set an actuator state")
async def set_actuator(actuator_name: str, cmd: ActuatorCommand):
    """
    Proxy POST /api/actuators/{actuator_name} to the simulator.
    Body: { "state": "ON" | "OFF" }
    """
    url = f"{settings.simulator_base_url}/api/actuators/{actuator_name}"
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            r = await client.post(url, json={"state": cmd.state})
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Simulator unreachable: {exc}")
