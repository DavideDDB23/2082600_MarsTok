"""
api/src/routers/rules.py — CRUD for automation rules

  GET    /api/rules          → list all rules
  POST   /api/rules          → create a rule
  GET    /api/rules/{id}     → get one rule
  PUT    /api/rules/{id}     → update a rule (full replace)
  PATCH  /api/rules/{id}     → toggle enabled
  DELETE /api/rules/{id}     → delete a rule
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas import RuleSchema
from ..db import get_db
from ..models import Rule

router = APIRouter(prefix="/api/rules", tags=["rules"])


def _rule_to_schema(rule: Rule) -> dict:
    return {
        "id":         rule.id,
        "name":       rule.name,
        "enabled":    rule.enabled,
        "condition":  rule.condition,
        "action":     rule.action,
        "created_at": rule.created_at.isoformat(),
        "updated_at": rule.updated_at.isoformat(),
    }


@router.get("/", summary="List all rules")
async def list_rules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Rule).order_by(Rule.created_at))
    return [_rule_to_schema(r) for r in result.scalars().all()]


@router.post("/", status_code=201, summary="Create a rule")
async def create_rule(payload: RuleSchema, db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    rule = Rule(
        id=str(uuid.uuid4()),
        name=payload.name,
        enabled=payload.enabled,
        condition=payload.condition.model_dump(),
        action=payload.action.model_dump(),
        created_at=now,
        updated_at=now,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return _rule_to_schema(rule)


@router.get("/{rule_id}", summary="Get a single rule")
async def get_rule(rule_id: str, db: AsyncSession = Depends(get_db)):
    rule = await db.get(Rule, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return _rule_to_schema(rule)


@router.put("/{rule_id}", summary="Replace a rule")
async def update_rule(
    rule_id: str,
    payload: RuleSchema,
    db: AsyncSession = Depends(get_db),
):
    rule = await db.get(Rule, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.name      = payload.name
    rule.enabled   = payload.enabled
    rule.condition = payload.condition.model_dump()
    rule.action    = payload.action.model_dump()
    rule.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(rule)
    return _rule_to_schema(rule)


from pydantic import BaseModel as _BM


class _EnabledPayload(_BM):
    enabled: bool


@router.patch("/{rule_id}", summary="Set rule enabled state")
async def set_rule_enabled(
    rule_id: str,
    payload: _EnabledPayload,
    db: AsyncSession = Depends(get_db),
):
    """Explicitly set the ``enabled`` field. Body: ``{"enabled": true|false}``."""
    rule = await db.get(Rule, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.enabled    = payload.enabled
    rule.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(rule)
    return _rule_to_schema(rule)


@router.patch("/{rule_id}/toggle", summary="Toggle rule enabled/disabled")
async def toggle_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Flip the ``enabled`` boolean — no request body required."""
    rule = await db.get(Rule, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.enabled    = not rule.enabled
    rule.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(rule)
    return _rule_to_schema(rule)


@router.delete("/{rule_id}", status_code=204, summary="Delete a rule")
async def delete_rule(rule_id: str, db: AsyncSession = Depends(get_db)):
    rule = await db.get(Rule, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    await db.delete(rule)
    await db.commit()
