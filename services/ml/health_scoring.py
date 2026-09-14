"""Service health scoring calculation based on anomaly score and metrics."""

import numpy as np


class ServiceHealthScorer:
    """Calculates normalized service health score in range [0.0, 1.0]."""

    def calculate_score(
        self,
        anomaly_score: float,
        error_rate: float,
        cpu_percent: float,
        memory_percent: float,
    ) -> float:
        """Calculate composite health score. 1.0 = optimal health, 0.0 = total outage."""
        # Baseline health starts at 1.0
        # Deduct penalties for high error rate, resource exhaustion, and ML anomaly score
        error_penalty = min(error_rate * 2.0, 0.5)
        cpu_penalty = 0.2 if cpu_percent > 85.0 else 0.0
        mem_penalty = 0.2 if memory_percent > 85.0 else 0.0

        # Anomaly score is typically between -0.5 and 0.5 in IsolationForest
        # More negative means more anomalous
        ml_penalty = 0.3 if anomaly_score < -0.1 else 0.0

        raw_score = 1.0 - (error_penalty + cpu_penalty + mem_penalty + ml_penalty)
        return float(np.clip(raw_score, 0.0, 1.0))
