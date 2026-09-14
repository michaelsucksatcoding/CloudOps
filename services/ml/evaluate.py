"""Model evaluation script measuring Precision, Recall, F1, and Latency."""

import logging
import time

import numpy as np
import pandas as pd
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
)

from services.ml.train import train_model

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def evaluate_model() -> dict[str, float]:
    """Evaluate trained model against synthetic normal and incident datasets."""
    logger.info("Evaluating ML model...")
    detector = train_model()

    np.random.seed(123)
    n_normal = 500
    n_anom = 50

    # Normal dataset
    normal_features = pd.DataFrame(
        {
            "latency_ms": np.random.normal(loc=100.0, scale=15.0, size=n_normal),
            "cpu_percent": np.random.normal(loc=35.0, scale=8.0, size=n_normal),
            "memory_percent": np.random.normal(loc=45.0, scale=5.0, size=n_normal),
            "is_error": np.zeros(n_normal),
            "is_server_error": np.zeros(n_normal),
        }
    )

    # Simulated incident telemetry (high latency & high error rate)
    anom_features = pd.DataFrame(
        {
            "latency_ms": np.random.normal(loc=1800.0, scale=200.0, size=n_anom),
            "cpu_percent": np.random.normal(loc=85.0, scale=5.0, size=n_anom),
            "memory_percent": np.random.normal(loc=90.0, scale=3.0, size=n_anom),
            "is_error": np.ones(n_anom),
            "is_server_error": np.ones(n_anom),
        }
    )

    test_data = pd.concat([normal_features, anom_features], ignore_index=True)
    # Ground truth: 1 for normal, -1 for anomaly (matching IsolationForest conventions)
    y_true = np.array([1] * n_normal + [-1] * n_anom)

    start_time = time.perf_counter()
    y_pred = detector.predict(test_data)
    inference_latency_ms = (time.perf_counter() - start_time) * 1000.0 / len(test_data)

    # Convert to binary for metrics (1: anomaly, 0: normal)
    y_true_binary = (y_true == -1).astype(int)
    y_pred_binary = (y_pred == -1).astype(int)

    precision = float(precision_score(y_true_binary, y_pred_binary, zero_division=0))
    recall = float(recall_score(y_true_binary, y_pred_binary, zero_division=0))
    f1 = float(f1_score(y_true_binary, y_pred_binary, zero_division=0))

    logger.info("Evaluation metrics:")
    logger.info("  Precision: %.4f", precision)
    logger.info("  Recall:    %.4f", recall)
    logger.info("  F1 Score:  %.4f", f1)
    logger.info("  Inference Latency: %.3f ms/sample", inference_latency_ms)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "inference_latency_ms": inference_latency_ms,
    }


if __name__ == "__main__":
    evaluate_model()
