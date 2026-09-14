"""Tests for telemetry event ingestion, streaming, and querying."""

from fastapi.testclient import TestClient

from services.api.app.dependencies import get_hot_storage
from services.api.app.schemas.telemetry import TelemetryEventCreate
from services.event_processor.storage import InMemoryHotStore


def test_ingest_and_query_telemetry_event(client: TestClient) -> None:
    """Verify ingesting a valid telemetry payload and querying it back."""
    payload = {
        "timestamp": "2026-09-03T12:00:00Z",
        "service": "billing-api",
        "endpoint": "/api/v1/charge",
        "status_code": 200,
        "latency_ms": 142.5,
        "cpu_percent": 45.2,
        "memory_percent": 60.1,
        "request_rate": 35.0,
        "queue_depth": 5,
        "deployment_version": "v1.2.0",
        "instance_id": "pod-billing-79d8",
        "environment": "prod",
        "tenant_id": "org-acme",
        "region": "us-east-1",
    }
    response = client.post("/events", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["service"] == "billing-api"
    assert data["latency_ms"] == 142.5
    assert "id" in data
    assert "created_at" in data

    # Query all events
    list_res = client.get("/events")
    assert list_res.status_code == 200
    events = list_res.json()
    assert len(events) >= 1
    assert any(e["service"] == "billing-api" for e in events)

    # Query filtered by service
    filtered_res = client.get("/events?service=billing-api")
    assert filtered_res.status_code == 200
    filtered_events = filtered_res.json()
    assert len(filtered_events) >= 1
    assert all(e["service"] == "billing-api" for e in filtered_events)


def test_get_hot_telemetry_events_endpoint(client: TestClient) -> None:
    """Verify GET /events/hot retrieves events from Hot Storage."""
    hot_store = InMemoryHotStore()
    from services.api.app.main import app

    app.dependency_overrides[get_hot_storage] = lambda: hot_store

    from datetime import UTC, datetime

    event = TelemetryEventCreate(
        timestamp=datetime.now(UTC),
        service="auth-service",
        endpoint="/login",
        status_code=200,
        latency_ms=30.0,
        cpu_percent=10.0,
        memory_percent=20.0,
    )
    hot_store.put_event(event)

    response = client.get("/events/hot?service=auth-service")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 1
    assert events[0]["service"] == "auth-service"

    app.dependency_overrides.pop(get_hot_storage, None)


def test_ingest_telemetry_validation_error(client: TestClient) -> None:
    """Verify invalid telemetry payload (e.g. invalid status_code or negative latency) is rejected."""
    invalid_payload = {
        "timestamp": "not-a-timestamp",
        "service": "billing-api",
        "endpoint": "/charge",
        "status_code": 999,  # Invalid HTTP status code (> 599)
        "latency_ms": -10.0,  # Negative latency
        "cpu_percent": 150.0,  # > 100%
        "memory_percent": 50.0,
    }
    response = client.post("/events", json=invalid_payload)
    assert response.status_code == 422
