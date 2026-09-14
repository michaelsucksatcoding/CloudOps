"""Isolation Forest anomaly detection baseline."""

import time
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from services.api.app.monitoring.metrics import (
    ANOMALIES_DETECTED_TOTAL,
    ML_INFERENCE_DURATION_SECONDS,
    ML_INFERENCE_TOTAL,
)


class AnomalyDetector:
    """Isolation Forest based anomaly detector for cloud telemetry features."""

    def __init__(
        self,
        contamination: float = 0.05,
        random_state: int = 42,
        n_estimators: int = 100,
    ) -> None:
        self.contamination = contamination
        self.random_state = random_state
        self.n_estimators = n_estimators
        self.model: IsolationForest = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=self.n_estimators,
        )
        self.is_fitted: bool = False

    def fit(self, features: pd.DataFrame | np.ndarray[Any, Any]) -> "AnomalyDetector":
        """Train the Isolation Forest model on normal telemetry data."""
        self.model.fit(features)
        self.is_fitted = True
        return self

    def predict(
        self, features: pd.DataFrame | np.ndarray[Any, Any]
    ) -> np.ndarray[Any, Any]:
        """Predict whether samples are anomalies (-1: anomaly, 1: normal)."""
        if not self.is_fitted:
            raise RuntimeError(
                "AnomalyDetector model must be fitted before predicting."
            )
        start_time = time.perf_counter()
        try:
            predictions = np.asarray(self.model.predict(features))
            anomaly_count = int(np.count_nonzero(predictions == -1))
            if anomaly_count:
                ANOMALIES_DETECTED_TOTAL.inc(anomaly_count)
            ML_INFERENCE_TOTAL.labels(
                model_type="isolation_forest", status="success"
            ).inc()
            return predictions
        except Exception:
            ML_INFERENCE_TOTAL.labels(
                model_type="isolation_forest", status="error"
            ).inc()
            raise
        finally:
            ML_INFERENCE_DURATION_SECONDS.labels(model_type="isolation_forest").observe(
                time.perf_counter() - start_time
            )

    def score_samples(
        self, features: pd.DataFrame | np.ndarray[Any, Any]
    ) -> np.ndarray[Any, Any]:
        """Compute anomaly score (lower is more anomalous)."""
        if not self.is_fitted:
            raise RuntimeError("AnomalyDetector model must be fitted before scoring.")
        return np.asarray(self.model.score_samples(features))
