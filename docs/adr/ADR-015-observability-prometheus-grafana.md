# ADR-015: Observability stack

Status: Proposed

## Context

Need metrics, tracing, and logs for performance, reliability, and auditability.

## Decision

Adopt Prometheus for metrics, Grafana for dashboards, and OpenTelemetry for tracing and instrumenting services. Logs to centralised store (e.g., Loki or cloud logging) depending on deployment.

## Rationale

- Prometheus + Grafana is a standard observability stack with wide support
- OpenTelemetry provides vendor-neutral tracing and metrics instrumentation

## Consequences

- Requires instrumentation work and additional infra (Prometheus, Grafana, exporters)
- Need alerting rules and SLO definitions as part of Phase 2

Decision: Prometheus + Grafana + OpenTelemetry (approved)
