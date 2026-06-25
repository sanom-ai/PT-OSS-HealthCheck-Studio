# ADR-006: Document extraction

Status: Proposed

## Context

The system must extract structured text and metadata from a variety of document formats (PDF, DOCX, XLSX, plain text) to enable evidence mapping, claim extraction, and rule evaluation. Extraction should be reliable for digital PDFs and Office documents in Phase 1.

## Decision

Adopt a layered extraction approach for Phase 1:

- Use unstructured.io for generic multi-format parsing where available (wrapper layer)
- Use pdfplumber for robust PDF text/table extraction
- Use python-docx for DOCX extraction
- Use openpyxl / pandas for Excel where needed

## Alternatives Considered

- Commercial extraction services (e.g., AWS Textract, Google Document AI): higher accuracy but increased cost and operational complexity
- Apache Tika: Java-based, powerful, but heavier to operate in Python-centric stack

## Rationale

- pdfplumber and python-docx are lightweight, well-supported Python libraries that handle most digital documents reliably for Phase 1.
- A wrapper layer (unstructured.io or a small internal adapter) allows swapping in commercial providers later without changing upper layers.
- Prioritize deterministic outputs and provenance metadata for traceability.

## Consequences

Positive:
- Good coverage for digital documents without OCR
- Lower operational cost in Phase 1

Trade-offs:
- OCR-requiring documents will need a separate OCR step (see ADR-007)
- Complex layouts or scanned PDFs may need additional parsing or human-in-the-loop correction

Decision: Use pdfplumber + python-docx + unstructured.io adapter pattern (approved)
