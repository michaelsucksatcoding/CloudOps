"""Unit tests for TelemetryProducer abstractions."""

from datetime import UTC, datetime

from services.api.app.schemas.telemetry import TelemetryEventCreate
from services.event_processor.producer import InMemoryProducer, KinesisProducer


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
