# ADR-014: CI/CD tooling

Status: Proposed

## Context

CI/CD must support linting, tests, builds, image publishing, and deployment automation.

## Decision

Use GitHub Actions for CI (unit tests, linting, security scanning), build container images and publish to container registry, and use ArgoCD for deployments in staging/production. Terraform manages infra provisioning.

## Rationale

- GitHub Actions integrates with repo and is straightforward to configure
- ArgoCD enables GitOps for deployments and sync with desired state
- Terraform and GitHub Actions together automate infra and app lifecycle

## Consequences

- Need service account credentials for registry and ArgoCD in CI secrets
- Must implement secret management and rotate keys

Decision: GitHub Actions + ArgoCD + Terraform (approved)
