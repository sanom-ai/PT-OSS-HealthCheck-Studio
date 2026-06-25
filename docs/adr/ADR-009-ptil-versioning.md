# ADR-009: PTIL versioning and schema target

Status: Proposed

## Context

PTIL is the platform interchange layer for evidence objects and must be versioned for traceability and backward compatibility.

## Decision

Adopt PTIL v0.1.0 for Phase 1. Use semantic versioning for PTIL (MAJOR.MINOR.PATCH). Store JSON Schema files in repo under `schemas/ptil/` and reference schema version in every PTIL payload.

## Rationale

- Versioned schemas ensure reproducible rule evaluation and report generation
- JSON Schema files in repo can be validated during CI

## Consequences

- Need schema migration strategy when PTIL evolves
- Must include schema version in all engine run metadata

Decision: PTIL v0.1.0 (approved)
