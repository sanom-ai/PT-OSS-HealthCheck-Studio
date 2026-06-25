# ADR-013: Deployment target

Status: Proposed

## Context

Need a repeatable deployment model for dev/staging/production and IaC automation.

## Decision

Target containerised deployments (Docker + Kubernetes) with IaC (Terraform) for infrastructure. Use CI to build container images, store in container registry, and deploy via ArgoCD in production. Support simple container-compose or single-node deployments for local/dev.

## Rationale

- Containers provide consistent runtime across environments
- Kubernetes + ArgoCD supports progressive delivery and GitOps
- Terraform standardises infra across cloud providers

## Consequences

- Operational overhead for Kubernetes; provide simplified local dev options
- Need CI pipelines for image builds and registry pushes

Decision: Containerised + Kubernetes + Terraform + ArgoCD (approved)
