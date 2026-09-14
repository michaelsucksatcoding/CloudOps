"""Tests for Prometheus metrics and request-correlation observability."""

from fastapi.testclient import TestClient


def test_metrics_endpoint_exposes_http_metrics(client: TestClient) -> None:
    """The Prometheus endpoint exposes the application metric families."""
    client.get("/health/live")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "cloudops_http_requests_total" in response.text
    assert "cloudops_http_request_duration_seconds" in response.text


def test_request_id_is_propagated(client: TestClient) -> None:
    """An inbound request ID is returned for client-side correlation."""
    response = client.get("/health/live", headers={"X-Request-ID": "test-request"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request"
