# Local Evaluation Results

The measured result set is [`experiments/results/local-evaluation-results.json`](../../experiments/results/local-evaluation-results.json).
It was executed locally on 2026-09-14 using Python 3.13.5 and scikit-learn
1.9.0. Values below are derived from that raw file, not hand-entered targets.

| Metric | Measured value |
| --- | ---: |
| Precision | 0.8737 |
| Recall | 0.8700 |
| F1 | 0.8719 |
| False-positive rate | 0.8800 |
| False-negative rate | 0.1300 |
| Mean local pipeline latency | 0.2826 ms |
| P95 local pipeline latency | 0.4650 ms |

The detector identified 609 of 700 synthetic incident events, but also marked
88 of 100 synthetic normal events anomalous. The high false-positive rate is a
material negative result: these measurements do not support operational use
without recalibration and more representative normal training data.

The sequential in-process `/health/live` experiment had zero HTTP errors. Its
P95 latency was 3.75 ms (50 requests), 4.80 ms (200), and 4.00 ms (500).
These are process-local TestClient measurements, not network or Kubernetes
load-test results. Metric families for anomalies, ML inference, and processed
telemetry were emitted; Grafana and alert delivery were not evaluated locally.

![Scenario detection rate](../../experiments/results/scenario-detection-rate.svg)
