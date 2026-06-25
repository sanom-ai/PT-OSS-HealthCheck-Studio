# ADR-008: Multi-tenancy model

Status: Proposed

## Context

Platform must support multi-tenant deployments with strict data isolation, per-tenant configuration, and tenant-scoped object storage.

## Decision

Use tenant_id on all tenant-scoped tables and enforce Row-Level Security (RLS) in PostgreSQL. API layer injects tenant context from authenticated requests; all DB access must use tenant-aware queries or session variables.

## Rationale

- RLS provides strong server-side enforcement preventing accidental cross-tenant access
- Tenant ID on every row simplifies auditing, per-tenant reporting and lifecycle operations
- Session-level tenant injection reduces developer burden and centralizes enforcement

## Consequences

- Operational complexity in migrations and background jobs (must handle tenant context)
- Requires careful testing and CI checks to prevent queries that bypass tenant filters

Decision: tenant_id + RLS (approved)
