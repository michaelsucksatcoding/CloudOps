"""Unit tests for TelemetryProducer abstractions."""

from datetime import UTC, datetime

import pytest

from services.api.app.config import settings
from services.api.app.schemas.telemetry import TelemetryEventCreate
from services.event_processor.producer import (
    InMemoryProducer,
    KinesisProducer,
    get_stream_producer,
)


def _sample_event() -> TelemetryEventCreate:
    return TelemetryEventCreate(
        timestamp=datetime.now(UTC),
        service="auth-service",
        endpoint="/login",
        status_code=200,
        latency_ms=18.5,
        cpu_percent=22.0,
        memory_percent=40.0,
    )


def test_in_memory_producer_send_event() -> None:
    """Verify InMemoryProducer buffers single events."""
    producer = InMemoryProducer()
    event = _sample_event()
    rec_id = producer.send_event(event)

    assert rec_id.startswith("mem-rec-")
    buffered = producer.get_events()
    assert len(buffered) == 1
    assert buffered[0]["event"].service == "auth-service"


def test_in_memory_producer_send_batch() -> None:
    """Verify InMemoryProducer buffers event batches."""
    producer = InMemoryProducer()
    events = [_sample_event(), _sample_event()]
    rec_ids = producer.send_batch(events)

    assert len(rec_ids) == 2
    assert len(producer.get_events()) == 2

    producer.clear()
    assert len(producer.get_events()) == 0


def test_kinesis_producer_initialization() -> None:
    """Verify KinesisProducer properties."""
    kp = KinesisProducer(stream_name="test-stream", region="us-east-1")
    assert kp.stream_name == "test-stream"
    assert kp.region == "us-east-1"


def test_get_stream_producer_defaults_to_in_memory() -> None:
    """Verify the factory returns the in-memory producer by default."""
    producer = get_stream_producer()
    assert isinstance(producer, InMemoryProducer)


def test_get_stream_producer_returns_kinesis_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify the factory returns KinesisProducer when explicitly configured."""
    monkeypatch.setattr(settings, "telemetry_producer", "kinesis")
    producer = get_stream_producer()
    assert isinstance(producer, KinesisProducer)

    monkeypatch.setattr(settings, "telemetry_producer", "in_memory")
    assert isinstance(get_stream_producer(), InMemoryProducer)
