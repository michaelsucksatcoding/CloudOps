# Evaluation Methodology

The local evaluation uses Isolation Forest trained by `services.ml.train` on
1,000 seeded synthetic normal samples (seed 42; contamination 0.02; random
state 42). Test events are produced by the deterministic simulator with seed
20260914: 100 events per scenario across the 8 supported scenarios, for 800
evaluation samples in total.

## Ground truth

Ground truth is supplied by the simulator scenario, not by the telemetry
schema:

- `normal` is the negative class (100 samples).
- The seven incident scenarios (`cpu_spike`, `memory_pressure`,
  `latency_spike`, `error_spike`, `database_failure`, `queue_backlog`,
  `deployment_regression`) are the positive class (700 samples).

These labels are synthetic simulator labels. They are **not** production ground
truth.

## Metrics measured

- Confusion-matrix counts (TP, FP, TN, FN).
- Precision, recall, F1, false-positive rate, false-negative rate.
- Per-scenario detection rates.
- Per-scenario mean inference latency. The harness reports only a mean per
  scenario; inference latency is **not** reported as p50/p95/p99.
- In-memory event validation/routing latency over 100 calls (mean, p50, p95,
  p99).
- Sequential in-process API `/health/live` latency and throughput at 50, 200,
  and 500 requests.

Monotonic `perf_counter` is used within each process, avoiding mixed wall
clocks. Observability metric families for anomalies, ML inference, and
processed telemetry are emitted during the run; Prometheus/Grafana alert
delivery is intentionally not evaluated by the local harness.

## Scope of measurements

This does not measure Kinesis, Lambda, S3, DynamoDB, network transport,
Grafana rendering, Prometheus alert delivery, CloudWatch, or EKS HPA timing.
Local in-memory performance measurements are not equivalent to production
distributed-system measurements.