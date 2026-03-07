"""
api/src/routers/alerts.py — Alert history

  GET    /api/alerts          → paginated list, newest first
  GET    /api/alerts/{id}     → single alert
  DELETE /api/alerts/{id}     → remove an alert
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Alert

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


def _alert_to_dict(a: Alert) -> dict:
    return {
        "id":              a.id,
        "rule_id":         a.rule_id,
        "rule_name":       a.rule_name,
        "triggered_event": a.triggered_event,
        "triggered_at":    a.triggered_at.isoformat(),
    }


@router.get("/", summary="List alerts (newest first)")
async def list_alerts(
    offset:    int            = Query(0,    ge=0,        description="Pagination offset"),
    limit:     int            = Query(50,   ge=1, le=200, description="Page size"),
    rule_id:   Optional[str]  = Query(None, description="Filter by rule_id"),
    source_id: Optional[str]  = Query(None, description="Filter by triggered_event source_id"),
    db: AsyncSession = Depends(get_db),
):
    """
    Paginated alert list, newest first.
    Supports optional filters: ``?rule_id=`` and ``?source_id=``.
    """
    q = select(Alert)
    if rule_id:
        q = q.where(Alert.rule_id == rule_id)
    if source_id:
        # JSONB containment: triggered_event->>'source_id' = source_id
        q = q.where(Alert.triggered_event["source_id"].astext == source_id)

    count_q = select(func.count()).select_from(q.subquery())
    total_result = await db.execute(count_q)
    total: int   = total_result.scalar_one()

    result = await db.execute(
        q.order_by(Alert.triggered_at.desc()).offset(offset).limit(limit)
    )
    items = [_alert_to_dict(a) for a in result.scalars().all()]
    return {"total": total, "offset": offset, "limit": limit, "items": items}


@router.get("/{alert_id}", summary="Get a single alert")
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    alert = await db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _alert_to_dict(alert)


@router.delete("/{alert_id}", status_code=204, summary="Delete an alert")
async def delete_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    alert = await db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    await db.delete(alert)
    await db.commit()
