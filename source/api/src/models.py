"""
api/src/models.py — SQLAlchemy ORM models (mirrors rules-engine/src/models.py).

Defined independently here so the API Docker image does not depend on the
rules-engine service's source tree.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Rule(Base):
    __tablename__ = "rules"

    id:         Mapped[str]      = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name:       Mapped[str]      = mapped_column(String(255), nullable=False)
    enabled:    Mapped[bool]     = mapped_column(Boolean, nullable=False, default=True)
    condition:  Mapped[dict]     = mapped_column(JSONB, nullable=False)
    action:     Mapped[dict]     = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)


class Alert(Base):
    __tablename__ = "alerts"

    id:              Mapped[str]      = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id:         Mapped[str]      = mapped_column(String, nullable=False, index=True)
    rule_name:       Mapped[str]      = mapped_column(String(255), nullable=False)
    triggered_event: Mapped[dict]     = mapped_column(JSONB, nullable=False)
    triggered_at:    Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
