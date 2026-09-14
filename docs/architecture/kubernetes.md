# Kubernetes & EKS Architecture — CloudOps AI

This document details the production-oriented containerization, Kubernetes topology, and Amazon EKS infrastructure design for CloudOps AI.

---

## 1. High-Level Cluster Topology

```text
                               AWS VPC (10.0.0.0/16)
┌─────────────────────────────────────────────────────────────────────────────┐
│ Public Subnets (10.0.1.0/24, 10.0.2.0/24)                                  │
│   ├── Internet Gateway                                                      │
│   ├── NAT Gateway (Single EIP for dev cost optimization)                    │
│   └── AWS Application Load Balancer (ALB)                                   │
│           │                                                                 │
│           ▼ (Port 8000)                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Private Subnets (10.0.10.0/24, 10.0.11.0/24)                                │
│   EKS Managed Node Group (t3.medium, min: 2, max: 4, desired: 2)           │
│                                                                             │
│   Namespace: cloudops-dev                                                   │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                                                                       │ │
│   │   ┌───────────────────────────────────────────────┐                   │ │
│   │   │ cloudops-api (Deploy: 2 Pods + HPA 2-5)       │                   │ │
│   │   │   ├── Port 8000 (ClusterIP Service)           │                   │ │
│   │   │   ├── Liveness: /health/live                  │                   │ │
│   │   │   └── Readiness: /health/ready                │                   │ │
│   │   └──────┬───────────────────────┬────────────────┘                   │ │
│   │          │ (Internal RPC/HTTP)   │ (DB queries)                       │ │
│   │          ▼                       ▼                                    │ │
│   │   ┌──────────────────┐   ┌────────────────────────┐                   │ │
│   │   │ cloudops-ml      │   │ Postgres & Redis       │                   │ │
│   │   │ (ClusterIP: 8001)│   │ (Internal Storage)     │                   │ │
│   │   └──────────────────┘   └────────────────────────┘                   │ │
│   │                                                                       │ │
│   │   ┌───────────────────────────────────────────────┐                   │ │
│   │   │ cloudops-event-processor                      │                   │ │
│   │   │ (Worker Daemon / Consumer)                    │                   │ │
│   │   └───────────────────────────────────────────────┘                   │ │
│   │                                                                       │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   Namespace: cloudops-monitoring                                            │
│   └── Monitoring & Observability agents                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ingress & Service Exposure

- **Public Traffic**: Enters through the AWS Application Load Balancer (ALB) provisioned automatically via AWS Load Balancer Controller using the `cloudops-api-ingress` resource.
- **Internal Only**: The `cloudops-ml` and `cloudops-event-processor` services have no external Ingress rules. They are reachable only within the Kubernetes cluster via ClusterIP services.
- **Database & Cache**: Kept entirely internal in private subnets, never exposed publicly.

---

## 3. Security & Isolation Model

1. **Non-Root Execution**:
   - All container images run as `appuser` (UID 1000).
   - `securityContext` specifies `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, and drops all Linux capabilities (`drop: ["ALL"]`).
2. **Kubernetes NetworkPolicies**:
   - `default-deny-ingress`: Drops all unsolicited ingress traffic across the namespace.
   - `api-network-policy`: Permits HTTP traffic on port 8000 from the ALB; allows egress to ML (8001), PostgreSQL (5432), Redis (6379), DNS (53), and HTTPS (443).
   - `ml-network-policy`: Restricts ingress exclusively to pods with `app: cloudops-api`.
   - `event-processor-network-policy`: Blocks all direct ingress; permits outbound streaming/storage calls.
3. **Secret Externalization**:
   - Sensitive database passwords and connection strings are stored in `Secret` manifests or injected via AWS Secrets Manager.
   - Non-sensitive parameters are managed via `ConfigMap`.

---

## 4. Horizontal Pod Autoscaling (HPA)

The `cloudops-api` deployment includes an HPA configured to scale pod replicas dynamically between 2 and 5 based on CPU utilization:
- Target average CPU utilization: `70%`.
- Ensures high availability during traffic surges while preserving baseline resources during quiet periods.

---

## 5. Health Checks & Probes

- **Liveness (`/health/live`)**: Lightweight process probe. Returns HTTP 200 without connecting to external databases to prevent cascading pod restart loops if the database experiences transient load.
- **Readiness (`/health/ready`)**: Verifies database connectivity. Removes the pod from ALB target routing if the database connection drops, without restarting the container.
- **Backward-Compatible Health (`/health`)**: Retains complete diagnostic summary.

---

## 6. Helm Deployment

The unified Helm chart is located at `infrastructure/kubernetes/helm/cloudops-ai/`:

```bash
# Lint chart
helm lint infrastructure/kubernetes/helm/cloudops-ai

# Dry-run template render
helm template cloudops-ai infrastructure/kubernetes/helm/cloudops-ai --values infrastructure/kubernetes/helm/cloudops-ai/values.yaml

# Install / Upgrade
helm upgrade --install cloudops-ai infrastructure/kubernetes/helm/cloudops-ai -n cloudops-dev --create-namespace
```
