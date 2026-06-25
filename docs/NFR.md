# Non-Functional Requirements (NFR) — Phase 1

## Performance Targets
- Evidence ingestion: ≤ 30 seconds per 100 digital documents (non-OCR)
- DRS computation: ≤ 5 seconds after review submission
- Report generation: ≤ 60 seconds for standard DOCX
- API response (read): ≤ 300 ms p95
- API response (write/job trigger): ≤ 500 ms p95

## Reliability Targets
- Platform uptime: ≥ 99.5% (SaaS tier)
- Evidence processing success rate: ≥ 95% (digital documents)
- Certification workflow: zero data loss
- RPO ≤ 1 hour | RTO ≤ 4 hours

## Security Targets
- TLS 1.2+ (TLS 1.3 preferred)
- AES-256 at rest for DB & object storage
- Per-tenant encryption key management (Vault integration in later phases)
- Secrets: no secrets in repo; use env or Vault
- PDPA/GDPR principle alignment and audit trails

## Compliance & Audit
- Full audit trail for state changes, scores, reviews
- Immutable EngineRun records (no delete/overwrite)
- Certified report artifacts: write-once, hash-verified

## Scalability
- Phase 1–2: single-tenant or small multi-tenant, ≤ 50 concurrent users
- Evidence index designed for 100k+ documents per tenant

## Monitoring & SLOs
- Instrumentation with Prometheus/OpenTelemetry
- Alerts for ingestion failures, high error rates, and SLO breaches

## Notes
This document is the Phase 1 baseline. Targets to be revisited after real-world calibration and load testing.
