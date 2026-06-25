# Data Model v0 (Phase 1 Baseline)

## Overview
This baseline lists core tables and brief descriptions. All tenant-scoped tables include `tenant_id` and are subject to Row-Level Security (RLS).

## Core Tables
- organization: tenant profile and metadata
- user: user accounts and auth metadata
- role: role definitions
- role_assignment: user-role mappings
- assessment_case: assessment case header (name, org, mode, state)
- assessment_scope: case scope (departments, date range)
- evidence_source: connector/source metadata (cloud folder, upload)
- evidence_document: document metadata (path, content summary, tsvector)
- evidence_version_history: versions of evidence files
- evidence_mapping: mapping of document regions to PTIL evidence categories
- evidence_claim: extracted claims referencing evidence
- metric_result: DRS and other metric outputs
- engine_run: evaluation run metadata (rule package version, timestamp)
- rule_package_version: rule package registry
- validation_alert: validation warnings/errors
- care_plan_action: suggested remediation actions
- report_artifact: generated report metadata and object storage reference
- certification_review: certification events and approvals
- certification_snapshot: certified report snapshot refs
- audit_event: immutable audit trail for state changes
- monitoring_signal: observability metrics/events
- overlay_object: annotation/overlay artifacts
- review_decision: human review decisions and metadata

## Indexing & Search
- evidence_document includes a `tsvector` column for full-text search with GIN index

## Migrations
- Use Alembic for schema migrations; include tenant-safe migration practices (set tenant context where needed)

## Notes
This schema is a baseline for Phase 1. Additional normalization, constraints, and indexes will be added as requirements crystallize.
