"""Model training script for Isolation Forest anomaly detection."""

import logging

import numpy as np
import pandas as pd

from services.ml.anomaly_detection import AnomalyDetector

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def train_model() -> AnomalyDetector:
    """Train baseline anomaly detection model with synthetic baseline data."""
    logger.info("Starting ML model training...")
    np.random.seed(42)

    # Generate normal telemetry features
    n_samples = 1000
    latency = np.random.normal(loc=100.0, scale=15.0, size=n_samples)
    cpu = np.random.normal(loc=35.0, scale=8.0, size=n_samples)
    memory = np.random.normal(loc=45.0, scale=5.0, size=n_samples)
    is_error = np.zeros(n_samples)
    is_server_error = np.zeros(n_samples)

    features = pd.DataFrame(
        {
            "latency_ms": np.clip(latency, 10.0, 500.0),
            "cpu_percent": np.clip(cpu, 1.0, 100.0),
            "memory_percent": np.clip(memory, 1.0, 100.0),
            "is_error": is_error,
            "is_server_error": is_server_error,
        }
    )

    detector = AnomalyDetector(contamination=0.02, random_state=42)
    detector.fit(features)
    logger.info(
        "Anomaly detection model successfully trained on %d samples.", len(features)
    )
    return detector


if __name__ == "__main__":
    train_model()
