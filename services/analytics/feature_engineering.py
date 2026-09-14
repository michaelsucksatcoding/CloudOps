"""Feature engineering for telemetry metrics and ML datasets."""

import pandas as pd

FEATURE_COLUMNS = [
    "latency_ms",
    "cpu_percent",
    "memory_percent",
    "is_error",
    "is_server_error",
]


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and engineer ML telemetry features from raw dataframe."""
    features = pd.DataFrame()
    features["latency_ms"] = df["latency_ms"].astype(float)
    features["cpu_percent"] = df["cpu_percent"].astype(float)
    features["memory_percent"] = df["memory_percent"].astype(float)
    features["is_error"] = (df["status_code"] >= 400).astype(int)
    features["is_server_error"] = (df["status_code"] >= 500).astype(int)
    return features[FEATURE_COLUMNS]
