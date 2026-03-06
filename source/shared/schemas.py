"""
source/shared/schemas.py
========================
Canonical Pydantic v2 data models shared across collector, rules-engine, and api.

Every service that produces or consumes InternalEvent MUST import from here.
Do NOT duplicate these models in individual services.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class SourceType(str, Enum):
    REST_SENSOR     = "rest_sensor"
    TELEMETRY_TOPIC = "telemetry_topic"


class Category(str, Enum):
    ENVIRONMENT  = "environment"
    POWER        = "power"
    LIFE_SUPPORT = "life_support"
    AIRLOCK      = "airlock"
    THERMAL      = "thermal"


# ---------------------------------------------------------------------------
# Core event model
# ---------------------------------------------------------------------------

class MetricReading(BaseModel):
    """A single named measurement inside an InternalEvent."""
    name:  str
    value: float
    unit:  str


class InternalEvent(BaseModel):
    """
    The canonical normalized event that flows through the entire system.

    Published by the Collector to RabbitMQ (mars.events exchange).
    Stored as latest state in Redis under key  state:{source_id}.
    Re-published to Redis pub/sub channels mars.events and mars.alerts.
    """
    event_id:     str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID v4 — unique per event",
    )
    timestamp:    str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 — original capture time from sensor; fallback to ingestion time",
    )
    source_id:    str  = Field(description="Sensor name or topic path")
    source_type:  SourceType
    category:     Category
    metrics:      list[MetricReading] = Field(description="One or more normalised metric readings")
    status:       Optional[str] = Field(
        default=None,
        description="'ok' | 'warning' | null (null for schemas without a status field)",
    )
    raw_schema:   str  = Field(description="Originating simulator schema name, e.g. rest.scalar.v1")
    extra_fields: dict = Field(
        default_factory=dict,
        description="Schema-specific metadata that doesn't fit into metrics (airlock last_state, etc.)",
    )


# ---------------------------------------------------------------------------
# Rule & Alert models (used by rules-engine and api)
# ---------------------------------------------------------------------------

class RuleCondition(BaseModel):
    """IF part of an automation rule."""
    source_id: str   = Field(description="sensor / topic source_id to watch")
    metric:    str   = Field(description="metric name within the InternalEvent.metrics list")
    operator:  str   = Field(description="gt | lt | gte | lte | eq | neq")
    threshold: float = Field(description="Numeric threshold to compare against")


class RuleAction(BaseModel):
    """THEN part of an automation rule."""
    actuator_name: str = Field(description="Actuator name as returned by GET /api/actuators")
    state:         str = Field(description="ON | OFF")


class RuleSchema(BaseModel):
    """Full rule as stored in PostgreSQL and returned by the API."""
    id:         Optional[str] = None
    name:       str
    enabled:    bool          = True
    condition:  RuleCondition
    action:     RuleAction
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AlertSchema(BaseModel):
    """Alert record written by the rules-engine when a rule fires."""
    id:               Optional[str] = None
    rule_id:          str
    rule_name:        Optional[str] = None
    triggered_event:  dict          = Field(description="Serialised InternalEvent snapshot")
    triggered_at:     Optional[str] = None
