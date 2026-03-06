"""
rules-engine/src/evaluator.py — Rule evaluation engine.

For every incoming InternalEvent:
  1. Load all enabled rules from PostgreSQL.
  2. Find any rule whose condition matches the event.
  3. For each match: persist an Alert, publish it to Redis, and fire the actuator.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas import AlertSchema, InternalEvent, RuleCondition
from .actuator_client import trigger_actuator
from .config import settings
from .models import Alert, Rule
from .state_store import StateStore

logger = logging.getLogger(__name__)

# Supported operators
_OPS = {
    "gt":  lambda v, t: v >  t,
    "lt":  lambda v, t: v <  t,
    "gte": lambda v, t: v >= t,
    "lte": lambda v, t: v <= t,
    "eq":  lambda v, t: v == t,
    "neq": lambda v, t: v != t,
}


def _condition_matches(condition: dict, event: InternalEvent) -> bool:
    """
    Return True if the event satisfies the rule condition.

    The condition must match on source_id, metric name, operator, and threshold.
    """
    if condition.get("source_id") != event.source_id:
        return False

    metric_name = condition.get("metric")
    threshold   = condition.get("threshold")
    operator    = condition.get("operator")

    # Find the metric in the event
    value: float | None = None
    for m in event.metrics:
        if m.name == metric_name:
            value = m.value
            break

    if value is None:
        return False  # metric not present in this event

    op_fn = _OPS.get(operator)
    if op_fn is None:
        logger.warning("Unknown operator '%s' in rule condition.", operator)
        return False

    return op_fn(value, threshold)


async def evaluate_event(
    event: InternalEvent,
    session: AsyncSession,
    store: StateStore,
) -> None:
    """
    Evaluate an InternalEvent against all enabled rules.
    Fires side effects (alert persist + Redis publish + actuator call) for matches.
    """
    # Load enabled rules
    result = await session.execute(select(Rule).where(Rule.enabled == True))  # noqa: E712
    rules: list[Rule] = result.scalars().all()

    for rule in rules:
        if not _condition_matches(rule.condition, event):
            continue

        logger.info(
            "Rule '%s' triggered by source_id='%s' metric='%s'",
            rule.name, event.source_id, rule.condition.get("metric"),
        )

        # ── Persist alert ─────────────────────────────────────────────────
        alert_id  = str(uuid.uuid4())
        triggered_at = datetime.now(timezone.utc)
        db_alert = Alert(
            id=alert_id,
            rule_id=rule.id,
            rule_name=rule.name,
            triggered_event=event.model_dump(mode="json"),
            triggered_at=triggered_at,
        )
        session.add(db_alert)
        await session.commit()

        # ── Build AlertSchema for pub/sub ─────────────────────────────────
        alert_schema = AlertSchema(
            id=alert_id,
            rule_id=rule.id,
            rule_name=rule.name,
            triggered_event=event.model_dump(mode="json"),
            triggered_at=triggered_at.isoformat(),
        )
        await store.publish_alert(alert_schema)

        # ── Fire actuator (best-effort) ───────────────────────────────────
        action = rule.action
        try:
            await trigger_actuator(
                settings.simulator_base_url,
                action["actuator_name"],
                action["state"],
            )
        except Exception as exc:
            logger.error(
                "Failed to trigger actuator '%s': %s",
                action.get("actuator_name"), exc,
            )
