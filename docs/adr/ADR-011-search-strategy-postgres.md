# ADR-011: Search strategy

Status: Proposed

## Context

Platform needs search across evidence metadata and extracted content. Initial phase should minimize infrastructure while providing usable search.

## Decision

Use PostgreSQL full-text search for Phase 1. Define searchable tsvector columns on evidence_document and PTIL text fields, with GIN indexes. Evaluate OpenSearch for Phase 2 if search needs grow.

## Rationale

- Minimizes infra footprint for Phase 1
- GIN-indexed tsvector provides acceptable performance for initial scale

## Consequences

- Some advanced search features deferred until OpenSearch migration
- Need to design text extraction and tokenization carefully

Decision: PostgreSQL FTS for Phase 1 (approved)
