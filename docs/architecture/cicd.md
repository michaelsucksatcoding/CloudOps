# CI/CD & DevOps Automation Architecture — CloudOps AI

This document details the design, configuration, security model, and execution lifecycle of the CloudOps AI continuous integration and deployment pipelines.

---

## 1. End-to-End Delivery Lifecycle

```text
               Developer
                   │
                   ▼
         Git Push / Pull Request
                   │
                   ▼
     GitHub Actions Workflow: CI
     ┌─────────────────────────────────────────────────────────────┐
     │ 1. Python 3.12 Runtime Setup & Pip Cache                    │
     │ 2. Code Quality Gates:                                      │
     │    ├── Ruff Linter (PEP8, imports, best practices)          │
     │    ├── Ruff Formatter Check                                 │
     │    └── Mypy Static Type Checking                            │
     │ 3. Automated Test Suite:                                    │
     │    └── Pytest with Coverage Matrix                          │
     │ 4. Dependency Security Audit:                               │
     │    └── PyPA pip-audit (Vulnerability database scan)         │
     │ 5. Multi-Stage Docker Builds:                               │
     │    ├── cloudops-api                                         │
     │    ├── cloudops-ml                                          │
     │    └── cloudops-event-processor                             │
     │ 6. Container Image Security Scan:                           │
     │    └── Trivy (CRITICAL / HIGH OS & Library CVE scan)        │
     │ 7. Infrastructure Dry-Run Validation:                       │
     │    ├── Helm Lint & Template Render                          │
     │    └── Terraform Format Check & Dev Config Validation       │
     └─────────────────────────────────────────────────────────────┘
                   │
              (Merge to main)
                   │
                   ▼
     GitHub Actions Workflow: CD
     ┌─────────────────────────────────────────────────────────────┐
     │ 1. Short-Lived AWS Authentication via OpenID Connect (OIDC) │
     │ 2. Authenticate Docker with Amazon ECR                      │
     │ 3. Build & Push Multi-Stage Images:                         │
     │    ├── <ecr-registry>/cloudops-api:<git-sha>                │
     │    ├── <ecr-registry>/cloudops-ml:<git-sha>                 │
     │    └── <ecr-registry>/cloudops-event-processor:<git-sha>    │
     │ 4. Update Target EKS Kubeconfig via AWS CLI                 │
     │ 5. Automated Helm Upgrade/Install:                          │
     │    └── Injects immutable Git SHA tags into EKS release      │
     │ 6. Post-Deployment Verification:                            │
     │    ├── kubectl rollout status (API, ML, Event-Processor)    │
     │    └── Automated HTTP Smoke Test (/health/live, /health)    │
     └─────────────────────────────────────────────────────────────┘
                   │
                   ▼
          Running EKS Cluster
```

---

## 2. CI Workflow (`.github/workflows/ci.yml`)

The CI workflow runs on every pull request targeting `main`, pushes to `main`, and manual dispatches.

### Quality & Security Gates
1. **Ruff Lint & Format**: Validates syntax, imports order (`I`), flake8 bug prevention (`B`), and enforces black-compatible formatting.
2. **Mypy Strict Analysis**: Enforces comprehensive type coverage on `services/`.
3. **Pytest & Coverage**: Executes unit, integration, and e2e test suites.
4. **Dependency Audit (`pip-audit`)**: Scans all installed packages against the PyPA Advisory Database and OSV.
5. **Docker Buildx Caching**: Tests container image builds across `api`, `ml`, and `event-processor` build targets.
6. **Container Security Scan (`trivy`)**: Scans the compiled image filesystem for operating system and library CVEs.
7. **Infrastructure Linter**: Runs `helm lint` and `terraform fmt -check` to detect infrastructure regressions before merge.

---

## 3. CD Workflow (`.github/workflows/cd.yml`)

The CD workflow deploys exclusively from the `main` branch or via authorized manual dispatches with environment targeting (`dev` / `prod`).

### Key Operational Characteristics
- **Concurrency Management**: Configured with `cancel-in-progress: false` to ensure in-flight deployments are never abruptly terminated.
- **Traceable Immutable Tagging**: Images are tagged with the full Git commit SHA (`${{ github.sha }}`) ensuring every container running in EKS is 100% traceable to source code.
- **Fail-Safe Rollout**: Deploys using Helm's `--wait` and validates pod readiness using `kubectl rollout status` with a strict timeout.

---

## 4. AWS OIDC Authentication & IAM Least Privilege

The pipeline uses **AWS IAM OpenID Connect (OIDC)** identity federation, completely eliminating long-lived AWS Access Keys and Secret Keys from GitHub repository secrets.

### GitHub Actions Permissions
```yaml
permissions:
  contents: read
  id-token: write # Required for requesting short-lived AWS OIDC token
```

### IAM Role Trust Policy Template
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:<GITHUB_ORG_OR_USER>/cloudops-ai:*"
        }
      }
    }
  ]
}
```

### IAM Permissions Policy (Least Privilege)
The deployment role requires permissions only for ECR push, EKS cluster description, and token acquisition:
- `ecr:GetAuthorizationToken`
- `ecr:BatchCheckLayerAvailability`, `ecr:GetDownloadUrlForLayer`, `ecr:BatchGetImage`, `ecr:PutImage`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`
- `eks:DescribeCluster`

---

## 5. Required GitHub Configuration

### Repository Secrets
| Secret Name | Description | Example |
|---|---|---|
| `AWS_ROLE_ARN` | ARN of the IAM Role assumed via OIDC | `arn:aws:iam::123456789012:role/cloudops-github-deploy-role` |
| `AWS_REGION` | Target AWS Region | `us-east-1` |
| `EKS_CLUSTER_NAME` | Name of the Amazon EKS cluster | `cloudops-eks-dev` |

---

## 6. Post-Deployment Verification & Smoke Testing

After Helm applies changes to EKS, the workflow executes automated verification:
1. `kubectl rollout status` monitors pod deployment progression.
2. `scripts/smoke_test.py` validates:
   - `/health/live` — Ensures the process is running and responding.
   - `/health/ready` — Ensures database connectivity is established.
   - `/health` — Validates system health diagnostic payload.
   - `/services` — Ensures metadata catalog is queryable.
   - `/metrics` — Verifies metrics endpoint accessibility.

---

## 7. Troubleshooting & Failure Recovery

- **CI Failure on `pip-audit`**: Upgrade vulnerable sub-dependencies in `pyproject.toml` or add an explicitly reviewed vulnerability exception.
- **CD Rollout Timeout**: Check Kubernetes events with `kubectl describe deployment cloudops-ai-api -n cloudops-dev` and pod logs with `kubectl logs -l app.kubernetes.io/component=api -n cloudops-dev`.
- **OIDC STS Token Denial**: Verify the repository name in the IAM role trust policy `sub` condition matches the GitHub repository path exactly.
