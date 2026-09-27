"""Tests for the telemetry event processor."""

import json

import pytest

from services.event_processor.processor import TelemetryProcessor
from services.event_processor.storage import InMemoryDataLakeStore, InMemoryHotStore


def test_process_valid_event() -> None:
    """Verify processor validates correct telemetry event and routes to hot and cold stores."""
    hot_store = InMemoryHotStore()
    lake_store = InMemoryDataLakeStore()
    processor = TelemetryProcessor(hot_storage=hot_store, data_lake_storage=lake_store)

    raw_data = {
        "timestamp": "2026-09-02T15:20:32Z",
        "service": "auth-service",
        "endpoint": "/login",
        "status_code": 200,
        "latency_ms": 25.4,
        "cpu_percent": 15.0,
        "memory_percent": 30.0,
    }
    event = processor.process_event(raw_data)
    assert event.service == "auth-service"
    assert event.status_code == 200

    # Verify stored in hot store
    hot_events = hot_store.get_latest_events("auth-service")
    assert len(hot_events) == 1
    assert hot_events[0].latency_ms == 25.4

    # Verify stored in data lake
    lake_objects = lake_store.get_objects()
    assert len(lake_objects) == 1


def test_process_invalid_event_raises() -> None:
    """Verify invalid event raises ValueError with diagnostics."""
    processor = TelemetryProcessor()
    invalid_data = {
        "service": "broken-svc",
        "status_code": 888,  # invalid
        "latency_ms": -5.0,  # negative
    }
    with pytest.raises(ValueError) as exc_info:
        processor.process_event(invalid_data)
    assert "Invalid telemetry event schema" in str(exc_info.value)


def test_process_batch_raw_payloads() -> None:
    """Verify process_batch routes a batch of raw telemetry payloads."""
    hot_store = InMemoryHotStore()
    processor = TelemetryProcessor(hot_storage=hot_store)

    records = [
        {
            "timestamp": "2026-09-02T15:20:32Z",
            "service": "order-service",
            "endpoint": "/checkout",
            "status_code": 200,
            "latency_ms": 110.0,
            "cpu_percent": 45.0,
            "memory_percent": 55.0,
        }
    ]
    result = processor.process_batch(records)

    assert result["processed"] == 1
    assert result["failed"] == 0
    assert len(hot_store.get_latest_events("order-service")) == 1


def test_process_batch_accepts_json_string_envelope() -> None:
    """Verify process_batch also accepts a {"data": "<json>"} envelope."""
    hot_store = InMemoryHotStore()
    processor = TelemetryProcessor(hot_storage=hot_store)

    payload = {
        "timestamp": "2026-09-02T15:20:32Z",
        "service": "order-service",
        "endpoint": "/checkout",
        "status_code": 200,
        "latency_ms": 110.0,
        "cpu_percent": 45.0,
        "memory_percent": 55.0,
    }
    result = processor.process_batch([{"data": json.dumps(payload)}])

    assert result["processed"] == 1
    assert result["failed"] == 0
    assert len(hot_store.get_latest_events("order-service")) == 1


def test_process_batch_partial_failures() -> None:
    """Verify process_batch continues processing when some records are malformed."""
    hot_store = InMemoryHotStore()
    processor = TelemetryProcessor(hot_storage=hot_store)

    valid_payload = {
        "timestamp": "2026-09-02T15:20:32Z",
        "service": "valid-service",
        "endpoint": "/api",
        "status_code": 200,
        "latency_ms": 50.0,
        "cpu_percent": 20.0,
        "memory_percent": 30.0,
    }
    records = [
        valid_payload,
        {"service": "incomplete", "status_code": 999},
    ]
    result = processor.process_batch(records)

    assert result["processed"] == 1
    assert result["failed"] == 1
    assert len(result["errors"]) == 1
    assert len(hot_store.get_latest_events("valid-service")) == 1
