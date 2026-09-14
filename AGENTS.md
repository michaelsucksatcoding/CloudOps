# AGENTS.md — CloudOps AI

## 1. Project Identity

**Project:** CloudOps AI  
**Type:** Final-Year Project / Cloud-Native Intelligent Operations Platform

CloudOps AI is a Python-first platform for collecting application/infrastructure telemetry, processing it through an event-driven pipeline, detecting anomalous behaviour with machine learning, and exposing service health, analytics, incidents, and recommendations through an API/dashboard.

### Primary research focus

> Can a cloud-native, event-driven Python platform use machine learning to detect abnormal application/infrastructure behaviour and provide actionable incident insights?

The project must prioritize **measurable ML results, reliable data processing, clean software engineering, and reproducible deployment** over simply using many cloud services.

---

# 2. Core Architecture

```text
Applications / Simulator
        │
        ▼
   FastAPI / Events
        │
        ▼
     Kinesis
        │
        ▼
      Lambda
      /    \
     ▼      ▼
 DynamoDB   S3
  hot data  data lake
              │
              ▼
          PySpark / ETL
              │
              ▼
       Analytics Database

Telemetry
   │
   ▼
ML Pipeline
   ├── anomaly detection
   ├── service health scoring
   └── optional incident prediction
              │
              ▼
       FastAPI API
              │
              ▼
       Dashboard / Alerts

GitHub
   │
   ▼
GitHub Actions
   │
   ▼
Docker → ECR → EKS
```

### Architecture principles

- Python is the primary implementation language.
- APIs use FastAPI.
- Events use an event-driven architecture.
- Hot/realtime data and historical/cold data are separate.
- ML must operate on measurable telemetry features.
- Infrastructure must be reproducible with Terraform.
- Production-like deployment uses Docker + Kubernetes.
- CI/CD must automatically test and validate code.
- Every major infrastructure component must have a documented purpose.

Do **not** add AWS services merely to make the architecture look impressive.

---

# 3. Core Technology Stack

## Application

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis where caching is demonstrably useful
- boto3

## Data / Analytics

- Pandas
- PyArrow
- PySpark
- S3
- DynamoDB
- Amazon Kinesis
- SQL

## Machine Learning

- scikit-learn
- Isolation Forest as the initial anomaly-detection baseline
- Random Forest / XGBoost only when justified experimentally
- NumPy
- ML models must be versioned and reproducible

## Infrastructure

- AWS
- Terraform
- Docker
- Kubernetes
- Amazon EKS
- Helm
- ECR
- ALB
- Kubernetes NetworkPolicy
- AWS Secrets Manager

## Events / Operations

- Kinesis
- Lambda
- EventBridge
- SQS
- SNS
- CloudWatch

## Observability

- Prometheus
- Grafana
- CloudWatch
- OpenTelemetry when useful

## Development / Quality

- GitHub
- GitHub Actions
- pytest
- Ruff
- mypy
- httpx
- Docker Compose for local development

---

# 4. Repository Architecture

```text
cloudops-ai/
│
├── services/
│   ├── api/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── dependencies.py
│   │   │   │
│   │   │   ├── routes/
│   │   │   │   ├── health.py
│   │   │   │   ├── services.py
│   │   │   │   ├── metrics.py
│   │   │   │   ├── incidents.py
│   │   │   │   ├── analytics.py
│   │   │   │   └── ml.py
│   │   │   │
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── repositories/
│   │   │   └── services/
│   │   └── tests/
│   │
│   ├── event_processor/
│   │   ├── handler.py
│   │   ├── processor.py
│   │   └── tests/
│   │
│   ├── analytics/
│   │   ├── pipeline.py
│   │   ├── feature_engineering.py
│   │   ├── queries.py
│   │   └── tests/
│   │
│   ├── ml/
│   │   ├── anomaly_detection.py
│   │   ├── health_scoring.py
│   │   ├── incident_prediction.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   ├── models/
│   │   └── tests/
│   │
│   └── simulator/
│       ├── telemetry.py
│       ├── incidents.py
│       └── tests/
│
├── infrastructure/
│   ├── terraform/
│   │   ├── modules/
│   │   │   ├── networking/
│   │   │   ├── eks/
│   │   │   ├── rds/
│   │   │   ├── ecr/
│   │   │   ├── kinesis/
│   │   │   ├── lambda/
│   │   │   └── monitoring/
│   │   │
│   │   └── environments/
│   │       ├── dev/
│   │       └── prod/
│   │
│   └── kubernetes/
│       ├── namespaces/
│       ├── deployments/
│       ├── services/
│       ├── ingress/
│       ├── network-policies/
│       └── helm/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
│
├── notebooks/
│   ├── exploration/
│   └── experiments/
│
├── tests/
│   ├── integration/
│   └── e2e/
│
├── scripts/
│   ├── seed_data.py
│   ├── generate_telemetry.py
│   └── simulate_incident.py
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── experiments/
│   └── decisions/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── Makefile
├── README.md
└── AGENTS.md
```

Keep domain logic in `services/`.  
Keep deployment/infrastructure code in `infrastructure/`.  
Do not mix Terraform, Kubernetes manifests, and Python application code.

---

# 5. Required API Surface

The API should evolve around these concepts:

```text
GET  /health
GET  /services
GET  /services/{service_id}/health
GET  /metrics
GET  /incidents
GET  /incidents/{incident_id}
GET  /analytics/errors
GET  /analytics/latency
GET  /analytics/traffic
GET  /ml/anomalies
GET  /ml/health-scores
POST /events
```

Use Pydantic schemas for request/response validation.

Do not expose database models directly from API endpoints.

---

# 6. Telemetry Contract

The canonical telemetry event should contain fields similar to:

```json
{
  "timestamp": "2026-09-02T15:20:32Z",
  "service": "payment-api",
  "endpoint": "/api/payment",
  "status_code": 500,
  "latency_ms": 1832,
  "cpu_percent": 81.4,
  "memory_percent": 74.2
}
```

Additional fields may be added when justified:

- request rate
- queue depth
- deployment version
- instance ID
- environment
- tenant ID
- region

Telemetry schemas must be versionable.

Invalid events must be rejected or routed to an appropriate failure path. Never silently corrupt data.

---

# 7. Machine Learning Rules

The ML component is a core FYP contribution.

### Initial implementation

Start with:

```text
Telemetry
   ↓
Feature engineering
   ↓
Isolation Forest
   ↓
Anomaly score
   ↓
Service health score
```

Possible features:

- CPU utilization
- memory utilization
- latency
- request rate
- error rate
- HTTP 5xx rate
- queue depth
- recent deployment indicator

### Evaluation

Every ML change must preserve an evaluation path.

Measure appropriate metrics such as:

- precision
- recall
- F1
- false-positive rate
- detection latency
- inference latency

Use controlled simulated incidents to create reproducible evaluation scenarios.

Do not claim that a model "predicts incidents" unless the implementation and experimental methodology actually support that claim.

---

# 8. Incident Simulator

The simulator is an important testing and demonstration component.

It should support scenarios such as:

```text
normal
cpu_spike
memory_pressure
latency_spike
error_spike
database_failure
queue_backlog
deployment_regression
```

Each scenario should generate deterministic/reproducible telemetry when given a seed.

The simulator must not be treated as production telemetry.

Clearly distinguish:

```text
SIMULATED INCIDENT
```

from real infrastructure events.

---

# 9. Exact Development Commands

All developers and coding agents must use the project's standard commands.

## Create environment

```bash
python -m venv .venv
```

### Linux/macOS

```bash
source .venv/bin/activate
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

## Install dependencies

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Run API locally

```bash
uvicorn services.api.app.main:app --reload
```

## Run tests

```bash
pytest
```

## Run tests with coverage

```bash
pytest --cov=services --cov-report=term-missing
```

## Lint

```bash
ruff check .
```

## Format

```bash
ruff format .
```

## Type checking

```bash
mypy services
```

## Run all quality checks

```bash
ruff check . && ruff format --check . && mypy services && pytest
```

## Run local infrastructure

```bash
docker compose up --build
```

Stop it with:

```bash
docker compose down
```

## Build Docker image

```bash
docker build -t cloudops-ai:local .
```

## Run simulator

```bash
python -m services.simulator.telemetry
```

## Simulate an incident

```bash
python -m scripts.simulate_incident --scenario latency_spike
```

## Train ML model

```bash
python -m services.ml.train
```

## Evaluate ML model

```bash
python -m services.ml.evaluate
```

## Terraform

From the appropriate environment directory:

```bash
terraform fmt -recursive
terraform init
terraform validate
terraform plan
```

Never run `terraform apply` automatically.

## Kubernetes

```bash
kubectl cluster-info
kubectl get pods -A
helm lint infrastructure/kubernetes/helm/cloudops-ai
```

Deployment must be explicitly requested or performed through the approved CI/CD workflow.

---

# 10. Coding Standards

- Follow PEP 8.
- Use type hints throughout application code.
- Prefer small, testable functions.
- Use dependency injection for external services.
- Keep business logic independent from AWS-specific code where practical.
- Use async code only where it provides a real benefit.
- Validate all external input.
- Use structured logging.
- Never swallow exceptions silently.
- Never commit credentials, tokens, API keys, or private certificates.
- Configuration belongs in environment variables or secret management.
- Database migrations must use Alembic.
- Public APIs must have explicit Pydantic schemas.
- Avoid global mutable state.
- Add tests for meaningful behaviour, not trivial line coverage.

---

# 11. Rules of Engagement

## MUST

1. **Read existing code before modifying it.**
2. Preserve existing behaviour unless the task explicitly requires a breaking change.
3. Run relevant tests after every substantive change.
4. Run lint/type checks before considering a task complete.
5. Update documentation when architecture or public behaviour changes.
6. Add or update tests for new functionality.
7. Prefer the simplest implementation that satisfies the requirement.
8. Keep ML experiments reproducible with fixed seeds/configuration where appropriate.
9. Record important architectural decisions in `docs/decisions/`.
10. Keep cloud resources identifiable and easy to destroy to control FYP costs.

## MUST NOT

1. Do not introduce a new framework when an existing dependency already solves the problem.
2. Do not add AWS services without a documented architectural reason.
3. Do not replace FastAPI with Flask/Django/etc. without an explicit project decision.
4. Do not introduce microservices merely for architectural appearance.
5. Do not introduce LLMs, agents, deep learning, or complex MLOps tooling unless explicitly approved.
6. Do not implement multi-region disaster recovery before the core system works.
7. Do not hardcode AWS credentials or database passwords.
8. Do not commit `.env`, secret files, Terraform state, model secrets, or credentials.
9. Do not execute destructive AWS/Terraform commands automatically.
10. Do not make architectural changes unrelated to the current task.
11. Do not silently modify research methodology or evaluation metrics.
12. Do not fabricate ML performance results.
13. Do not treat simulated incidents as real-world validation.
14. Do not optimize prematurely.
15. Do not remove tests simply because they are inconvenient.

---

# 12. Scope Control

The project has three priority levels.

### P0 — Required

- Python/FastAPI API
- telemetry ingestion
- event processing
- PostgreSQL
- Kinesis/Lambda architecture
- S3 data lake
- analytics pipeline
- anomaly detection
- incident simulator
- automated tests
- Docker
- Terraform
- Kubernetes/EKS deployment
- CI/CD
- basic observability

### P1 — Strong additions

- service health scoring
- multi-tenancy
- Redis caching
- Prometheus/Grafana
- SQS/SNS alerting
- deployment-regression detection
- ML model comparison

### P2 — Optional / Future Work

- multi-region DR
- advanced incident prediction
- automated rollback
- cost forecasting
- sophisticated LLM/AI assistant
- complex distributed tracing
- advanced model-serving infrastructure

If P0 functionality is incomplete, **do not work on P2 features.**

---

# 13. Security Boundaries

Treat all external input as untrusted.

Required practices:

- environment-based configuration
- AWS IAM least privilege
- Kubernetes secrets
- AWS Secrets Manager for production secrets
- private database access where appropriate
- NetworkPolicies for Kubernetes workloads
- input validation
- dependency/security scanning in CI
- no credentials in source control

Never print secrets in logs.

Never expose internal infrastructure credentials through API responses.

---

# 14. Testing Strategy

Testing should exist at four levels.

```text
Unit
  ↓
Integration
  ↓
End-to-End
  ↓
ML Evaluation
```

### Unit tests

Test:

- telemetry validation
- feature engineering
- anomaly detection
- health scoring
- API services
- repositories

### Integration tests

Test:

- API ↔ database
- event processor ↔ storage
- analytics pipeline
- AWS adapters where practical

### E2E tests

Test:

```text
telemetry
   ↓
event processing
   ↓
storage
   ↓
ML
   ↓
API
```

### ML evaluation

Every model experiment must record:

- dataset/version
- features
- algorithm
- hyperparameters
- random seed
- evaluation metrics

---

# 15. CI/CD Contract

Every pull request should perform:

```text
checkout
   ↓
install dependencies
   ↓
ruff check
   ↓
ruff format --check
   ↓
mypy
   ↓
pytest
   ↓
security/dependency scan
```

After approved merge:

```text
test
 ↓
Docker build
 ↓
image scan
 ↓
ECR push
 ↓
deployment
 ↓
smoke test
```

Deployment failures must not be silently ignored.

Production deployment must require an explicit approval mechanism.

---

# 16. Definition of Done

A task is **not complete** merely because the code compiles.

A feature is complete when:

- implementation exists
- relevant tests exist
- tests pass
- lint passes
- type checking passes where applicable
- documentation is updated where necessary
- configuration is reproducible
- security implications have been considered
- no unrelated files were modified
- the change fits the existing architecture

For ML functionality, "done" additionally requires:

- reproducible experiment
- evaluation dataset
- measurable metrics
- documented methodology
- no fabricated results

---

# 17. Agent Behaviour

Act as a **senior Python/cloud engineer assisting with a final-year research project**.

Before implementing:

1. Understand the current architecture.
2. Identify the smallest change satisfying the request.
3. Check existing abstractions and tests.
4. State important assumptions when they affect design.
5. Implement incrementally.

After implementing:

1. Run tests.
2. Run lint/type checks.
3. Inspect the resulting diff.
4. Remove unnecessary complexity.
5. Report exactly what changed and what was verified.

When uncertain between a simple and complex solution, choose the **simpler solution** unless the project requirements or measured evidence justify the complexity.

The agent's primary objective is:

> **Build a reliable, measurable, academically defensible CloudOps AI system—not an unnecessarily complicated cloud architecture.**

## Agent Decision Boundary

The human developer owns architectural and research decisions.

The agent may:
- implement approved designs
- refactor existing code
- write tests
- fix bugs
- improve documentation
- suggest architectural improvements

The agent must ask for confirmation before:
- changing the primary technology stack
- adding a major AWS service
- changing the ML methodology
- changing database architecture
- introducing a new microservice
- changing public API contracts
- modifying research objectives
- deleting substantial functionality
- performing destructive infrastructure operations
- changing Terraform production resources

When multiple valid implementations exist, prefer the simplest one
and explain the trade-off before making a major architectural decision.