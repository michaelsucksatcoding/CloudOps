"""Telemetry event database model."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from services.api.app.database import Base


class TelemetryEntity(Base):
    """Persisted telemetry event received by the platform."""

    __tablename__ = "telemetry_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    service: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    endpoint: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    latency_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    cpu_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    memory_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    request_rate: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    queue_depth: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    deployment_version: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    instance_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    environment: Mapped[str | None] = mapped_column(
        String(32),
        default="dev",
        nullable=True,
    )
    tenant_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    region: Mapped[str | None] = mapped_column(
        String(32),
        default="us-east-1",
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
