# CloudOps AI Development Roadmap

## Phase 1 — Foundation
- [x] FastAPI application
- [x] PostgreSQL
- [x] SQLAlchemy
- [x] Alembic
- [x] Docker Compose
- [x] Unit tests

## Phase 2 — Event Processing
- [x] Telemetry schema
- [x] Kinesis producer
- [x] Lambda processor
- [x] DynamoDB realtime metrics

## Phase 3 — Analytics
- [x] S3 data lake
- [x] Parquet
- [x] PySpark pipeline
- [x] Feature engineering

## Phase 4 — Machine Learning
- [x] Dataset generation
- [x] Isolation Forest
- [x] Model training
- [x] Evaluation
- [x] Health scoring

## Phase 5 — Kubernetes
- [x] Docker images
- [x] ECR
- [x] EKS
- [x] Helm
- [x] HPA
- [x] NetworkPolicy

## Phase 6 — DevOps
- [x] GitHub Actions
- [x] Automated tests
- [x] Image scanning
- [x] Deployment

## Phase 7 — Observability
- [x] Prometheus application metrics and in-cluster scraper configuration
- [x] Grafana provisioned dashboards (system, Kubernetes, ML/incidents)
- [x] Structured JSON logs, request correlation, and basic Prometheus alerts
- [ ] Provision CloudWatch alarms/dashboards after the AWS resource inventory and
      approved notification target are available (monitoring runbook documented)

## Phase 8 — Evaluation
- [x] Local simulator-ground-truth detection evaluation
- [x] Local ML inference and in-memory pipeline latency measurement
- [x] Local sequential API latency and throughput measurement
- [ ] Load testing
- [ ] Kubernetes resource utilization and HPA scale-out evaluation
