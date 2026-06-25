# ADR-007: OCR strategy

Status: Proposed

## Context

Some submitted evidence will be scanned images or image-based PDFs requiring OCR to extract text. OCR accuracy and throughput influence evidence ingestion SLAs and downstream scoring confidence.

## Decision

Phase 1: Provide a pluggable OCR adapter layer with a default open-source engine (Tesseract) for basic OCR needs and the option to configure a commercial OCR provider (e.g., Google Document AI, AWS Textract, Azure Form Recognizer) for higher accuracy in production.

## Alternatives Considered

- Tesseract (open-source): inexpensive, works offline, but lower accuracy on complex documents
- Commercial OCR (Textract, Document AI): higher accuracy and structured outputs, but cost and complexity
- No OCR: reject scanned evidence (not acceptable for many customers)

## Rationale

- Tesseract allows Phase 1 deployments to operate without vendor lock-in and supports offline/private deployments.
- The adapter pattern enables easy migration to commercial OCR providers when accuracy or throughput requirements justify the cost.
- Document pre-processing (deskewing, image enhancement) should be included to improve OCR quality.

## Consequences

Positive:
- Quick Phase 1 availability with reasonable accuracy for many scanned documents
- Clear upgrade path to commercial OCR

Trade-offs:
- Tesseract's accuracy may be insufficient for highly formatted or low-quality scans; human-in-the-loop review will be necessary for critical documents
- Need to implement preprocessing and quality heuristics

Decision: OCR adapter with Tesseract default, commercial providers toggleable (approved)
