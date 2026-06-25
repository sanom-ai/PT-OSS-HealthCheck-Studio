# ADR-004: Database strategy

Status: Proposed

## Context

The platform requires reliable relational storage for transactional data, flexible document/indexing capabilities for evidence metadata, JSON-based schemas for PTIL objects, and support for full-text search and extensions. Multi-tenant isolation with RLS is a requirement.

## Decision

Use PostgreSQL as the primary database for Phase 1, leveraging JSONB for PTIL object storage and document metadata, and PostgreSQL full-text search for initial search capabilities.

## Alternatives Considered

- PostgreSQL + JSONB (chosen)
- OpenSearch / Elasticsearch for primary search (deferred to Phase 2/4)
- NoSQL (MongoDB) for document-first approach (rejected due to relational needs and RLS support)

## Rationale

- PostgreSQL provides strong ACID guarantees for transactional records (assessments, users, audit events).
- JSONB supports schemaless PTIL payloads while enabling indexing and constraints where needed.
- Row-Level Security (RLS) is well supported for tenant isolation.
- Mature ecosystem: Alembic for migrations, good managed service options across cloud providers.
- Built-in full-text search reduces initial infra complexity compared to adding a separate search engine.

## Consequences

Positive:
- Strong data integrity and auditability.
- Flexible storage for PTIL and rule evaluation artifacts.
- Simpler operational footprint for Phase 1 (no separate search cluster required).

Trade-offs:
- Full-text capabilities are less feature-rich than OpenSearch; plan to evaluate and migrate search to OpenSearch in Phase 2 if necessary.
- JSONB misuse can lead to poor schema governance; enforce PTIL JSON Schema validation at application layer.

Decision: PostgreSQL + JSONB (approved)
