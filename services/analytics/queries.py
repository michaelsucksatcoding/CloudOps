"""Analytics queries and aggregation operations."""

import pandas as pd


def aggregate_service_metrics(
    df: pd.DataFrame,
    service_id: str | None = None,
) -> dict[str, float]:
    """Calculate aggregated metrics (mean latency, error rate, resource utilization)."""
    if df.empty:
        return {
            "avg_latency_ms": 0.0,
            "error_rate": 0.0,
            "avg_cpu_percent": 0.0,
            "avg_memory_percent": 0.0,
        }

    filtered = df if service_id is None else df[df["service"] == service_id]
    if filtered.empty:
        return {
            "avg_latency_ms": 0.0,
            "error_rate": 0.0,
            "avg_cpu_percent": 0.0,
            "avg_memory_percent": 0.0,
        }

    total = len(filtered)
    errors = int((filtered["status_code"] >= 400).sum())

    return {
        "avg_latency_ms": float(filtered["latency_ms"].mean()),
        "error_rate": float(errors / total if total > 0 else 0.0),
        "avg_cpu_percent": float(filtered["cpu_percent"].mean()),
        "avg_memory_percent": float(filtered["memory_percent"].mean()),
    }
