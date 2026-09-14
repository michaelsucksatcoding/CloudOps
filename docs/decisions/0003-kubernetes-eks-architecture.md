# ADR 0003: Kubernetes & Amazon EKS Architecture

## Status
Accepted

## Context
Phase 5 of CloudOps AI requires containerization of services and establishing a production-grade Kubernetes deployment on Amazon EKS while avoiding unnecessary complexity, excessive AWS costs, or brittle infrastructure.

## Decisions

1. **Multi-Stage Containerization**:
   - A single multi-stage `Dockerfile` with distinct build targets (`api`, `ml`, `event-processor`) was selected to share common caching layers while keeping individual container images lean and focused.
   - All containers run as non-root user (`appuser`, UID 1000) and drop all Linux capabilities.

2. **EKS Cluster Topology**:
   - Managed node group is placed in private subnets across two Availability Zones for high availability and isolation.
   - Nodes use cost-effective `t3.medium` instances with autoscaling configured between 2 (desired/min) and 4 (max).
   - A single NAT Gateway is utilized for the development environment to reduce AWS monthly overhead.

3. **Ingress and Service Routing**:
   - Only `cloudops-api` is exposed externally via an AWS Application Load Balancer (ALB) through the AWS Load Balancer Controller.
   - `cloudops-ml` and `cloudops-event-processor` are configured as internal ClusterIP services and isolated with Kubernetes NetworkPolicies.

4. **Health Probe Segregation**:
   - Separated `/health/live` (lightweight, non-dependent process check) and `/health/ready` (database/dependency check) from the full diagnostic `/health` endpoint to prevent cascading pod restarts during downstream degradations.

5. **Packaging with Helm**:
   - Created a configurable Helm v2 chart (`cloudops-ai`) that parameterizes all image registries, resource limits, environment configs, and scaling thresholds.

## Consequences
- **Positive**: Clean separation of concerns, least-privilege networking, cost-optimized infrastructure, reproducible deployment with Terraform and Helm.
- **Trade-offs**: Requires AWS Load Balancer Controller and Metrics Server in the EKS cluster for full ALB and HPA functionality in a live environment.
