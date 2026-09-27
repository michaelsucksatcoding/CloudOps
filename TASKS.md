# CloudOps AI Development Roadmap

> **FYP documentation freeze — 2026-09-18.** The implementation and evaluation
> are complete and frozen for the final-year project submission. No further
> implementation is planned. Remaining unchecked items below are deliberately
> out of the FYP scope and recorded as future work only.

## Phase 1 — Foundation
- [x] FastAPI application
- [x] PostgreSQL
- [x] SQLAlchemy
- [x] Alembic
- [x] Docker Compose
- [x] Unit tests

## Phase 2 — Event Processing
- [x] Telemetry schema
- [x] In-process telemetry producer
- [x] PostgreSQL-backed event-processing worker
- [x] Hot storage routing

## Phase 3 — Analytics
- [x] Partitioned data-lake records
- [x] Parquet
- [x] Analytics pipeline
- [x] Feature engineering

## Phase 4 — Machine Learning
- [x] Dataset generation
- [x] Isolation Forest
- [x] Model training
- [x] Evaluation
- [x] Health scoring

## Phase 5 — Kubernetes
- [x] Docker images (multi-target: `api`, `ml`, `event-processor`)
- [x] Helm chart with cloud-neutral default values
- [x] HPA
- [x] NetworkPolicy
- [x] `helm lint` / `helm template` validation in CI

## Phase 6 — DevOps
- [x] GitHub Actions
- [x] Automated tests
- [x] Image scanning
- [x] Container build validation

## Phase 7 — Observability
- [x] Prometheus application metrics and in-cluster scraper configuration
- [x] Grafana provisioned dashboards (system, Kubernetes, ML/incidents)
- [x] Structured JSON logs, request correlation, and basic Prometheus alerts
- [x] Local Compose verification: Prometheus scrapes API metrics; 7 alert rules
      loaded (inactive during verification); Grafana datasource + 3 dashboards
      provisioned
- [x] Removed the cloud architecture (Terraform, managed stream/serverless
      consumer, object stores, CD workflow) — see
      [ADR 0005](docs/decisions/0005-cloud-neutral-architecture.md)
- [ ] Deploy an Alertmanager and verify alert *delivery* (evaluation only is
      verified; out of FYP scope)

## Phase 8 — Evaluation
- [x] Local simulator-ground-truth detection evaluation
- [x] Local ML inference and in-memory pipeline latency measurement
- [x] Local sequential API latency and throughput measurement
- [x] Reproducibility: 2026-09-18 run reproduced 2026-09-14 classification
      results exactly
- [ ] Load testing (future work; not part of FYP evaluation)
- [ ] Live Helm deployment to a local cluster (chart is lint/template-validated
      only; no cluster available in CI)
- [ ] Durable fan-out if measured throughput becomes a constraint — see
      [event-processing.md](docs/architecture/event-processing.md)
