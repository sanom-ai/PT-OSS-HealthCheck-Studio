from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import ceil
from pathlib import PurePosixPath

from ptoss.models import (
    EvidenceDocument,
    EvidenceMapping,
    FreshnessStatus,
    SourceType,
    TierCFileInput,
    TierCScanEstimate,
)

ALLOWED_EXTENSIONS = {".docx", ".pdf", ".xlsx", ".csv", ".txt", ".png", ".jpg", ".jpeg", ".tiff"}


@dataclass(frozen=True)
class TierCScanItem:
    document: EvidenceDocument
    mapping: EvidenceMapping
    extracted_pages: int
    ocr_pages: int
    ai_pages: int


@dataclass(frozen=True)
class TierCScanResult:
    estimate: TierCScanEstimate
    items: list[TierCScanItem] = field(default_factory=list)


def infer_document_type(file_name: str) -> str:
    suffix = PurePosixPath(file_name.lower()).suffix
    return {
        ".docx": "DOCX",
        ".pdf": "PDF",
        ".xlsx": "XLSX",
        ".csv": "CSV",
        ".txt": "TXT",
        ".png": "IMAGE",
        ".jpg": "IMAGE",
        ".jpeg": "IMAGE",
        ".tiff": "IMAGE",
    }.get(suffix, "UNKNOWN")


def infer_category(file_name: str, document_type: str, extracted_text: str | None) -> tuple[str, float, str]:
    name = file_name.lower()
    text = (extracted_text or "").lower()
    if any(token in name for token in ["org", "organization", "chart"]):
        return "A", 0.82, "filename heuristic"
    if any(token in name for token in ["sop", "procedure", "process", "wi", "work instruction"]):
        return "B", 0.86, "filename heuristic"
    if any(token in name for token in ["jd", "job", "raci", "skill", "manpower"]):
        return "C", 0.84, "filename heuristic"
    if any(token in name for token in ["log", "audit", "erp", "ticket", "incident"]):
        return "D", 0.8, "filename heuristic"
    if any(token in name for token in ["kpi", "kri", "capa", "audit report"]):
        return "E", 0.8, "filename heuristic"
    if any(token in name for token in ["form", "template", "checklist", "matrix"]):
        return "F", 0.78, "filename heuristic"
    if "public" in name or "government" in name or "sector" in name:
        return "G", 0.76, "filename heuristic"
    if "stale" in text or "revision" in text:
        return "H", 0.7, "text heuristic"
    if document_type == "IMAGE":
        return "H", 0.55, "image fallback"
    return "H", 0.5, "fallback"


def compute_freshness_status(effective_date, latest_update_date, justification_note: str | None = None):
    reference_date = effective_date or latest_update_date
    if reference_date is None:
        return FreshnessStatus.UNKNOWN_FRESHNESS
    age_days = (datetime.now(timezone.utc).date() - reference_date).days
    if age_days > 365:
        if justification_note and "justify" in justification_note.lower():
            return FreshnessStatus.JUSTIFIED_STALE
        return FreshnessStatus.STALE_BY_DEFAULT
    return FreshnessStatus.CURRENT


def estimate_pages(file: TierCFileInput) -> tuple[int, int, int]:
    document_type = infer_document_type(file.file_name)
    extracted_text = file.extracted_text or ""
    if extracted_text:
        estimated_pages = max(1, ceil(len(extracted_text) / 3500))
    elif document_type == "PDF":
        estimated_pages = 2
    else:
        estimated_pages = 1

    estimated_ocr_pages = estimated_pages if document_type in {"PDF", "IMAGE"} and not extracted_text else 0
    estimated_ai_pages = 1 if estimated_ocr_pages > 0 else 0
    return estimated_pages, estimated_ocr_pages, estimated_ai_pages


def estimate_cost(estimated_pages: int, estimated_ocr_pages: int, estimated_ai_pages: int) -> float:
    return round(estimated_pages * 0.02 + estimated_ocr_pages * 0.15 + estimated_ai_pages * 0.25, 2)


def scan_tier_c_files(
    case_id: str,
    tenant_id: str,
    files: list[TierCFileInput],
    existing_hashes: set[str] | None = None,
) -> TierCScanResult:
    existing_hashes = set(existing_hashes or set())
    items: list[TierCScanItem] = []
    allowlist_violations: list[str] = []
    duplicates_skipped = 0
    total_pages = 0
    total_ocr_pages = 0
    total_ai_pages = 0
    accepted = 0

    for file in files:
        suffix = PurePosixPath(file.file_name.lower()).suffix
        if suffix not in ALLOWED_EXTENSIONS:
            allowlist_violations.append(file.file_name)
            continue
        if file.content_hash in existing_hashes:
            duplicates_skipped += 1
            continue
        existing_hashes.add(file.content_hash)

        document_type = infer_document_type(file.file_name)
        estimated_pages, estimated_ocr_pages, estimated_ai_pages = estimate_pages(file)
        mapped_category, confidence, mapping_method = infer_category(file.file_name, document_type, file.extracted_text)

        document = EvidenceDocument(
            case_id=case_id,
            tenant_id=tenant_id,
            source_type=SourceType.ZIP,
            file_name=file.file_name,
            source_uri=file.source_uri,
            content_hash=file.content_hash,
            document_type=document_type,
            extraction_status="COMPLETED" if file.extracted_text else "QUEUED",
            metadata_completeness=0.65 if file.source_uri else 0.5,
            evidence_quality="MEDIUM" if file.extracted_text else "LOW",
            effective_date=file.modified_at.date() if file.modified_at else None,
            latest_update_date=file.modified_at.date() if file.modified_at else None,
            freshness_status=compute_freshness_status(
                file.modified_at.date() if file.modified_at else None,
                file.modified_at.date() if file.modified_at else None,
                file.extracted_text,
            ),
            extracted_text=file.extracted_text,
        )
        mapping = EvidenceMapping(
            case_id=case_id,
            tenant_id=tenant_id,
            evidence_document_id=document.id,
            mapped_category=mapped_category,
            mapping_status="AUTO_SUGGESTED",
            mapping_method=mapping_method,
            confidence=confidence,
            review_note="Draft mapping suggested from Tier C connector.",
            mapped_to_metrics=["DRS"],
        )
        items.append(
            TierCScanItem(
                document=document,
                mapping=mapping,
                extracted_pages=estimated_pages,
                ocr_pages=estimated_ocr_pages,
                ai_pages=estimated_ai_pages,
            )
        )
        accepted += 1
        total_pages += estimated_pages
        total_ocr_pages += estimated_ocr_pages
        total_ai_pages += estimated_ai_pages

    estimate = TierCScanEstimate(
        files_seen=len(files),
        files_accepted=accepted,
        duplicates_skipped=duplicates_skipped,
        allowlist_violations=allowlist_violations,
        estimated_pages=total_pages,
        estimated_ocr_pages=total_ocr_pages,
        estimated_ai_pages=total_ai_pages,
        estimated_cost=estimate_cost(total_pages, total_ocr_pages, total_ai_pages),
    )
    return TierCScanResult(estimate=estimate, items=items)
