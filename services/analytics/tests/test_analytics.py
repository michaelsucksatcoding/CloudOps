"""Tests for analytics feature engineering and queries."""

import pandas as pd

from services.analytics.feature_engineering import extract_features
from services.analytics.queries import aggregate_service_metrics


def test_extract_features() -> None:
    """Verify feature extraction computes error and latency features."""
    df = pd.DataFrame(
        [
            {
                "timestamp": "2026-09-02T15:20:32Z",
                "service": "payment-api",
                "endpoint": "/charge",
                "status_code": 500,
                "latency_ms": 1500.0,
                "cpu_percent": 85.0,
                "memory_percent": 75.0,
            },
            {
                "timestamp": "2026-09-02T15:20:33Z",
                "service": "payment-api",
                "endpoint": "/charge",
                "status_code": 200,
                "latency_ms": 120.0,
                "cpu_percent": 30.0,
                "memory_percent": 40.0,
            },
        ]
    )
    features = extract_features(df)
    assert len(features) == 2
    assert features["is_error"].tolist() == [1, 0]
    assert features["is_server_error"].tolist() == [1, 0]


def test_aggregate_service_metrics() -> None:
    """Verify aggregation computes expected means and error rate."""
    df = pd.DataFrame(
        [
            {
                "service": "api",
                "status_code": 200,
                "latency_ms": 100.0,
                "cpu_percent": 50.0,
                "memory_percent": 60.0,
            },
            {
                "service": "api",
                "status_code": 500,
                "latency_ms": 200.0,
                "cpu_percent": 70.0,
                "memory_percent": 80.0,
            },
        ]
    )
    metrics = aggregate_service_metrics(df, "api")
    assert metrics["avg_latency_ms"] == 150.0
    assert metrics["error_rate"] == 0.5
    assert metrics["avg_cpu_percent"] == 60.0
    assert metrics["avg_memory_percent"] == 70.0
