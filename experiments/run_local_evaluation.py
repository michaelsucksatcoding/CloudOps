"""Run reproducible local ML, pipeline, API, and metric-emission experiments."""

from __future__ import annotations

import json
import platform
import statistics
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import sklearn
from fastapi.testclient import TestClient
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score

from services.analytics.feature_engineering import extract_features
from services.api.app.main import create_app
from services.api.app.monitoring.metrics import get_latest_metrics
from services.event_processor.processor import TelemetryProcessor
from services.event_processor.storage import InMemoryDataLakeStore, InMemoryHotStore
from services.ml.train import train_model
from services.simulator.incidents import IncidentScenario
from services.simulator.telemetry import TelemetrySimulator

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "configs" / "local-evaluation.json"
RESULTS_PATH = ROOT / "results" / "local-evaluation-results.json"


def percentile(values: list[float], percentile_value: float) -> float:
    """Return a nearest-rank percentile without adding a numerical dependency."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int((len(ordered) - 1) * percentile_value))
    return ordered[index]


def scenario_events(scenario: IncidentScenario, count: int, seed: int) -> pd.DataFrame:
    """Generate labelled simulator telemetry for one reproducible scenario."""
    simulator = TelemetrySimulator(seed=seed)
    return pd.DataFrame(
        [simulator.generate_event(scenario=scenario).model_dump() for _ in range(count)]
    )


def evaluate_scenarios(
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[int], list[int]]:
    """Evaluate simulator-labelled normal and incident telemetry with Isolation Forest."""
    detector = train_model()
    records: list[dict[str, Any]] = []
    all_truth: list[int] = []
    all_predictions: list[int] = []

    for offset, scenario in enumerate(IncidentScenario):
        telemetry = scenario_events(
            scenario,
            int(config["samples_per_scenario"]),
            int(config["random_seed"]) + offset,
        )
        features = extract_features(telemetry)
        started = time.perf_counter()
        predictions = detector.predict(features)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        predicted_anomaly = (predictions == -1).astype(int)
        actual_anomaly = 0 if scenario is IncidentScenario.NORMAL else 1
        truth = [actual_anomaly] * len(predicted_anomaly)

        all_truth.extend(truth)
        all_predictions.extend(predicted_anomaly.tolist())
        records.append(
            {
                "scenario": scenario.value,
                "simulated_incident": actual_anomaly == 1,
                "events": len(predicted_anomaly),
                "detected_anomalies": int(predicted_anomaly.sum()),
                "detection_rate": float(predicted_anomaly.mean()),
                "mean_inference_latency_ms_per_event": elapsed_ms
                / len(predicted_anomaly),
            }
        )
    return records, all_truth, all_predictions


def measure_pipeline_latency() -> dict[str, float]:
    """Measure local in-memory event validation and routing latency."""
    processor = TelemetryProcessor(InMemoryHotStore(), InMemoryDataLakeStore())
    event = TelemetrySimulator(seed=7).generate_event().model_dump()
    samples: list[float] = []
    for _ in range(100):
        started = time.perf_counter()
        processor.process_event(event)
        samples.append((time.perf_counter() - started) * 1000.0)
    return {
        "samples": float(len(samples)),
        "mean_ms": statistics.mean(samples),
        "p50_ms": percentile(samples, 0.50),
        "p95_ms": percentile(samples, 0.95),
        "p99_ms": percentile(samples, 0.99),
    }


def measure_api(config: dict[str, Any]) -> list[dict[str, float]]:
    """Measure sequential in-process FastAPI liveness requests at three load sizes."""
    measurements: list[dict[str, float]] = []
    with TestClient(create_app()) as client:
        for request_count in config["api_request_counts"]:
            latencies: list[float] = []
            errors = 0
            overall_started = time.perf_counter()
            for _ in range(int(request_count)):
                started = time.perf_counter()
                response = client.get(str(config["endpoint"]))
                latencies.append((time.perf_counter() - started) * 1000.0)
                errors += int(response.status_code >= 400)
            elapsed_s = time.perf_counter() - overall_started
            measurements.append(
                {
                    "requests": float(request_count),
                    "throughput_requests_per_second": request_count / elapsed_s,
                    "error_rate": errors / request_count,
                    "p50_latency_ms": percentile(latencies, 0.50),
                    "p95_latency_ms": percentile(latencies, 0.95),
                    "p99_latency_ms": percentile(latencies, 0.99),
                }
            )
    return measurements


def run() -> dict[str, Any]:
    """Execute all local experiments and persist raw measured output."""
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    scenarios, truth, predictions = evaluate_scenarios(config)
    tn, fp, fn, tp = confusion_matrix(truth, predictions, labels=[0, 1]).ravel()
    metrics_text = get_latest_metrics().decode("utf-8")
    results: dict[str, Any] = {
        "experiment_id": config["experiment_id"],
        "executed_at": datetime.now(UTC).isoformat(),
        "environment": {
            "execution": "local in-process FastAPI and in-memory event storage",
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "scikit_learn": sklearn.__version__,
        },
        "configuration": config,
        "ml_scenarios": scenarios,
        "ml_metrics": {
            "true_positives": int(tp),
            "false_positives": int(fp),
            "true_negatives": int(tn),
            "false_negatives": int(fn),
            "precision": float(precision_score(truth, predictions, zero_division=0)),
            "recall": float(recall_score(truth, predictions, zero_division=0)),
            "f1": float(f1_score(truth, predictions, zero_division=0)),
            "false_positive_rate": float(fp / (fp + tn)) if fp + tn else 0.0,
            "false_negative_rate": float(fn / (fn + tp)) if fn + tp else 0.0,
        },
        "pipeline_latency": measure_pipeline_latency(),
        "api_performance": measure_api(config),
        "observability": {
            "metrics_emitted": {
                "anomalies_detected": "cloudops_anomalies_detected_total"
                in metrics_text,
                "ml_inference": "cloudops_ml_inference_total" in metrics_text,
                "telemetry_processed": "cloudops_telemetry_events_processed_total"
                in metrics_text,
            },
            "grafana_or_prometheus_alert_evaluated": False,
        },
    }
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    output = run()
    print(f"Wrote measured results to {RESULTS_PATH}")
    print(json.dumps(output["ml_metrics"], indent=2))
