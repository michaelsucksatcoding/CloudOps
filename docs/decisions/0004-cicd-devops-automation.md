# ADR 0004: CI/CD & DevOps Automation Architecture

## Status
Accepted

## Context
Phase 6 of CloudOps AI requires establishing an automated, secure, and reproducible Continuous Integration and Continuous Deployment (CI/CD) pipeline for application code, container packaging, and Kubernetes deployment while strictly adhering to the architectural boundaries defined in `AGENTS.md`.

## Decisions

1. **GitHub Actions Native Orchestration**:
   - Selected GitHub Actions for CI/CD over third-party external orchestrators (e.g. Jenkins, ArgoCD, Flux) to maintain a lightweight, cloud-native developer workflow without extra infrastructure overhead.
   - Segregated pipelines into separate `ci.yml` (validation & security) and `cd.yml` (delivery & deployment) workflows.

2. **Zero Long-Lived Credentials via AWS OIDC**:
   - Eliminated static AWS Access Key / Secret Key pairs from GitHub Secrets.
   - Utilized AWS IAM OpenID Connect (OIDC) identity federation with scoped trust policies (`sub` claim restricted to repository) and least-privilege IAM policies.

3. **Immutable Artifact Traceability**:
   - Container images are tagged using the full Git commit SHA (`${{ github.sha }}`) alongside `latest`.
   - Helm deployments strictly reference the immutable commit SHA to guarantee reproducibility and auditability from git commit to running container.

4. **Multi-Tier Automated Security Scanning**:
   - Embedded PyPA `pip-audit` to detect known CVEs in Python package dependencies.
   - Embedded Trivy container vulnerability scanner to detect OS and library vulnerabilities before release.

5. **Helm as the Single Application Release Mechanism**:
   - GitHub Actions executes `helm upgrade --install` against the existing parameterized Helm chart from Phase 5 rather than applying raw manifests directly.
   - Verified deployment readiness with `kubectl rollout status` and an automated Python HTTP smoke test script (`scripts/smoke_test.py`).

## Consequences
- **Positive**: Complete deployment reproducibility, high security baseline (OIDC + non-root containers + image scanning), rapid feedback loop, zero additional server maintenance costs.
- **Trade-offs**: Requires initial one-time AWS IAM OIDC identity provider registration in the AWS account.
