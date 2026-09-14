"""Monitoring, metrics, and structured logging package for CloudOps AI."""

from services.api.app.monitoring.logging import (
    JSONLogFormatter,
    get_current_request_id,
    set_current_request_id,
    setup_logging,
)
from services.api.app.monitoring.metrics import (
    HTTP_ACTIVE_REQUESTS,
    HTTP_ERRORS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
    ML_INFERENCE_DURATION_SECONDS,
    ML_INFERENCE_TOTAL,
    SERVICE_HEALTH_SCORE,
    TELEMETRY_EVENTS_FAILED_TOTAL,
    TELEMETRY_EVENTS_PROCESSED_TOTAL,
    TELEMETRY_EVENTS_RECEIVED_TOTAL,
    get_latest_metrics,
    get_metrics_content_type,
)
from services.api.app.monitoring.middleware import ObservabilityMiddleware

__all__ = [
    "HTTP_ACTIVE_REQUESTS",
    "HTTP_ERRORS_TOTAL",
    "HTTP_REQUESTS_TOTAL",
    "HTTP_REQUEST_DURATION_SECONDS",
    "JSONLogFormatter",
    "ML_INFERENCE_DURATION_SECONDS",
    "ML_INFERENCE_TOTAL",
    "ObservabilityMiddleware",
    "SERVICE_HEALTH_SCORE",
    "TELEMETRY_EVENTS_FAILED_TOTAL",
    "TELEMETRY_EVENTS_PROCESSED_TOTAL",
    "TELEMETRY_EVENTS_RECEIVED_TOTAL",
    "get_current_request_id",
    "get_latest_metrics",
    "get_metrics_content_type",
    "set_current_request_id",
    "setup_logging",
]
