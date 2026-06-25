v0.1.0-prephase — Pre-Phase (Foundations)

Includes: ADRs 001–015, NFR, Risk register, IaC baseline (terraform placeholder), Data Model v0, Rule package v0.1.0, PTIL schemas v0.1.0, CI workflow, PR template, ExampleOrg calibration pack, Definition of Done.

Next steps (Phase 1):
- Implement Authentication & User Management (JWT, RBAC)
- Case Workspace + state machine
- Evidence ingestion (Tier B/C connectors)
- Document extraction pipeline + OCR integration
- Rule engine integration and unit tests (DRS logic)
- DB migrations (Alembic), deploy IaC to dev
- CI/CD: build image, run tests, deploy to dev cluster
- Observability & SLOs setup
- Security: SAST, secret management, policy checks

Release branch: release/pre-phase-1
Tag: v0.1.0-prephase
