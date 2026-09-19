# CloudOps AI

Cloud-Native Intelligent Operations Platform.

CloudOps AI is a Python-first platform for collecting application/infrastructure telemetry, processing it through an event-driven pipeline, detecting anomalous behaviour with machine learning, and exposing service health, analytics, incidents, and recommendations through an API/dashboard.

## Architecture

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
```

## Final-Year Project Status (2026-09-18)

CloudOps AI implements:

- Python/FastAPI application with Pydantic-validated telemetry ingestion
- ML anomaly detection with Isolation Forest
- Simulator-based controlled incident evaluation with reproducible results
- PostgreSQL persistence (SQLAlchemy + Alembic)
- Event-driven AWS architecture using Kinesis, Lambda, DynamoDB, and S3
- Kubernetes/EKS deployment with AWS ALB
- Prometheus/Grafana observability
- CI/CD, containerization, and Terraform infrastructure-as-code
- Automated quality gates (pytest, ruff, mypy)

### Verified deployment state (dev environment, EKS `cloudops-eks-dev`)

- EKS cluster and managed node group deployed; FastAPI API running (2 pods)
- PostgreSQL running; Alembic migration applied; PostgreSQL PVC bound
- AWS ALB provisioned with healthy targets; `/health/live` and `/health/ready`
  return HTTP 200 (readiness confirms database connectivity)
- Prometheus running and successfully scraping API metrics
- Grafana running with provisioned Prometheus datasource and 3 dashboards
- 6 Prometheus alert rules loaded (inactive during verification; no incident
  was active)
- EBS CSI addon active
- Terraform validation/plan and Helm lint/template succeeded

### Kinesis limitation

The event-driven telemetry architecture was implemented using Amazon Kinesis
Data Streams, AWS Lambda, Amazon DynamoDB, and Amazon S3. Live end-to-end
validation of this pipeline could not be performed because the AWS account
used for the experiment returned a `SubscriptionRequiredException` when
accessing Kinesis Data Streams. The restriction occurred at the AWS
account/service-access level before the Kinesis stream could be provisioned.

### Evaluation

The ML evaluation uses synthetic simulator ground truth. The fresh 2026-09-18
run reproduced the committed baseline's classification results exactly; the
detector achieves F1 = 0.8719 with a high false-positive rate of 0.88, a
documented negative result. See [docs/evaluation/](docs/evaluation/) for
methodology, results, reproducibility, and limitations.

This project is an academic final-year project artifact. It is **not**
production-ready, and synthetic simulator evaluation must not be described as
production validation.

---

## Quickstart & Local Development

### 1. Setup Virtual Environment

```bash
python -m venv .venv
```

**Windows PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 3. Run Quality Checks

```bash
ruff check . && ruff format --check . && mypy services && pytest
```

### 4. Run API Locally

```bash
uvicorn services.api.app.main:app --reload
```

### 5. Run Simulator

```bash
python -m services.simulator.telemetry
```

---

## Containerization & Docker

Build container images locally for each service target:

```bash
# Build FastAPI API image
docker build --target api -t cloudops-api:local .

# Build ML Service image
docker build --target ml -t cloudops-ml:local .

# Build Event Processor worker image
docker build --target event-processor -t cloudops-event-processor:local .
```

Run complete local multi-container stack with Docker Compose:

```bash
docker compose up --build
```

---

## Kubernetes & Helm Deployment

### 1. Dry-Run Validate Raw Manifests

```bash
kubectl apply --dry-run=client -f infrastructure/kubernetes/namespaces/
kubectl apply --dry-run=client -f infrastructure/kubernetes/deployments/
kubectl apply --dry-run=client -f infrastructure/kubernetes/services/
kubectl apply --dry-run=client -f infrastructure/kubernetes/ingress/
kubectl apply --dry-run=client -f infrastructure/kubernetes/network-policies/
```

### 2. Deploy Using Helm

```bash
# Lint Helm chart
helm lint infrastructure/kubernetes/helm/cloudops-ai

# Render templates locally
helm template cloudops-ai infrastructure/kubernetes/helm/cloudops-ai

# Install or upgrade on EKS
helm upgrade --install cloudops-ai infrastructure/kubernetes/helm/cloudops-ai \
  --namespace cloudops-dev \
  --create-namespace
```

---

## CI/CD & DevOps Automation

CloudOps AI uses dual GitHub Actions workflows with zero static AWS credentials (powered by AWS OIDC):

- **Continuous Integration (`.github/workflows/ci.yml`)**: Triggered on pull requests and pushes to `main`. Executes Ruff linter/formatter, Mypy, Pytest with coverage, PyPA `pip-audit` security scan, multi-stage Docker build caching, Trivy container security scans, Helm linting, and Terraform validation.
- **Continuous Deployment (`.github/workflows/cd.yml`)**: Triggered on push to `main` or manual release dispatch. Authenticates via AWS OIDC, pushes immutable Git SHA-tagged images to Amazon ECR, executes Helm release upgrades to Amazon EKS, verifies pod rollouts, and runs automated HTTP smoke tests.

### Run Local Smoke Tests

```bash
# Execute against a running local API or forwarded EKS cluster service
python scripts/smoke_test.py --base-url http://localhost:8000
```

### Run Dependency Security Audit

```bash
pip-audit --desc
```

Refer to [CI/CD Architecture](docs/architecture/cicd.md) and [ADR 0004](docs/decisions/0004-cicd-devops-automation.md) for detailed pipeline specifications.

---

## Infrastructure Provisioning (Terraform)

```bash
cd infrastructure/terraform/environments/dev

# Format check
terraform fmt -check -recursive

# Initialize modules
terraform init

# Validate configuration
terraform validate

# Plan infrastructure changes (never auto-apply in production)
terraform plan
```

Refer to [AGENTS.md](AGENTS.md) for master architecture documentation and rules of engagement.

## Observability

The API exposes Prometheus metrics at `GET /metrics` and returns an
`X-Request-ID` header for log correlation. The Helm chart includes a lightweight
Prometheus/Grafana stack and provisioned dashboards. See
[Observability & Monitoring](docs/architecture/observability.md) for metrics,
alerts, CloudWatch guidance, and local validation instructions.
