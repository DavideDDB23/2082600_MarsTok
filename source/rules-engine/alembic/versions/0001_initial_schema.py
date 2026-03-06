"""Initial schema: rules and alerts tables.

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00.000000+00:00
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── rules ──────────────────────────────────────────────────────────────────
    op.create_table(
        "rules",
        sa.Column("id",         sa.String(),                  nullable=False),
        sa.Column("name",       sa.String(255),               nullable=False),
        sa.Column("enabled",    sa.Boolean(),                  nullable=False, server_default="true"),
        sa.Column("condition",  postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("action",     postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),   nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True),   nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── alerts ────────────────────────────────────────────────────────────────
    op.create_table(
        "alerts",
        sa.Column("id",               sa.String(),                  nullable=False),
        sa.Column("rule_id",          sa.String(),                  nullable=False),
        sa.Column("rule_name",        sa.String(255),               nullable=False),
        sa.Column("triggered_event",  postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("triggered_at",     sa.DateTime(timezone=True),   nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_rule_id", "alerts", ["rule_id"])


def downgrade() -> None:
    op.drop_index("ix_alerts_rule_id", table_name="alerts")
    op.drop_table("alerts")
    op.drop_table("rules")
