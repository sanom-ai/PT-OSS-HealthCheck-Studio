# Definition of Done (DoD)

Every deliverable must satisfy the following before merge:

- [ ] Unit tests written and passing (coverage ≥ 80% for rule logic, ≥ 70% overall)
- [ ] Integration tests for connectors and workflows
- [ ] PTIL JSON Schema validation passes
- [ ] Rule package version recorded in engine runs
- [ ] Migration scripts created and reviewed
- [ ] No secrets in code; secrets in env or Vault
- [ ] SAST/Security scanning passed
- [ ] Audit events emitted for state changes
- [ ] Traceability: Evidence → Mapping → Claim → Metric → Report
- [ ] OpenAPI documentation updated where relevant
- [ ] Feature flagged if not fully stable

Link this checklist in PR template and enforce on all pre-phase & phase PRs.
