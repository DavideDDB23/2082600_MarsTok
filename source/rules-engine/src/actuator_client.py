"""
rules-engine/src/actuator_client.py — HTTP client for the simulator's actuator API.

Wraps POST /api/actuators/{actuator_name} with the body {"state": "ON"|"OFF"}.
"""
from __future__ import annotations

import logging

import httpx

logger = logging.getLogger(__name__)

_TIMEOUT = 5.0  # seconds


async def trigger_actuator(
    base_url: str,
    actuator_name: str,
    state: str,
) -> dict:
    """
    Call POST /api/actuators/{actuator_name} on the simulator.

    Parameters
    ----------
    base_url       : simulator base URL, e.g. ``http://simulator:8080``
    actuator_name  : the actuator identifier
    state          : ``"ON"`` or ``"OFF"``

    Returns
    -------
    The parsed JSON response from the simulator.

    Raises
    ------
    httpx.HTTPError on any transport or HTTP-status error.
    """
    url = f"{base_url}/api/actuators/{actuator_name}"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.post(url, json={"state": state})
        response.raise_for_status()
        result = response.json()
        logger.info(
            "Actuator '%s' set to %s → %s",
            actuator_name, state, result,
        )
        return result
