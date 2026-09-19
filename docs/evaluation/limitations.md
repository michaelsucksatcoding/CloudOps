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
6. **No AWS-path timing.** Pipeline and API measurements are local/in-memory and
   exclude Kinesis, Lambda, S3, DynamoDB, network transport, Grafana rendering,
   Prometheus alert delivery, CloudWatch, and EKS HPA timing.
7. **Kinesis service-access restriction.** The AWS account returned
   `SubscriptionRequiredException` when accessing Amazon Kinesis Data Streams;
   the Kinesis stream could not be provisioned and the live
   Kinesis → Lambda → DynamoDB/S3 path was not experimentally validated.
8. **Local measurements ≠ production measurements.** Sequential in-process
   latency/throughput figures are not equivalent to production distributed-system
   measurements and must not be presented as production performance.