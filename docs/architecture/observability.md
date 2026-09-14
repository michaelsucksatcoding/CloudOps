# Observability & Monitoring

CloudOps AI uses Prometheus for application metrics, Grafana for operational
visualization, and structured JSON logs for container and AWS log collection.
This is deliberately a small, reproducible monitoring stack for development
and project demonstrations; it does not perform autonomous remediation.

## Application metrics

The API exposes Prometheus text format on `GET /metrics`. HTTP middleware adds
request count, latency histogram, active-request gauge, and error count. Route
labels are FastAPI route templates rather than raw URLs. Telemetry counters use
only bounded outcome/reason labels, so submitted service IDs, payloads, request
IDs, and timestamps do not create Prometheus time series.

| Metric | Meaning |
| --- | --- |
| `cloudops_http_requests_total` | Requests by method, route, and status. |
| `cloudops_http_request_duration_seconds` | Request latency histogram. |
| `cloudops_http_active_requests` | In-flight API requests. |
| `cloudops_http_errors_total` | 4xx, 5xx, and unhandled request errors. |
| `cloudops_telemetry_events_received_total` | Accepted telemetry events. |
| `cloudops_telemetry_events_processed_total` | Event-processor successes. |
| `cloudops_telemetry_events_failed_total` | Validation, stream, or storage failures. |
| `cloudops_anomalies_detected_total` | Isolation Forest predictions flagged anomalous. |
| `cloudops_ml_inference_duration_seconds` | Isolation Forest inference latency histogram. |
| `cloudops_ml_inference_total` | ML inference attempts by status. |
| `cloudops_service_health_score` | Current deterministic service health score from the API health-score view. |

## Logs and correlation

API and Lambda event-processor output is JSON to stdout with timestamp, level,
service, environment, event, request ID (when applicable), status, and
duration. `X-Request-ID` is accepted and returned by the API; otherwise a new
ID is generated. Raw telemetry payloads and configuration secrets are never
included in logs. In EKS, configure the standard CloudWatch Container Insights
agent or Fluent Bit integration to collect container stdout into CloudWatch
Logs.

## Helm monitoring stack

`infrastructure/kubernetes/helm/cloudops-ai` enables a single-replica
Prometheus and Grafana instance in `cloudops-monitoring`. Prometheus scrapes
the API service at `/metrics`; Grafana is provisioned with System Overview,
Kubernetes Workloads, and ML & Incidents dashboards.

Before an install, create a Grafana password secret outside source control:

```bash
kubectl -n cloudops-monitoring create secret generic cloudops-grafana-admin \
  --from-literal=password='<choose-a-strong-password>'
```

Then validate and install with the normal Helm workflow. Use port forwarding
for local access:

```bash
kubectl -n cloudops-monitoring port-forward service/cloudops-ai-prometheus 9090:9090
kubectl -n cloudops-monitoring port-forward service/cloudops-ai-grafana 3000:3000
```

The Kubernetes dashboard queries standard `kube-state-metrics` and kubelet
cAdvisor metric names. Enable the managed EKS observability add-on or deploy
those standard exporters in the cluster before treating those panels as data
sources; the lightweight chart intentionally does not add another exporter.

## Alerts and CloudWatch

Prometheus evaluates alerts for high API error rate and P95 latency, telemetry
processing failures, degraded/critical service health, and high anomaly rate.
They identify incidents only; no alert triggers a rollback, restart, or other
remediation. Configure an Alertmanager receiver in the target environment when
notification delivery is required.

CloudWatch uses native AWS service metrics rather than duplicate application
metrics. The operational runbook should monitor Lambda invocations/errors/
duration, Kinesis iterator age, DynamoDB throttles, RDS CPU and connections,
SQS queue depth when provisioned, and EKS cluster health. No CloudWatch alarms
are provisioned by this repository because the corresponding AWS resources and
notification destination are environment-owned; alarm thresholds and SNS
recipients require the project owner's approval.

## Simulator validation

Run a deterministic simulated incident (for example
`python -m scripts.simulate_incident --scenario latency_spike`) and submit its
events through `POST /events`. Observe request and pipeline counters at
`/metrics`, then inspect the Grafana overview and ML dashboards. Simulated data
must always be reported as **SIMULATED INCIDENT** and is useful for repeatable
monitoring validation, not production validation.
