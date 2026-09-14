"""Tests for API routes."""

from fastapi.testclient import TestClient


def test_list_services_route(client: TestClient) -> None:
    """Verify GET /services returns a list of services."""
    response = client.get("/services")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_ingest_telemetry_event_route(client: TestClient) -> None:
    """Verify POST /events ingests valid telemetry payload."""
    payload = {
        "timestamp": "2026-09-02T15:20:32Z",
        "service": "payment-api",
        "endpoint": "/api/payment",
        "status_code": 200,
        "latency_ms": 45.2,
        "cpu_percent": 32.1,
        "memory_percent": 48.0,
    }
    response = client.post("/events", json=payload)
    assert response.status_code == 201
    assert response.json()["service"] == "payment-api"
