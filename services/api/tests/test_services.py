"""Tests for service management API endpoints."""

from fastapi.testclient import TestClient


def test_create_and_get_service(client: TestClient) -> None:
    """Verify registering a service and retrieving its details."""
    payload = {
        "id": "payment-api",
        "name": "Payment Gateway API",
        "environment": "dev",
    }
    response = client.post("/services", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "payment-api"
    assert data["name"] == "Payment Gateway API"
    assert data["environment"] == "dev"
    assert data["status"] == "healthy"
    assert data["current_health_score"] == 1.0

    # Get by ID
    get_res = client.get("/services/payment-api")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Payment Gateway API"


def test_create_duplicate_service_conflict(client: TestClient) -> None:
    """Verify duplicate service ID returns 409 conflict."""
    payload = {
        "id": "auth-service",
        "name": "Authentication Service",
        "environment": "prod",
    }
    res1 = client.post("/services", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/services", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_get_nonexistent_service_404(client: TestClient) -> None:
    """Verify non-existent service ID returns 404."""
    response = client.get("/services/unknown-service-xyz")
    assert response.status_code == 404


def test_update_service(client: TestClient) -> None:
    """Verify updating service status and health score."""
    create_payload = {
        "id": "worker-service",
        "name": "Background Worker",
        "environment": "staging",
    }
    client.post("/services", json=create_payload)

    update_payload = {
        "status": "degraded",
        "current_health_score": 0.65,
    }
    patch_res = client.patch("/services/worker-service", json=update_payload)
    assert patch_res.status_code == 200
    updated_data = patch_res.json()
    assert updated_data["status"] == "degraded"
    assert updated_data["current_health_score"] == 0.65


def test_list_services(client: TestClient) -> None:
    """Verify listing all registered services."""
    client.post(
        "/services", json={"id": "svc-1", "name": "Service 1", "environment": "dev"}
    )
    client.post(
        "/services", json={"id": "svc-2", "name": "Service 2", "environment": "dev"}
    )

    response = client.get("/services")
    assert response.status_code == 200
    services = response.json()
    assert len(services) >= 2
