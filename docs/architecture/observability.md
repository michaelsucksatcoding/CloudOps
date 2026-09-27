# Observability & Monitoring

CloudOps AI uses Prometheus for application metrics, Grafana for operational
visualization, and structured JSON logs to container stdout. This is
deliberately a small, reproducible monitoring stack for development and project
demonstrations; it does not perform autonomous remediation.

The platform targets no cloud provider, so there is no cloud log-aggregation
service and no cloud alarms. Collection is done from the container runtime or
from `kubectl logs` / `docker compose logs`.

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
| `cloudops_telemetry_events_failed_total` | Validation, ingestion, or storage failures. |
| `cloudops_anomalies_detected_total` | Isolation Forest predictions flagged anomalous. |
| `cloudops_ml_inference_duration_seconds` | Isolation Forest inference latency histogram. |
| `cloudops_ml_inference_total` | ML inference attempts by status. |
| `cloudops_service_health_score` | Current deterministic service health score from the API health-score view. |

## Logs and correlation

API and event-processor output is JSON to stdout with timestamp, level, service,
environment, event, request ID (when applicable), status, and duration.
`X-Request-ID` is accepted and returned by the API; otherwise a new ID is
generated. Raw telemetry payloads and configuration secrets are never included in
logs.

Collect from the local runtime:

```bash
docker compose logs -f api event-processor
kubectl logs -l app.kubernetes.io/part-of=cloudops-ai -n cloudops-dev -f
```

Because the logs are plain JSON on stdout, any container log shipper can ingest
them; the project does not bundle or require one.

## Helm monitoring stack

`infrastructure/kubernetes/helm/cloudops-ai` enables a single-replica
Prometheus and Grafana instance in `cloudops-monitoring`. Prometheus scrapes
the API service at `/metrics`; Grafana is provisioned with System Overview,
Kubernetes Workloads, and ML & Incidents dashboards.

Grafana's admin password is generated on first install and stored only in the
`cloudops-grafana-admin` Secret (monitoring namespace, key `password`); it is
never committed to source control. The chart reuses the existing Secret on
upgrade so the password stays stable (see
`templates/monitoring-grafana-secret.yaml`).

Then validate and install with the normal Helm workflow. Use port forwarding
for local access:

```bash
kubectl -n cloudops-monitoring port-forward service/cloudops-ai-prometheus 9090:9090
kubectl -n cloudops-monitoring port-forward service/cloudops-ai-grafana 3000:3000
```

The Kubernetes dashboard queries standard `kube-state-metrics` and kubelet
cAdvisor metric names. Deploy those standard exporters in your cluster before
treating those panels as data sources; the lightweight chart intentionally does
not add another exporter.

## Alerts

Prometheus evaluates alerts for high API error rate and P95 latency, telemetry
processing failures, degraded/critical service health, and high anomaly rate.
They identify incidents only; no alert triggers a rollback, restart, or other
remediation. Configure an Alertmanager receiver in the target environment when
notification delivery is required.

Seven alert rules are defined in
`infrastructure/kubernetes/monitoring/alerts/prometheus-rules.yaml` and are
mounted read-only into the Compose Prometheus container, so both runtimes
evaluate an identical rule set.

No notification delivery is verified by this repository: no Alertmanager is
deployed, so alert *evaluation* is verified but alert *delivery* is not.

## Simulator validation

Run a deterministic simulated incident (for example
`python -m scripts.simulate_incident --scenario latency_spike`) and submit its
events through `POST /events`. Observe request and pipeline counters at
`/metrics`, then inspect the Grafana overview and ML dashboards. Simulated data
must always be reported as **SIMULATED INCIDENT** and is useful for repeatable
monitoring validation, not production validation.
