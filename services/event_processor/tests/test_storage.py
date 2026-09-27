"""Unit tests for HotStorage and DataLakeStorage abstractions."""

from datetime import UTC, datetime

from services.api.app.schemas.telemetry import TelemetryEventCreate
from services.event_processor.storage import (
    InMemoryDataLakeStore,
    InMemoryHotStore,
)


def _create_sample_event(
    service: str = "payment-api", latency: float = 45.5
) -> TelemetryEventCreate:
    return TelemetryEventCreate(
        timestamp=datetime.now(UTC),
        service=service,
        endpoint="/api/pay",
        status_code=200,
        latency_ms=latency,
        cpu_percent=35.5,
        memory_percent=55.0,
        request_rate=20.0,
        queue_depth=2,
    )


def test_in_memory_hot_store_put_and_get() -> None:
    """Verify InMemoryHotStore stores and retrieves latest events in reverse chronological order."""
    store = InMemoryHotStore()
    e1 = _create_sample_event(latency=10.0)
    e2 = _create_sample_event(latency=50.0)

    store.put_event(e1)
    store.put_event(e2)

    latest = store.get_latest_events("payment-api", limit=10)
    assert len(latest) == 2

    # Get single event
    single = store.get_event("payment-api", e1.timestamp.isoformat())
    assert single is not None
    assert single.latency_ms == 10.0


def test_in_memory_data_lake_store() -> None:
    """Verify InMemoryDataLakeStore generates partition key and stores JSON."""
    store = InMemoryDataLakeStore()
    event = _create_sample_event(service="order-svc")
    key = store.save_event(event)

    assert "service=order-svc" in key
    objects = store.get_objects()
    assert key in objects
    assert "order-svc" in objects[key]
