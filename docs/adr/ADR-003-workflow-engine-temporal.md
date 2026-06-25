# ADR-003: Workflow engine

Status: Proposed

## Context

The engineering plan requires a workflow engine to coordinate long-running, stateful processes: evidence ingestion, document extraction, human review gates, scoring pipelines, and report generation. Workflows must be observable, restartable, and auditable across failures and upgrades.

## Decision

Adopt Temporal as the primary workflow engine (recommended) and design the codebase with an abstraction layer that allows a simpler job queue (e.g., Celery/RQ) to be used for Phase 1 if Temporal cannot be provisioned immediately.

## Alternatives Considered

- Temporal: full-featured, language SDKs, durable workflows, strong observability and retry semantics.
- Celery/RQ with Redis/RabbitMQ: simpler to stand up but lacks durable workflow primitives and long-lived state management.
- Orchestrator-based (e.g., Argo Workflows): Kubernetes-native but more operational complexity for local/dev.

## Rationale

- Temporal offers durable, versioned workflows with rich retry/compensation semantics and visibility that maps well to audit and certification requirements.
- Temporal's SDKs and community support long-lived workflows and make modelling review gates straightforward.
- The abstraction/fallback ensures Phase 1 progress is not blocked if Temporal is unavailable.

## Consequences

Positive:
- Durable, auditable, restartable workflow executions
- Simplifies modelling of human-in-the-loop steps and compensation logic

Trade-offs:
- Additional operational complexity (Temporal server or cloud offering)
- Need to add Temporal SDK and deployment plan into IaC baseline

Migration:
- Provide a well-documented fallback adapter using simple job queue implementation for early-stage deployments. Migrate to Temporal by replacing the adapter implementation and mapping existing tasks to Temporal activities/workflows.

Decision: Temporal preferred; fallback adapter for Phase 1 allowed (approved)
