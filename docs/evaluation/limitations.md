# Evaluation Limitations

- All ground truth and telemetry are simulator-generated; they are not real
  production incidents or traffic.
- One deterministic local run was recorded. Repeated runs and confidence
  intervals have not been collected.
- API requests are sequential and in-process, excluding network, database,
  container, and concurrent-client effects.
- The pipeline timing uses in-memory stores and does not include AWS services.
- Prometheus/Grafana alert delivery, CloudWatch, Kubernetes resource use, and
  HPA scale-out were not available in the local environment and were not
  claimed as tested.
- The observed 88% false-positive rate on generated normal telemetry indicates
  substantial training-data distribution mismatch.
