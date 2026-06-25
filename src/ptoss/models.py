from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AssessmentMode(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class CaseState(str, Enum):
    DRAFT = "DRAFT"
    EVIDENCE_COLLECTION = "EVIDENCE_COLLECTION"
    AWAITING_EVIDENCE_REVIEW = "AWAITING_EVIDENCE_REVIEW"
    REVIEW_IN_PROGRESS = "REVIEW_IN_PROGRESS"
    REVIEW_SUBMITTED = "REVIEW_SUBMITTED"
    DRS_RUNNING = "DRS_RUNNING"
    DRS_READY = "DRS_READY"
    REPORT_READY = "REPORT_READY"


class WorkflowStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    WAITING_FOR_REVIEW = "WAITING_FOR_REVIEW"
    ADVANCING = "ADVANCING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowStep(str, Enum):
    CASE_CREATED = "CASE_CREATED"
    EVIDENCE_INGESTED = "EVIDENCE_INGESTED"
    WAITING_FOR_REVIEW = "WAITING_FOR_REVIEW"
    REVIEW_SIGNAL_RECEIVED = "REVIEW_SIGNAL_RECEIVED"
    DRS_COMPUTED = "DRS_COMPUTED"
    REPORT_GENERATED = "REPORT_GENERATED"


class SourceType(str, Enum):
    DCC = "DCC"
    CLOUD = "CLOUD"
    ZIP = "ZIP"
    MANUAL = "MANUAL"


class ItemStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    NOT_PROVIDED = "NOT_PROVIDED"


class ReviewAction(str, Enum):
    CONFIRM = "CONFIRM"
    REJECT = "REJECT"
    REMAP = "REMAP"
    MARK_MISSING = "MARK_MISSING"
    MARK_PARTIAL = "MARK_PARTIAL"
    MARK_DUPLICATE = "MARK_DUPLICATE"
    SELECT_LATEST_APPROVED = "SELECT_LATEST_APPROVED"
    MARK_OUT_OF_SCOPE = "MARK_OUT_OF_SCOPE"


class FreshnessStatus(str, Enum):
    CURRENT = "CURRENT"
    STALE_BY_DEFAULT = "STALE_BY_DEFAULT"
    JUSTIFIED_STALE = "JUSTIFIED_STALE"
    UNKNOWN_FRESHNESS = "UNKNOWN_FRESHNESS"


class ThresholdBand(str, Enum):
    GO = "GO"
    GO_WITH_CAUTION = "GO_WITH_CAUTION"
    NO_GO = "NO_GO"


class Organization(BaseModel):
    id: str = Field(default_factory=lambda: new_id("org"))
    name: str


class AssessmentScope(BaseModel):
    departments: list[str] = Field(default_factory=list)
    processes: list[str] = Field(default_factory=list)
    date_from: date | None = None
    date_to: date | None = None
    assessment_mode: AssessmentMode = AssessmentMode.PRIVATE


class TierCFileInput(BaseModel):
    file_name: str
    content_hash: str
    source_uri: str | None = None
    extracted_text: str | None = None
    size_bytes: int | None = None
    folder_path: str | None = None
    modified_at: datetime | None = None


class TierBFileInput(BaseModel):
    file_name: str
    content_hash: str
    source_uri: str | None = None
    extracted_text: str | None = None
    provider: str = "CLOUD"
    folder_path: str | None = None
    owner: str | None = None
    modified_at: datetime | None = None


class TierCScanEstimate(BaseModel):
    files_seen: int
    files_accepted: int
    duplicates_skipped: int
    allowlist_violations: list[str] = Field(default_factory=list)
    estimated_pages: int
    estimated_ocr_pages: int
    estimated_ai_pages: int
    estimated_cost: float


class TierBScanEstimate(BaseModel):
    files_seen: int
    files_accepted: int
    duplicates_skipped: int
    version_candidates: list[str] = Field(default_factory=list)
    allowlist_violations: list[str] = Field(default_factory=list)
    sync_status: str = "CONNECTED"
    estimated_metadata_confidence: float = 0.0


class ReviewQueueItem(BaseModel):
    mapping_id: str
    evidence_document_id: str
    file_name: str
    mapped_category: str
    mapping_status: str
    mapping_method: str
    confidence: float
    document_type: str | None = None
    freshness_status: FreshnessStatus
    review_note: str | None = None


class ReviewDecision(BaseModel):
    mapping_id: str
    action: ReviewAction
    mapped_category: str | None = None
    review_note: str | None = None


class EvidenceIndexEntry(BaseModel):
    evidence_document_id: str
    case_id: str
    tenant_id: str
    file_name: str
    source_type: SourceType
    document_type: str | None = None
    mapped_category: str | None = None
    mapping_status: str | None = None
    owner: str | None = None
    approver: str | None = None
    revision: str | None = None
    freshness_status: FreshnessStatus
    metadata_completeness: float
    evidence_quality: str
    content_hash: str
    source_uri: str | None = None
    extracted_text: str | None = None
    created_at: datetime


class AuditEvent(BaseModel):
    id: str = Field(default_factory=lambda: new_id("audit"))
    tenant_id: str
    case_id: str
    user_id: str | None = None
    event_type: str
    from_state: str | None = None
    to_state: str | None = None
    timestamp: datetime = Field(default_factory=utc_now)
    correlation_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceDocument(BaseModel):
    id: str = Field(default_factory=lambda: new_id("evdoc"))
    case_id: str
    tenant_id: str
    source_type: SourceType
    file_name: str
    source_uri: str | None = None
    content_hash: str
    document_type: str | None = None
    category: str | None = None
    owner: str | None = None
    approver: str | None = None
    revision: str | None = None
    effective_date: date | None = None
    latest_update_date: date | None = None
    extraction_status: str = "QUEUED"
    metadata_completeness: float = 0.0
    evidence_quality: str = "UNKNOWN"
    freshness_status: FreshnessStatus = FreshnessStatus.UNKNOWN_FRESHNESS
    extracted_text: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class EvidenceMapping(BaseModel):
    id: str = Field(default_factory=lambda: new_id("evmap"))
    evidence_document_id: str
    case_id: str
    tenant_id: str
    mapped_category: str
    mapping_status: str
    mapping_method: str
    confidence: float
    review_note: str | None = None
    mapped_to_metrics: list[str] = Field(default_factory=list)


class EvidenceClaim(BaseModel):
    id: str = Field(default_factory=lambda: new_id("claim"))
    case_id: str
    tenant_id: str
    evidence_document_id: str
    evidence_mapping_id: str
    claim_text: str
    claim_tag: str
    location_reference: str | None = None
    quoted_snippet: str | None = None
    used_for: list[str] = Field(default_factory=list)
    confidence: str = "MEDIUM"
    assumption_note: str | None = None
    review_status: str = "PENDING"


class EvidenceItem(BaseModel):
    code: str
    status: ItemStatus
    required: bool = True
    critical: bool = False
    note: str | None = None


class CategoryInput(BaseModel):
    code: str
    items: list[EvidenceItem] = Field(default_factory=list)


class ValidationAlert(BaseModel):
    id: str = Field(default_factory=lambda: new_id("alert"))
    case_id: str
    tenant_id: str
    severity: str
    rule_code: str
    message: str
    required_action: str
    triggered_metric_ids: list[str] = Field(default_factory=list)
    status: str = "OPEN"


class MetricResult(BaseModel):
    id: str = Field(default_factory=lambda: new_id("metric"))
    case_id: str
    tenant_id: str
    metric_code: str
    metric_name: str
    value: float
    unit: str
    threshold_band: ThresholdBand | None = None
    status: str
    formula: str
    confidence: str
    error_margin: str
    evidence_claim_ids: list[str] = Field(default_factory=list)
    data_gap_impact: str | None = None
    rule_package_version: str
    engine_run_id: str


class EngineRun(BaseModel):
    id: str = Field(default_factory=lambda: new_id("run"))
    case_id: str
    tenant_id: str
    rule_package_version: str
    evidence_index_version: str
    engine_version: str
    mode: AssessmentMode
    created_at: datetime = Field(default_factory=utc_now)


class ReportArtifact(BaseModel):
    id: str = Field(default_factory=lambda: new_id("report"))
    case_id: str
    tenant_id: str
    report_type: str
    file_format: str = "MARKDOWN"
    artifact_uri: str
    official_status: str = "PROVISIONAL"
    engine_version: str
    rule_package_version: str
    evidence_index_version: str
    verification_id: str | None = None
    content_hash: str
    generated_at: datetime = Field(default_factory=utc_now)
    content: str


class AssessmentCase(BaseModel):
    id: str = Field(default_factory=lambda: new_id("case"))
    tenant_id: str
    organization: Organization
    scope: AssessmentScope
    state: CaseState = CaseState.DRAFT
    rule_package_version: str = "pt-oss-rules-0.1.0"
    evidence_index_version: str = "evidx_0"
    evidence_documents: list[EvidenceDocument] = Field(default_factory=list)
    evidence_mappings: list[EvidenceMapping] = Field(default_factory=list)
    evidence_claims: list[EvidenceClaim] = Field(default_factory=list)
    metric_results: list[MetricResult] = Field(default_factory=list)
    validation_alerts: list[ValidationAlert] = Field(default_factory=list)
    audit_events: list[AuditEvent] = Field(default_factory=list)
    engine_runs: list[EngineRun] = Field(default_factory=list)
    reports: list[ReportArtifact] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=utc_now)
    workflow_status: WorkflowStatus = WorkflowStatus.NOT_STARTED
    workflow_step: WorkflowStep = WorkflowStep.CASE_CREATED
    workflow_signal_id: str | None = None
    workflow_error: str | None = None
    workflow_started_at: datetime | None = None
    workflow_updated_at: datetime = Field(default_factory=utc_now)
