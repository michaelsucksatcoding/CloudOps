"""End-to-end telemetry flow test: Simulation -> Ingestion API -> Anomaly Evaluation."""

import pandas as pd
from fastapi.testclient import TestClient

from services.analytics.feature_engineering import extract_features
from services.ml.train import train_model
from services.simulator.incidents import IncidentScenario
from services.simulator.telemetry import TelemetrySimulator


def test_e2e_telemetry_to_ml_pipeline(api_client: TestClient) -> None:
    """Verify full loop: simulation, API ingestion, feature extraction, and ML scoring."""
    simulator = TelemetrySimulator(seed=999)
    detector = train_model()

    # Generate incident event and submit to API
    incident_event = simulator.generate_event(scenario=IncidentScenario.LATENCY_SPIKE)
    response = api_client.post("/events", json=incident_event.model_dump(mode="json"))
    assert response.status_code == 201

    # Extract features and verify anomaly score is negative / flagged
    df = pd.DataFrame([incident_event.model_dump()])
    features = extract_features(df)
    score = detector.score_samples(features)[0]
    assert score < 0.0  # Flagged anomalous relative to normal baseline
