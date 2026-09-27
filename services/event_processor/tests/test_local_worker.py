"""Tests for the local PostgreSQL-consuming event processor worker.

These cover the path used by Docker Compose: the API persists telemetry to
PostgreSQL and the long-lived worker consumes those rows exactly once, routing
them into the hot store and the data lake.
"""

from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from services.api.app.database import Base
from services.api.app.repositories.telemetry import TelemetryRepository
from services.api.app.schemas.telemetry import TelemetryEventCreate
from services.event_processor.handler import process_pending_events
from services.event_processor.processor import TelemetryProcessor
from services.event_processor.storage import InMemoryDataLakeStore, InMemoryHotStore


def _event(
    service: str = "payment-api",
    latency_ms: float = 120.0,
    second: int = 0,
) -> TelemetryEventCreate:
    # Distinct timestamps per event: the in-memory hot store is keyed by
    # (service, timestamp), so identical timestamps would collapse into one.
    return TelemetryEventCreate(
        timestamp=datetime(2026, 9, 2, 15, 20, 32 + second, tzinfo=UTC),
        service=service,
        endpoint="/api/payment",
        status_code=200,
        latency_ms=latency_ms,
        cpu_percent=42.0,
        memory_percent=51.0,
    )


@pytest.fixture
def worker_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_process_pending_events_bootstraps_from_empty_watermark(
    worker_session: Session,
) -> None:
    """With no watermark the worker consumes the pending rows exactly once."""
    repo = TelemetryRepository(worker_session)
    repo.create(_event(latency_ms=100.0, second=0))
    repo.create(_event(latency_ms=200.0, second=1))

    hot_store = InMemoryHotStore()
    lake_store = InMemoryDataLakeStore()
    processor = TelemetryProcessor(hot_storage=hot_store, data_lake_storage=lake_store)

    processed, watermark = process_pending_events(worker_session, processor, after=None)

    assert processed == 2
    assert watermark is not None
    assert len(hot_store.get_latest_events("payment-api")) == 2
    assert len(lake_store.get_objects()) == 2

    # A second cycle with the returned watermark must not reprocess anything.
    processed_again, watermark_again = process_pending_events(
        worker_session, processor, after=watermark
    )
    assert processed_again == 0
    assert watermark_again == watermark
    assert len(hot_store.get_latest_events("payment-api")) == 2
    assert len(lake_store.get_objects()) == 2


def test_process_pending_events_picks_up_newly_persisted_rows(
    worker_session: Session,
) -> None:
    """Events persisted after the watermark are picked up by the next cycle."""
    repo = TelemetryRepository(worker_session)
    repo.create(_event(latency_ms=100.0))

    hot_store = InMemoryHotStore()
    lake_store = InMemoryDataLakeStore()
    processor = TelemetryProcessor(hot_storage=hot_store, data_lake_storage=lake_store)

    first, watermark = process_pending_events(worker_session, processor, after=None)
    assert first == 1
    assert watermark is not None

    repo.create(_event(service="auth-service", latency_ms=300.0))

    second, watermark_second = process_pending_events(
        worker_session, processor, after=watermark
    )
    assert second == 1
    assert watermark_second is not None
    assert len(hot_store.get_latest_events("auth-service")) == 1


def test_process_pending_events_does_not_mutate_source_rows(
    worker_session: Session,
) -> None:
    """Processing must not duplicate or alter the durable PostgreSQL rows."""
    repo = TelemetryRepository(worker_session)
    created = repo.create(_event())
    original_id = created.id

    processor = TelemetryProcessor(
        hot_storage=InMemoryHotStore(), data_lake_storage=InMemoryDataLakeStore()
    )
    process_pending_events(worker_session, processor, after=None)

    remaining = TelemetryRepository(worker_session).list_all()
    assert len(remaining) == 1
    assert remaining[0].id == original_id


def test_process_pending_events_with_no_rows_returns_same_watermark(
    worker_session: Session,
) -> None:
    """An empty queue is a no-op and preserves the current watermark."""
    processor = TelemetryProcessor(
        hot_storage=InMemoryHotStore(), data_lake_storage=InMemoryDataLakeStore()
    )
    marker = datetime(2020, 1, 1, tzinfo=UTC)

    processed, watermark = process_pending_events(
        worker_session, processor, after=marker
    )

    assert processed == 0
    assert watermark == marker
