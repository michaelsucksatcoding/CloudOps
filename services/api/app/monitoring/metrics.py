"""Prometheus metric collectors and registry for CloudOps AI.

Exposes low-cardinality application, event-processing, and ML observability metrics.
"""

from __future__ import annotations

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# Standard HTTP latency buckets in seconds
HTTP_LATENCY_BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
)

# ML inference latency buckets in seconds
ML_LATENCY_BUCKETS = (
    0.001,
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
)

# -----------------------------------------------------------------------------
# Application HTTP Metrics
# -----------------------------------------------------------------------------
HTTP_REQUESTS_TOTAL = Counter(
    "cloudops_http_requests_total",
    "Total count of HTTP requests processed by the API service.",
    ["method", "route", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "cloudops_http_request_duration_seconds",
    "HTTP request execution latency distribution in seconds.",
    ["method", "route"],
    buckets=HTTP_LATENCY_BUCKETS,
)

HTTP_ACTIVE_REQUESTS = Gauge(
    "cloudops_http_active_requests",
    "Number of in-flight HTTP requests currently executing.",
    ["method", "route"],
)

HTTP_ERRORS_TOTAL = Counter(
    "cloudops_http_errors_total",
    "Total count of HTTP server or validation errors.",
    ["method", "route", "error_type"],
)

# -----------------------------------------------------------------------------
# Event Pipeline Metrics
# -----------------------------------------------------------------------------
TELEMETRY_EVENTS_RECEIVED_TOTAL = Counter(
    "cloudops_telemetry_events_received_total",
    "Total count of telemetry events ingested into the platform.",
)

TELEMETRY_EVENTS_PROCESSED_TOTAL = Counter(
    "cloudops_telemetry_events_processed_total",
    "Total count of telemetry events successfully processed and routed.",
    ["status"],
)

TELEMETRY_EVENTS_FAILED_TOTAL = Counter(
    "cloudops_telemetry_events_failed_total",
    "Total count of telemetry events that failed validation or routing.",
    ["reason"],
)

# -----------------------------------------------------------------------------
# Machine Learning & Health Scoring Metrics
# -----------------------------------------------------------------------------
ANOMALIES_DETECTED_TOTAL = Counter(
    "cloudops_anomalies_detected_total",
    "Total count of anomalous telemetry events flagged by ML detectors.",
)

ML_INFERENCE_DURATION_SECONDS = Histogram(
    "cloudops_ml_inference_duration_seconds",
    "Execution duration of machine learning inference passes.",
    ["model_type"],
    buckets=ML_LATENCY_BUCKETS,
)

ML_INFERENCE_TOTAL = Counter(
    "cloudops_ml_inference_total",
    "Total count of ML inference executions performed.",
    ["model_type", "status"],
)

SERVICE_HEALTH_SCORE = Gauge(
    "cloudops_service_health_score",
    "Current composite health score of registered services (0.0=outage, 1.0=optimal).",
    ["service"],
)


def get_latest_metrics(registry: CollectorRegistry = REGISTRY) -> bytes:
    """Generate Prometheus exposition text format representation."""
    return generate_latest(registry)


def get_metrics_content_type() -> str:
    """Return standard Prometheus text format content-type header."""
    return CONTENT_TYPE_LATEST
