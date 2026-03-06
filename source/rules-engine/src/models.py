"""
rules-engine/src/models.py — SQLAlchemy ORM models for Rules and Alerts.

Both tables store the structured parts of their schemas as native JSONB columns
so the API can query and filter them without extra joins.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Rule(Base):
    """
    Persistent rule definition.

    Columns
    -------
    id          : UUID primary key
    name        : human-readable rule name
    enabled     : whether the rule is active
    condition   : JSONB  { source_id, metric, operator, threshold }
    action      : JSONB  { actuator_name, state }
    created_at  : creation timestamp (UTC)
    updated_at  : last-modified timestamp (UTC)
    """
    __tablename__ = "rules"

    id:         Mapped[str]      = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name:       Mapped[str]      = mapped_column(String(255), nullable=False)
    enabled:    Mapped[bool]     = mapped_column(Boolean, nullable=False, default=True)
    condition:  Mapped[dict]     = mapped_column(JSONB, nullable=False)
    action:     Mapped[dict]     = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)


class Alert(Base):
    """
    Immutable alert record created each time a rule fires.

    Columns
    -------
    id              : UUID primary key
    rule_id         : FK-like reference to the triggering rule (no FK constraint for simplicity)
    rule_name       : denormalised rule name at trigger time
    triggered_event : JSONB snapshot of the InternalEvent that triggered the rule
    triggered_at    : alert creation timestamp (UTC)
    """
    __tablename__ = "alerts"

    id:              Mapped[str]      = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id:         Mapped[str]      = mapped_column(String, nullable=False, index=True)
    rule_name:       Mapped[str]      = mapped_column(String(255), nullable=False)
    triggered_event: Mapped[dict]     = mapped_column(JSONB, nullable=False)
    triggered_at:    Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
