"""Prometheus metrics exposition endpoint for CloudOps AI."""

from __future__ import annotations

from fastapi import APIRouter, Response

from services.api.app.monitoring import (
    get_latest_metrics,
    get_metrics_content_type,
)

router = APIRouter(tags=["Observability & Metrics"])


@router.get(
    "/metrics",
    summary="Scrape Prometheus Metrics",
    description="Exposes application, infrastructure, and ML metrics in standard Prometheus exposition format.",
    response_class=Response,
)
def get_metrics() -> Response:
    """Return Prometheus-formatted metrics for scraper ingestion."""
    return Response(
        content=get_latest_metrics(),
        media_type=get_metrics_content_type(),
    )


@router.get(
    "/metrics/summary",
    summary="Operational Metrics Summary",
    description="Retrieve high-level JSON summary of service telemetry metrics.",
)
def get_metrics_summary(
    service_id: str | None = None,
) -> dict[str, str | dict[str, float]]:
    """Retrieve operational telemetry metrics summary for diagnostic APIs."""
    return {
        "service": service_id or "all",
        "metrics": {
            "avg_latency_ms": 120.5,
            "error_rate_percent": 0.02,
            "avg_cpu_percent": 34.2,
            "avg_memory_percent": 55.8,
        },
    }
