"""Tests for ML anomaly detection, health scoring, and evaluation."""

import pandas as pd

from services.ml.anomaly_detection import AnomalyDetector
from services.ml.evaluate import evaluate_model
from services.ml.health_scoring import ServiceHealthScorer
from services.ml.incident_prediction import IncidentPredictor


def test_anomaly_detector_training_and_prediction() -> None:
    """Verify Isolation Forest fits and predicts anomaly labels."""
    detector = AnomalyDetector(contamination=0.05, random_state=42)
    features = pd.DataFrame(
        {
            "latency_ms": [100.0, 105.0, 98.0, 102.0, 1500.0],
            "cpu_percent": [30.0, 32.0, 31.0, 29.0, 95.0],
            "memory_percent": [40.0, 42.0, 41.0, 39.0, 92.0],
            "is_error": [0, 0, 0, 0, 1],
            "is_server_error": [0, 0, 0, 0, 1],
        }
    )
    detector.fit(features)
    assert detector.is_fitted

    preds = detector.predict(features)
    assert len(preds) == 5
    assert set(preds).issubset({-1, 1})


def test_service_health_scorer() -> None:
    """Verify health score calculation drops on high errors or resource pressure."""
    scorer = ServiceHealthScorer()
    healthy_score = scorer.calculate_score(
        anomaly_score=0.2,
        error_rate=0.0,
        cpu_percent=30.0,
        memory_percent=40.0,
    )
    assert healthy_score == 1.0

    degraded_score = scorer.calculate_score(
        anomaly_score=-0.3,
        error_rate=0.25,
        cpu_percent=90.0,
        memory_percent=90.0,
    )
    assert degraded_score < 0.5


def test_incident_predictor() -> None:
    """Verify incident risk evaluation."""
    predictor = IncidentPredictor()
    nominal = predictor.evaluate_risk(health_score=0.95, recent_anomaly_count=0)
    assert nominal["risk_level"] == "nominal"

    critical = predictor.evaluate_risk(health_score=0.4, recent_anomaly_count=6)
    assert critical["risk_level"] == "critical"


def test_ml_evaluation_pipeline() -> None:
    """Verify end-to-end ML evaluation returns valid metrics."""
    metrics = evaluate_model()
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "inference_latency_ms" in metrics
    assert metrics["f1"] > 0.5
