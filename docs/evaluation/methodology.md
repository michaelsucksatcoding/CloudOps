# Evaluation Methodology

The local evaluation uses Isolation Forest trained by `services.ml.train` on
1,000 seeded synthetic normal samples (seed 42; contamination 0.02). Test
events are produced by the deterministic simulator with seed 20260914: 100
normal events and 100 events for each supported incident scenario. Simulator
scenario membership supplies synthetic ground truth only.

The evaluation reports confusion-matrix counts, precision, recall, F1, false
positive rate, false negative rate, and model inference time. It also measures
in-memory event validation/routing latency over 100 calls and sequential
in-process API liveness requests at 50, 200, and 500 requests. Monotonic
`perf_counter` is used within each process, avoiding mixed wall clocks.

This does not measure Kinesis, Lambda, S3, DynamoDB, network transport,
Grafana rendering, Prometheus alert delivery, CloudWatch, or EKS HPA timing.
