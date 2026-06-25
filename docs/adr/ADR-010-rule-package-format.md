# ADR-010: Rule package format

Status: Proposed

## Context

Rule packages encode DRS rules, thresholds, and stop conditions. They must be versioned, auditable, and machine-readable.

## Decision

Use JSON Schema-based rule package format with SemVer for package versions. Store rule packages in `rules/` as immutable, version-tagged artifacts. Engine stores a reference to the rule package version used in every run.

## Rationale

- JSON Schema is widely supported and integrates with Pydantic/validation
- SemVer allows controlled upgrades and compatibility checks

## Consequences

- Rule authors must follow schema; CI validates rule packages
- Engines must record package version for traceability

Decision: JSON Schema + SemVer (approved)
