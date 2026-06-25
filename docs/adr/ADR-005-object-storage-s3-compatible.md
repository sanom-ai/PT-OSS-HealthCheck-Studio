# ADR-005: Object storage

Status: Proposed

## Context

Evidence documents and generated report artifacts must be stored in durable object storage with strong consistency guarantees, per-tenant isolation, lifecycle policies, and support for large binary files. The system must allow on-prem or cloud deployments and prefer S3-compatible APIs for portability.

## Decision

Adopt S3-compatible object storage as the primary object store for Phase 1. Default to cloud-managed S3 (AWS S3) in hosted deployments and allow S3-compatible self-hosted options (MinIO, Wasabi, or vendor-provided S3-compatible endpoints) for on-prem or region-specific needs.

## Alternatives Considered

- AWS S3 (managed): fully managed, durable, highly available, integrated ecosystem.
- MinIO (self-hosted, S3-compatible): lightweight, Kubernetes-friendly, suitable for private deployments.
- Google Cloud Storage / Azure Blob Storage: viable alternatives but with differing API semantics; choose S3-compatible interface for consistency.

## Rationale

- S3-compatible APIs provide portability across providers and simplify client code.
- Managed S3 reduces operational overhead for Phase 1 while MinIO provides a path for private deployments.
- Tenant-scoped prefixes and bucket policies allow per-tenant isolation and lifecycle management.
- Object storage supports large files, server-side encryption (SSE), and integration with CDN for report delivery.

## Consequences

Positive:
- Scalable, durable storage for large evidence and report artifacts.
- Easier migration across providers when using S3-compatible APIs.
- Supports server-side encryption and lifecycle management.

Trade-offs:
- Operational cost for managed S3 in production; self-hosting increases operational burden.
- Need careful IAM/policy design to ensure tenant isolation.

Decision: S3-compatible object storage (AWS S3 preferred for hosted deployments; MinIO option for self-hosting) (approved)
