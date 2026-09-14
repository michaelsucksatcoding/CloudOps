"""Initial Phase 1 schema for services and telemetry_events

Revision ID: 0001_initial_phase1
Revises:
Create Date: 2026-09-03 13:48:00

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_phase1"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create services table
    op.create_table(
        "services",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column(
            "environment", sa.String(length=32), nullable=False, server_default="dev"
        ),
        sa.Column(
            "current_health_score", sa.Float(), nullable=False, server_default="1.0"
        ),
        sa.Column(
            "status", sa.String(length=32), nullable=False, server_default="healthy"
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create telemetry_events table
    op.create_table(
        "telemetry_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("service", sa.String(length=64), nullable=False),
        sa.Column("endpoint", sa.String(length=255), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("cpu_percent", sa.Float(), nullable=False),
        sa.Column("memory_percent", sa.Float(), nullable=False),
        sa.Column("request_rate", sa.Float(), nullable=True),
        sa.Column("queue_depth", sa.Integer(), nullable=True),
        sa.Column("deployment_version", sa.String(length=64), nullable=True),
        sa.Column("instance_id", sa.String(length=64), nullable=True),
        sa.Column(
            "environment", sa.String(length=32), nullable=True, server_default="dev"
        ),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column(
            "region", sa.String(length=32), nullable=True, server_default="us-east-1"
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_telemetry_events_timestamp"),
        "telemetry_events",
        ["timestamp"],
        unique=False,
    )
    op.create_index(
        op.f("ix_telemetry_events_service"),
        "telemetry_events",
        ["service"],
        unique=False,
    )
    op.create_index(
        op.f("ix_telemetry_events_status_code"),
        "telemetry_events",
        ["status_code"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_telemetry_events_status_code"), table_name="telemetry_events"
    )
    op.drop_index(op.f("ix_telemetry_events_service"), table_name="telemetry_events")
    op.drop_index(op.f("ix_telemetry_events_timestamp"), table_name="telemetry_events")
    op.drop_table("telemetry_events")
    op.drop_table("services")
