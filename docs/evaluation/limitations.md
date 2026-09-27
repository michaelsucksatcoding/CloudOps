# Evaluation Limitations

The following limitations apply to the 2026-09-18 local evaluation and the
2026-09-14 baseline. They are experimental scoping decisions and are not
implementation tasks.

1. **Synthetic ground truth.** All telemetry and labels are simulator-generated
   (`normal` = negative; seven incident scenarios = positive). They are not
   real production incidents or traffic, and must not be presented as
   production ground truth.
2. **High false-positive rate.** FPR = 0.88: 88 of 100 normal samples were
   flagged anomalous. This is a genuine measured outcome and a major limitation
   of the current baseline, indicating substantial training-data distribution
   mismatch. See [results.md](results.md).
3. **No detection-latency / time-to-detect measurement.** The harness does not
   measure how quickly an anomaly is raised relative to its onset; no such
   utility exists in the repository.
4. **No per-event inference p50/p95/p99.** The harness reports only per-scenario
   mean inference latency, not percentiles.
5. **No confidence intervals.** Two deterministic runs were compared; no
   stochastic re-runs or confidence intervals were collected.
6. **No cloud-path timing.** Pipeline and API measurements are local and
   in-process. They exclude network transport, Grafana rendering, Prometheus
   alert delivery, and Kubernetes autoscaling timing. The project targets no
   cloud provider, so no managed-service latency is included by design.
7. **No durable asynchronous fan-out.** The former managed-stream architecture
   (API → durable stream → serverless consumer) was removed rather than replaced
   with another hosted service. The current event path polls PostgreSQL with a
   `created_at` watermark. This costs durable broker semantics, independent
   consumer scaling, and a non-durable in-process hot store; throughput is
   bounded by the database. This is an accepted reduction in capability, not an
   equivalent substitution. See
   [event-processing.md](../architecture/event-processing.md) and
   [ADR 0005](../decisions/0005-cloud-neutral-architecture.md).
8. **Stream and object-store semantics are no longer exercised.** The deleted
   Kinesis, DynamoDB, and S3 adapters were the only place partitioned ordering,
   replay, and object-storage archival were tested. That coverage is genuinely
   gone and is not replaced by an equivalent test.
9. **Local measurements ≠ production measurements.** Sequential in-process
   latency/throughput figures are not equivalent to production distributed-system
   measurements and must not be presented as production performance.
10. **No infrastructure-as-code demonstration.** All Terraform configuration was
    removed, so the project can no longer demonstrate provisioned cloud
    infrastructure. Local Kubernetes deployment via Helm is unverified in CI
    because no cluster is available in the runner environment; the chart is
    validated by `helm lint` and `helm template` only.