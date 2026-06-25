# Risk Register — Initial (Pre-Phase)

Version: 0.1

## Summary
Initial risk register for Pre-Phase. Each entry: id, description, likelihood, impact, mitigation, owner, status.

### R-001: Rule package quality
- Likelihood: Medium
- Impact: High
- Mitigation: Create versioned rule package; test cases and calibration (ExampleOrg); CI validation
- Owner: Product/Rules
- Status: Open

### R-002: PTIL schema drift
- Likelihood: Medium
- Impact: High
- Mitigation: JSON Schema validation in CI; schema versioning; migration plan
- Owner: Platform
- Status: Open

### R-003: Evidence extraction failures
- Likelihood: Medium
- Impact: Medium
- Mitigation: Use layered extraction, human-in-loop fallback, test corpus
- Owner: Connectors
- Status: Open

### R-004: Multi-tenant data leakage
- Likelihood: Low
- Impact: Critical
- Mitigation: RLS enforcement, review, and CI query checks
- Owner: Platform
- Status: Open

(Expand register with probability scores, detection controls, and residual risk during Pre-Phase.)

