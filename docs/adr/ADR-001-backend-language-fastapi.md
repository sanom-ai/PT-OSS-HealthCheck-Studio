# ADR-001: Primary backend language and framework

Status: Proposed

## Context

The project requires a backend that supports fast API development, strong typing, modern async I/O, and good integration with Pydantic models, JSON Schema validation, and an ecosystem that supports production-grade deployment. Team has stated preference for Python-based tooling in the repository skeleton.

## Decision

Use Python 3.11+ as the primary backend language and FastAPI as the primary framework.

## Alternatives Considered

- Node.js with NestJS: strong TypeScript-first ecosystem and type safety, excellent performance for I/O-heavy services.
- Python with Flask: minimal and flexible but lacks built-in async-first design and explicit schema validation.

## Rationale

- FastAPI provides first-class Pydantic integration for validation and JSON Schema generation (OpenAPI) which aligns with PTIL schema and rule package validation needs.
- Python ecosystem has many libraries for document processing (pdfplumber, python-docx), data science, and ML integrations making it easier to implement evidence extraction and LLM integrations.
- Team familiarity (repo skeleton uses Python) reduces onboarding friction.
- Async support in FastAPI + uvicorn provides high throughput for I/O-bound tasks like evidence ingestion and connector integrations.

## Consequences

Positive:
- Rapid development with strong validation and automatic API docs (OpenAPI)
- Easier integration with existing Python libraries for document extraction and ML
- Clear schema-driven development via Pydantic and JSON Schema

Negative / Trade-offs:
- Potential lower raw single-thread CPU throughput compared to some Node.js patterns, mitigated by async design and horizontal scaling in containers
- Need to establish Python deployment best practices (type checks, linting, packaging)

## Migration

If future needs demand a different stack (e.g., organization mandates TypeScript/Node.js), provide an interoperability layer at the API contract level and consider a phased rewrite focusing on critical connectors.

---

Decision: Python + FastAPI (approved)
