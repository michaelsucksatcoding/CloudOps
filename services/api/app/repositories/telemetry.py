"""Telemetry repository implementation using SQLAlchemy."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.api.app.models.telemetry import TelemetryEntity
from services.api.app.schemas.telemetry import TelemetryEventCreate


class TelemetryRepository:
    """Repository handling database operations for telemetry events."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, event_in: TelemetryEventCreate) -> TelemetryEntity:
        """Create and persist a new telemetry event."""
        event = TelemetryEntity(
            timestamp=event_in.timestamp,
            service=event_in.service,
            endpoint=event_in.endpoint,
            status_code=event_in.status_code,
            latency_ms=event_in.latency_ms,
            cpu_percent=event_in.cpu_percent,
            memory_percent=event_in.memory_percent,
            request_rate=event_in.request_rate,
            queue_depth=event_in.queue_depth,
            deployment_version=event_in.deployment_version,
            instance_id=event_in.instance_id,
            environment=event_in.environment,
            tenant_id=event_in.tenant_id,
            region=event_in.region,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_by_service(
        self,
        service: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TelemetryEntity]:
        """List telemetry events for a specific service."""
        stmt = (
            select(TelemetryEntity)
            .where(TelemetryEntity.service == service)
            .order_by(TelemetryEntity.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def list_all(self, skip: int = 0, limit: int = 100) -> list[TelemetryEntity]:
        """List all telemetry events ordered by timestamp descending."""
        stmt = (
            select(TelemetryEntity)
            .order_by(TelemetryEntity.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def list_after_created_at(
        self, after: datetime | None = None, limit: int = 100
    ) -> list[TelemetryEntity]:
        """List telemetry events created after a watermark, oldest first.

        ``after=None`` returns the oldest unprocessed rows, which bootstraps the
        watermark on first run. Used by the local event processor to consume
        newly persisted events exactly once without re-processing older rows.
        """
        stmt = select(TelemetryEntity).order_by(TelemetryEntity.created_at.asc())
        if after is not None:
            stmt = stmt.where(TelemetryEntity.created_at > after)
        stmt = stmt.limit(limit)
        return list(self.db.scalars(stmt).all())
