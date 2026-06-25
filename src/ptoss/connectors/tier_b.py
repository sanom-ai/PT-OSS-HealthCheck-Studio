from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import PurePosixPath

from ptoss.models import (
    EvidenceDocument,
    EvidenceMapping,
    FreshnessStatus,
    SourceType,
    TierBFileInput,
    TierBScanEstimate,
)

ALLOWED_EXTENSIONS = {".docx", ".pdf", ".xlsx", ".csv", ".txt", ".png", ".jpg", ".jpeg", ".tiff"}


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


@dataclass(frozen=True)
class TierBScanItem:
    document: EvidenceDocument
    mapping: EvidenceMapping


@dataclass(frozen=True)
class TierBScanResult:
    estimate: TierBScanEstimate
    items: list[TierBScanItem] = field(default_factory=list)


def infer_cloud_category(file_name: str, extracted_text: str | None, owner: str | None) -> tuple[str, float, str]:
    name = file_name.lower()
    text = (extracted_text or "").lower()
    if any(token in name for token in ["org", "organization", "chart"]):
        return "A", 0.8, "cloud filename heuristic"
    if any(token in name for token in ["sop", "procedure", "process", "wi", "work instruction"]):
        return "B", 0.83, "cloud filename heuristic"
    if any(token in name for token in ["jd", "job", "raci", "skill", "manpower"]):
        return "C", 0.82, "cloud filename heuristic"
    if any(token in name for token in ["log", "audit", "erp", "ticket", "incident"]):
        return "D", 0.78, "cloud filename heuristic"
    if "policy" in name or "control" in name or "governance" in name:
        return "E", 0.76, "cloud filename heuristic"
    if owner:
        return "F", 0.72, "owner-present heuristic"
    if "revision" in text or "version" in text:
        return "H", 0.7, "text heuristic"
    return "H", 0.55, "fallback"


def scan_tier_b_files(
    case_id: str,
    tenant_id: str,
    files: list[TierBFileInput],
    existing_hashes: set[str] | None = None,
) -> TierBScanResult:
    existing_hashes = set(existing_hashes or set())
    items: list[TierBScanItem] = []
    version_candidates: list[str] = []
    allowlist_violations: list[str] = []
    duplicates_skipped = 0
    accepted = 0
    metadata_confidence_total = 0.0

    seen_names: dict[str, str] = {}

    for file in files:
        suffix = PurePosixPath(file.file_name.lower()).suffix
        if suffix not in ALLOWED_EXTENSIONS:
            allowlist_violations.append(file.file_name)
            continue
        if file.content_hash in existing_hashes:
            duplicates_skipped += 1
            continue
        existing_hashes.add(file.content_hash)

        normalized_name = file.file_name.strip().lower()
        previous_hash = seen_names.get(normalized_name)
        if previous_hash and previous_hash != file.content_hash:
            version_candidates.append(file.file_name)
        else:
            seen_names[normalized_name] = file.content_hash

        document = EvidenceDocument(
            case_id=case_id,
            tenant_id=tenant_id,
            source_type=SourceType.CLOUD,
            file_name=file.file_name,
            source_uri=file.source_uri,
            content_hash=file.content_hash,
            document_type=suffix.lstrip(".").upper() or "UNKNOWN",
            owner=file.owner,
            extraction_status="COMPLETED" if file.extracted_text else "QUEUED",
            metadata_completeness=0.8 if file.owner else 0.55,
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
        mapped_category, confidence, mapping_method = infer_cloud_category(file.file_name, file.extracted_text, file.owner)
        mapping = EvidenceMapping(
            case_id=case_id,
            tenant_id=tenant_id,
            evidence_document_id=document.id,
            mapped_category=mapped_category,
            mapping_status="AUTO_SUGGESTED",
            mapping_method=mapping_method,
            confidence=confidence,
            review_note="Draft mapping suggested from Tier B cloud connector.",
            mapped_to_metrics=["DRS"],
        )
        items.append(TierBScanItem(document=document, mapping=mapping))
        accepted += 1
        metadata_confidence_total += document.metadata_completeness

    average_metadata_confidence = round(metadata_confidence_total / accepted, 2) if accepted else 0.0
    estimate = TierBScanEstimate(
        files_seen=len(files),
        files_accepted=accepted,
        duplicates_skipped=duplicates_skipped,
        version_candidates=version_candidates,
        allowlist_violations=allowlist_violations,
        sync_status="CONNECTED",
        estimated_metadata_confidence=average_metadata_confidence,
    )
    return TierBScanResult(estimate=estimate, items=items)
