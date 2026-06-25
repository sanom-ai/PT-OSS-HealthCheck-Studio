# Release Notes Archive

## Overview

This directory contains release notes for each version of PT-OSS HealthCheck Studio.

## Versioning

- **Format**: Semantic Versioning (MAJOR.MINOR.PATCH)
- **Release Branches**: `release/v*`
- **Tags**: Annotated tags (`v0.1.0`, `v1.0.0`, etc.)

## Current Releases

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| v0.1.0 | 2026-06-25 | Released (Pre-Phase Foundations) | ADRs, PTIL schemas, rule package, baseline tests |

## How to Use

1. **For a new release**:
   - Create branch `release/vX.Y.Z` from `main`
   - Update `RELEASE_NOTES-vX.Y.Z.md` with changes
   - Create PR and merge
   - Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
   - Push tag: `git push origin vX.Y.Z`
   - Create GitHub release from tag (use content from RELEASE_NOTES file)

2. **To view a release**:
   - Check GitHub Releases: https://github.com/sanom-ai/PT-OSS-HealthCheck-Studio/releases
   - Or read the corresponding RELEASE_NOTES-*.md file here

3. **Installation**:
   - `pip install git+https://github.com/sanom-ai/PT-OSS-HealthCheck-Studio.git@vX.Y.Z`

## Future Releases

Planned versions:
- **v0.2.0** (Q3 2026): Phase 1 — Database, multi-tenancy, API endpoints
- **v0.3.0** (Q4 2026): Phase 2 — Document extraction, advanced rules, workflows
- **v1.0.0** (2027): Phase 3 — UI, analytics, enterprise deployment

---

For more info, see the main README.md and docs/
