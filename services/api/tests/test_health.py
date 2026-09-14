"""Tests for health check endpoints."""

from fastapi.testclient import TestClient


def test_health_check_returns_200(client: TestClient) -> None:
    """Verify GET /health returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert "app" in data
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data


def test_health_liveness_probe(client: TestClient) -> None:
    """Verify GET /health/live returns 200 without dependent service checks."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "untested"
    assert "app" in data


def test_health_readiness_probe(client: TestClient) -> None:
    """Verify GET /health/ready returns 200 when database connection is healthy."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
