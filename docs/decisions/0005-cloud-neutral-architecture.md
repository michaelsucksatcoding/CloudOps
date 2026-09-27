# ADR 0005: Cloud-Neutral Architecture

## Status
Accepted

## Context

CloudOps AI was originally designed around an event-driven AWS architecture:

```text
FastAPI / Events → Kinesis → Lambda → DynamoDB (hot) + S3 (data lake)
                                      ↓
                              Terraform / EKS
```

That architecture was implemented in code (boto3 adapters for Kinesis, DynamoDB,
and S3), in infrastructure (Terraform modules for EKS, ECR, ALB, VPC, IAM), and
in CI/CD (OIDC-authenticated delivery to ECR and EKS).

Two practical problems prevented the project from being validated as designed:

1. **The managed stream could not be provisioned.** The AWS account used for the
   experiment returned a `SubscriptionRequiredException` for Kinesis Data
   Streams, so the asynchronous fan-out was never validated end to end. The
   entire telemetry path therefore depended on infrastructure that could not be
   exercised.
2. **The infrastructure was unverifiable and costly to iterate on.** Terraform
   plans, EKS apply, and ECR delivery all require a funded account and network
   access. Nothing in the ML research loop — the project's actual contribution —
   needed them.

The result was a codebase whose headline architecture could not be run or
demonstrated by the person presenting it. For a final-year project whose stated
research question is whether machine learning can detect abnormal behaviour from
telemetry, that is a direct threat to the validity of the result: the ML
evaluation was reproducible locally, but the surrounding system was not.

This ADR records the decision to remove the cloud architecture rather than
replace it with a different one.

## Decisions

1. **No cloud provider.** The platform targets no cloud provider. No
   replacement provider (Azure, GCP, or otherwise) was introduced, and no new
   managed service, registry, or deployment platform was adopted.

2. **PostgreSQL is the durable system of record and the event transport.** The
   API validates each telemetry event with Pydantic and persists it to
   PostgreSQL. A long-lived worker (`services/event_processor/handler.py`)
   consumes rows newer than a `created_at` watermark and routes them through the
   unchanged `TelemetryProcessor` into the hot store and the data lake. This
   replaces the Kinesis → Lambda hop with a database-backed queue.

3. **Docker Compose is the primary runtime.** The platform is operated with
   `docker compose up --build` against six services: API, PostgreSQL, event
   processor, one-shot ML job, Prometheus, and Grafana. This is the path used
   for all demonstration, evaluation, and acceptance testing.

4. **Helm is a secondary target for generic local Kubernetes.** The chart
   targets kind, k3d, and minikube. `values.yaml` is the canonical
   configuration: it contains no cloud IAM binding, no cloud ingress
   controller, no cloud block storage class, and no managed-service wiring. All
   services are `ClusterIP` and are reached with `kubectl port-forward`. The
   former `values-local.yaml` overlay was deleted because its only purpose was
   to undo AWS defaults that no longer exist.

5. **No Terraform.** All Terraform configuration, modules, plan artifacts, and
   state files were deleted. Continuous integration validates Python quality
   gates, the Helm chart, the Compose stack, and the ML evaluation. Continuous
   deployment was deleted entirely; the project has no automated release path,
   by design.

6. **boto3 and botocore removed.** They were runtime dependencies solely for the
   removed adapters. The CI pipeline asserts that neither is installed, to
   prevent the coupling returning unnoticed.

7. **Provider-neutral telemetry fields are retained.** `region`, `environment`,
   `tenant_id`, `instance_id`, and `deployment_version` remain in the telemetry
   contract because they are meaningful concepts for any deployment. Only
   cloud-specific *defaults* were removed; for example `region` no longer
   defaults to `us-east-1` and is now an optional label.

8. **The lost capability is documented, not hidden.** See
   [docs/architecture/event-processing.md](../architecture/event-processing.md)
   and the limitations section of [docs/evaluation/limitations.md](../evaluation/limitations.md).

## Consequences

### Positive

- **The whole system runs and is verifiable.** The full stack, the eight
  incident scenarios, and the ML evaluation were all executed on one machine
  with no account, no credentials, and no network dependency.
- **The research claim is now defensible.** The ML results are produced by the
  same code path a reviewer can run, and the platform around it demonstrably
  works.
- **The dependency surface is smaller and auditable.** No cloud SDK, no
  Terraform provider downloads, no IAM configuration to reason about.
- **Cost is bounded.** There is no infrastructure bill to pay while the project
  is developed or demonstrated.

### Negative and accepted trade-offs

- **Durable asynchronous fan-out is lost.** This is the real cost. The removed
  Kinesis → Lambda path provided a durable, independently-scaled stream with
  retry semantics and partitioned ordering per service key. PostgreSQL polling
  provides at-least-once processing with no broker, but throughput is bounded by
  the database and the hot store is in-process, so it does not survive a worker
  restart. This is stated as a limitation rather than presented as equivalent.
- **No infrastructure-as-code demonstration.** Removing Terraform removes the
  ability to show IaC as part of the project. This was judged less valuable than
  having a working, reproducible system.
- **No public deployment.** Without a CDN, ingress controller, or managed
  cluster, the API is only reachable locally. For this project that is
  acceptable; a public deployment was never a research requirement.
- **A former capability is now only partially covered by unit tests.** The
  deleted Kinesis, DynamoDB, and S3 adapters were the only place object-store
  and stream semantics were exercised. That coverage is genuinely gone.

### Neutral

- The containerization, health-probe segregation (`/health/live` vs
  `/health/ready`), non-root execution, resource limits, and NetworkPolicy
  decisions from ADR 0003 all remain in force. Only the cloud-specific
  infrastructure behind them was removed.

## Alternatives considered

- **Fix the AWS account and keep the original architecture.** Rejected. The
  research question does not require managed streams, and any reviewer without
  the same account would be unable to reproduce the result.
- **Move the fan-out to a different managed service.** Rejected. This would
  reintroduce the same class of problem: an unverifiable dependency and a
  credential to manage. It would also contradict the instruction not to replace
  AWS with another hosted service.
- **Keep the code but disable the cloud adapters.** Rejected. Dead adapters plus
  a live `boto3` dependency misrepresent the architecture and make the codebase
  harder to reason about. The adapters were removed outright.
- **Introduce a local broker (e.g. Redis Streams or NATS) to preserve durable
  fan-out.** Referred, not adopted. It remains a reasonable future extension if
  measured throughput becomes a problem, but it adds a component that the
  current evaluation does not justify. Redis is already an optional dependency
  for caching and is not yet used.

## Related

- [ADR 0003](0003-kubernetes-eks-architecture.md) — superseded
- [ADR 0004](0004-cicd-devops-automation.md) — superseded
- [docs/architecture/event-processing.md](../architecture/event-processing.md)
