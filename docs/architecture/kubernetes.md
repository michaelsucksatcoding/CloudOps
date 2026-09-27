# Kubernetes Architecture (Generic Local Cluster) — CloudOps AI

This document details the containerization and Kubernetes design for CloudOps AI. The chart targets **any generic local Kubernetes cluster** (kind, k3d, minikube) and contains no cloud-provider assumptions. See
[ADR 0005](../decisions/0005-cloud-neutral-architecture.md).

Docker Compose is the primary runtime; Kubernetes is a secondary option. See the
[README](../../README.md) for the Compose workflow.

---

## 1. High-Level Topology

```text
Generic local Kubernetes cluster (kind / k3d / minikube)
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Namespace: cloudops-dev                                                   │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                                                                       │ │
│   │   ┌───────────────────────────────────────────────┐                   │ │
│   │   │ cloudops-api (Deployment: 2 replicas + HPA)   │                   │ │
│   │   │   ├── ClusterIP Service :8000                  │                   │ │
│   │   │   ├── Liveness:  /health/live                  │                   │ │
│   │   │   └── Readiness: /health/ready                 │                   │ │
│   │   └──────┬───────────────────────┬────────────────┘                   │ │
│   │          │ (HTTP)                │ (SQL over 5432)                    │ │
│   │          ▼                       ▼                                    │ │
│   │   ┌──────────────────┐   ┌────────────────────────┐                   │ │
│   │   │ cloudops-ml      │   │ cloudops-postgres      │                   │ │
│   │   │ ClusterIP :8001  │   │ ClusterIP :5432        │                   │ │
│   │   └──────────────────┘   │ PVC (default SC)       │                   │ │
│   │                          └───────────┬────────────┘                   │ │
│   │   ┌───────────────────────────────────────────────┐                   │ │
│   │   │ cloudops-event-processor (Deployment: 1)      │                   │ │
│   │   │   └── polls PostgreSQL, routes to hot/lake   │                   │ │
│   │   └───────────────────────────────────────────────┘                   │ │
│   │                                                                       │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   Namespace: cloudops-monitoring                                            │
│   ├── cloudops-prometheus  (ClusterIP :9090)                                │
│   └── cloudops-grafana     (ClusterIP :3000)                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Service Exposure

- **No external exposure by default.** Ingress is `enabled: false` because a
  local cluster usually has no ingress controller.
- **`cloudops-api`** — `ClusterIP` on port 8000. Reached with
  `kubectl port-forward -n cloudops-dev svc/cloudops-ai-api 8000:8000`.
- **`cloudops-ml` and `cloudops-event-processor`** — `ClusterIP` only, never
  exposed.
- **`cloudops-postgres`** — `ClusterIP` on 5432, never exposed.
- **Monitoring** — `ClusterIP` on 9090/3000, reached with `kubectl port-forward`.
- **Optional Ingress** — enable per cluster if a controller exists, for example
  `--set ingress.enabled=true --set ingress.className=nginx` (kind) or
  `traefik` (k3d). No provider-specific annotations are shipped.

---

## 3. Storage

PostgreSQL uses a `PersistentVolumeClaim` of 5Gi. `postgres.storage.storageClass`
defaults to the empty string, which means the cluster's own default
`StorageClass` is used. Set it explicitly per cluster when the default is
unsuitable:

```bash
--set postgres.storage.storageClass=standard   # k3d
--set postgres.storage.storageClass=hostpath   # kind
```

The deployment uses `strategy: Recreate` so the single-writer volume is not
attached to two pods during a rollout.

---

## 4. Security & Isolation

1. **Non-Root Execution**
   - Containers run as UID 1000 with `runAsNonRoot: true`.
   - `allowPrivilegeEscalation: false` and all Linux capabilities dropped
     (`drop: ["ALL"]`).
2. **Kubernetes NetworkPolicies**
   - `default-deny-ingress` — drops unsolicited ingress across the namespace.
   - `api-network-policy` — permits HTTP on 8000; allows egress to ML (8001),
     PostgreSQL (5432), Redis (6379), DNS (53), and HTTPS (443).
   - `ml-network-policy` — restricts ingress to pods labelled `app: cloudops-api`.
   - `event-processor-network-policy` — blocks all direct ingress; permits
     outbound database and DNS calls.
3. **Secret Externalization**
   - The PostgreSQL password is generated on first install and stored only in a
     Kubernetes `Secret` (`templates/postgres-secret.yaml`). Nothing sensitive is
     committed.
   - The API receives `DATABASE_URL` from that Secret via `secretKeyRef`.
   - Non-sensitive parameters are managed via `ConfigMap`.
4. **ServiceAccounts** — plain cluster-scoped ServiceAccounts with no cloud identity
   binding or workload-identity annotation.

---

## 5. Horizontal Pod Autoscaling

`cloudops-api` has an HPA scaling between 2 and 5 replicas on 70% average CPU
utilization. This requires the Metrics Server to be installed in the cluster
(kind and k3d include it by default; minikube needs `minikube start
--metrics-server`).

> The API is stateless, so the HPA is safe. `cloudops-event-processor` is
> deliberately **not** autoscaled: it holds an in-memory hot store, and multiple
> replicas would each maintain a partial view. Scaling the worker out requires
> sharding the poll, which is not implemented — see
> [event-processing.md](event-processing.md).

---

## 6. Health Checks & Probes

- **Liveness (`/health/live`)** — lightweight process probe returning 200
  without touching the database, so a transient database issue cannot cause a
  restart loop.
- **Readiness (`/health/ready`)** — verifies database connectivity and removes
  the pod from Service endpoints on failure, without restarting the container.
- **Diagnostic (`/health`)** — full health summary including dependency state.

---

## 7. Helm Values

`values.yaml` is the canonical configuration; there is no separate local overlay.
It contains no cloud identity binding, no cloud ingress controller, no cloud block
storage class, and no managed-service wiring.

Frequently adjusted values:

| Value | Default | Notes |
|---|---|---|
| `namespace.name` | `cloudops-dev` | Must exist before install |
| `api.replicaCount` | `2` | With `api.autoscaling.enabled: true` |
| `api.autoscaling.enabled` | `true` | Requires Metrics Server |
| `postgres.storage.storageClass` | `""` | Empty = cluster default |
| `ingress.enabled` | `false` | Set `className` if enabling |
| `monitoring.enabled` | `true` | Prometheus + Grafana |
| `monitoring.grafana.adminPasswordSecret` | `cloudops-grafana-admin` | Generated on install |

---

## 8. Validation & Known Gaps

Validated in CI on every pull request:

- `helm lint` passes.
- `helm template` renders cleanly with default values.
- A guard asserts the rendered output contains no cloud-provider dependency.

**Not validated:** there is no Kubernetes cluster in the CI runner, so the chart
is never actually applied. Live deployment to kind/k3d/minikube must be verified
manually. Migrations are not run at startup; run `alembic upgrade head` against
the API pod after installing. Alert notification delivery is also unverified, as
no Alertmanager is deployed.
