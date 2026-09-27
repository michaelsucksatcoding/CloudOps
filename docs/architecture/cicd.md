# CI & DevOps Automation Architecture — CloudOps AI

This document details the design, configuration, and security model of the CloudOps AI continuous integration pipeline.

The project has **no continuous deployment**. There is no cloud account, no container registry, and no managed cluster. Releases are run manually from a local machine. See
[ADR 0005](../decisions/0005-cloud-neutral-architecture.md).

---

## 1. End-to-End Lifecycle

```text
               Developer
                   │
                   ▼
         Git Push / Pull Request
                   │
                   ▼
       GitHub Actions Workflow: ci.yml
       ┌─────────────────────────────────────────────────────────────┐
       │ 1. Python 3.12 Runtime Setup & Pip Cache                    │
       │ 2. Code Quality Gates:                                      │
       │    ├── Ruff Linter                                         │
       │    ├── Ruff Formatter Check                                │
       │    └── Mypy Strict Type Checking                           │
       │ 3. Automated Test Suite:                                    │
       │    └── Pytest with Coverage                                │
       │ 4. Dependency Security Audit:                               │
       │    └── PyPA pip-audit (Vulnerability database scan)         │
       │ 5. Helm Chart Validation:                                   │
       │    ├── helm lint                                           │
       │    ├── helm template (default values)                      │
       │    └── cloud-neutral render guard                          │
       │ 6. Local Runtime Validation:                                │
       │    ├── docker compose config --quiet                       │
       │    ├── no-cloud-SDK guard (boto3/botocore must be absent)  │
       │    ├── PostgreSQL healthy                                  │
       │    ├── API /health reachable                               │
       │    └── ML evaluation job completes                         │
       │ 7. Multi-Stage Docker Builds + Trivy Image Scan             │
       └─────────────────────────────────────────────────────────────┘
                   │
          (merge to main)
                   │
                   ▼
      Local machine: docker compose up --build
      (primary runtime, or helm upgrade to a local cluster)
```

---

## 2. CI Workflow (`.github/workflows/ci.yml`)

The CI workflow runs on every pull request targeting `main`, pushes to `main`, and manual dispatches. It requires **no secrets, no credentials, and no external accounts**.

### Job: `python-quality-and-tests`

1. **Ruff Lint & Format** — validates syntax, import order (`I`), flake8-bugbear
   rules (`B`), pyupgrade rules (`UP`), and formatting.
2. **Mypy Strict Analysis** — enforces type coverage on `services/`.
3. **Pytest & Coverage** — executes unit and integration suites with a coverage
   report.
4. **Dependency Audit (`pip-audit`)** — scans installed packages against the PyPA
   Advisory Database and OSV.

### Job: `helm-manifest-validation`

1. **`helm lint`** — chart structure and template validity.
2. **`helm template`** — renders the chart with the canonical default values.
3. **Cloud-neutral guard** — fails the job if the rendered output contains a
   cloud-provider-specific dependency:

   ```bash
   grep -Eqi 'amazonaws\.com|eks\.amazonaws|ingressClassName: alb|storageClassName: gp2'
   ```

   The guard intentionally names the patterns it forbids. It is an assertion of
   absence, not a configuration.

### Job: `local-runtime-validation`

Validates the primary runtime on the runner.

1. **`docker compose config --quiet`** — the Compose file is well-formed.
2. **No-cloud-SDK guard** — fails if `boto3` or `botocore` is installed. These
   were removed with the cloud architecture; this prevents the coupling from
   returning unnoticed.
3. **PostgreSQL** — starts and waits for the `pg_isready` healthcheck.
4. **API** — starts the API (which runs `alembic upgrade head`) and waits for
   `/health`.
5. **ML evaluation** — runs the one-shot ML container to confirm the evaluation
   path executes end to end.

### Job: `docker-build-and-scan`

Builds all three image targets (`api`, `ml`, `event-processor`) with buildx
GitHub Actions layer caching, then scans the API image with Trivy for
CRITICAL/HIGH OS and library CVEs.

---

## 3. Permissions

```yaml
permissions:
  contents: read
```

Read-only repository access. No `id-token` write permission is requested,
because there is no OIDC exchange and no external system to authenticate to.

---

## 4. Required GitHub Configuration

**None.** The pipeline has no repository secrets and no environment variables.
It runs unmodified on a default `ubuntu-latest` runner.

---

## 5. Deployment (Manual, Local)

Deployment is deliberately not automated. From a local machine:

### Docker Compose (primary)

```bash
docker compose up --build
curl http://localhost:8000/health
```

### Helm to a local cluster (secondary)

```bash
kubectl apply -f infrastructure/kubernetes/namespaces/
helm upgrade --install cloudops-ai infrastructure/kubernetes/helm/cloudops-ai \
  --namespace cloudops-dev --create-namespace
kubectl exec -n cloudops-dev deploy/cloudops-ai-api -- alembic upgrade head
kubectl port-forward -n cloudops-dev svc/cloudops-ai-api 8000:8000
```

### Smoke testing a running instance

```bash
python scripts/smoke_test.py --base-url http://localhost:8000
```

`smoke_test.py` validates `/health/live`, `/health/ready`, `/health`,
`/services`, and `/metrics`.

---

## 6. Troubleshooting

- **`pip-audit` failure** — upgrade the vulnerable sub-dependency in
  `pyproject.toml` or add an explicitly reviewed exception.
- **Cloud-neutral guard failure** — a template or value reintroduced a
  cloud-specific dependency. Remove it; do not widen the guard.
- **No-cloud-SDK guard failure** — something re-added `boto3` or `botocore` to the
  dependency set. This must be reverted, not bypassed.
- **PostgreSQL/API never healthy in CI** — inspect `docker compose logs` output
  printed by the failing step.
- **Local Kubernetes pod not ready** — check
  `kubectl describe deployment cloudops-ai-api -n cloudops-dev` and
  `kubectl logs -l app.kubernetes.io/component=api -n cloudops-dev`. Migrations
  are not run automatically; run `alembic upgrade head` manually.
