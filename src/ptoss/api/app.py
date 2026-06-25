from __future__ import annotations

from pydantic import BaseModel, Field

from ptoss.models import AssessmentMode, ReviewAction, ReviewDecision, SourceType, TierBFileInput, TierCFileInput
from ptoss.repository import SQLiteCaseRepository
from ptoss.store import InMemoryPTOSSStore

try:
    from fastapi import FastAPI, HTTPException
except ImportError:  # pragma: no cover - fallback for environments without FastAPI
    FastAPI = None

    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str) -> None:
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail


app = FastAPI(title="PT-OSS HealthCheck Studio API", version="0.1.0") if FastAPI else None
store = InMemoryPTOSSStore(repository=SQLiteCaseRepository("data/ptoss.db"))


class CreateCaseRequest(BaseModel):
    tenant_id: str = "tenant_demo"
    organization_name: str
    assessment_mode: AssessmentMode = AssessmentMode.PRIVATE


class AddEvidenceRequest(BaseModel):
    tenant_id: str
    source_type: SourceType
    file_name: str
    content_hash: str
    document_type: str | None = None
    source_uri: str | None = None
    extracted_text: str | None = None


class MapEvidenceRequest(BaseModel):
    tenant_id: str
    evidence_document_id: str
    mapped_category: str
    mapping_method: str = "HEURISTIC"
    confidence: float = Field(ge=0.0, le=1.0)
    review_note: str | None = None
    mapped_to_metrics: list[str] = Field(default_factory=list)


class ReviewSubmissionRequest(BaseModel):
    tenant_id: str
    reviewer_id: str = "reviewer_demo"
    decisions: list[dict]


class TierCScanRequest(BaseModel):
    tenant_id: str
    files: list[TierCFileInput]


class TierBScanRequest(BaseModel):
    tenant_id: str
    files: list[TierBFileInput]


class ReviewBoardDecisionRequest(BaseModel):
    tenant_id: str
    reviewer_id: str = "reviewer_demo"
    decisions: list[ReviewDecision]


class WorkflowResumeRequest(BaseModel):
    tenant_id: str
    reviewer_id: str = "workflow_bot"


class EvidenceIndexQueryRequest(BaseModel):
    tenant_id: str
    query: str | None = None
    category: str | None = None
    freshness_status: str | None = None


def health() -> dict[str, str]:
    return {"status": "ok"}


def create_case(request: CreateCaseRequest) -> dict:
    case = store.create_case(
        tenant_id=request.tenant_id,
        organization_name=request.organization_name,
        assessment_mode=request.assessment_mode,
    )
    return case.model_dump()


def get_case(case_id: str) -> dict:
    try:
        return store.get_case(case_id).model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


def add_evidence(case_id: str, request: AddEvidenceRequest) -> dict:
    try:
        evidence = store.add_evidence(case_id=case_id, **request.model_dump())
        return evidence.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


def preview_tier_c(request: TierCScanRequest) -> dict:
    estimate = store.preview_tier_c_pack(files=request.files)
    return estimate.model_dump()


def preview_tier_b(request: TierBScanRequest) -> dict:
    estimate = store.preview_tier_b_folder(files=request.files)
    return estimate.model_dump()


def ingest_tier_c(case_id: str, request: TierCScanRequest) -> dict:
    try:
        estimate = store.ingest_tier_c_pack(case_id=case_id, tenant_id=request.tenant_id, files=request.files)
        return estimate.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


def ingest_tier_b(case_id: str, request: TierBScanRequest) -> dict:
    try:
        estimate = store.ingest_tier_b_folder(case_id=case_id, tenant_id=request.tenant_id, files=request.files)
        return estimate.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


def map_evidence(case_id: str, request: MapEvidenceRequest) -> dict:
    try:
        mapping = store.map_evidence(case_id=case_id, **request.model_dump())
        return mapping.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


def submit_review(case_id: str, request: ReviewSubmissionRequest) -> dict:
    try:
        return {"decisions": store.submit_review(case_id=case_id, **request.model_dump())}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


def review_board(case_id: str) -> dict:
    try:
        return {"items": [item.model_dump() for item in store.review_board_queue(case_id)]}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


def submit_review_board(case_id: str, request: ReviewBoardDecisionRequest) -> dict:
    try:
        updated = store.signal_review_submission(
            case_id=case_id,
            tenant_id=request.tenant_id,
            reviewer_id=request.reviewer_id,
            decisions=request.decisions,
        )
        return {"updated": updated, "workflow": store.workflow_snapshot(case_id)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


def workflow_state(case_id: str) -> dict:
    try:
        return store.workflow_snapshot(case_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


def resume_workflow(case_id: str, request: WorkflowResumeRequest) -> dict:
    try:
        return store.resume_workflow(case_id=case_id, tenant_id=request.tenant_id, reviewer_id=request.reviewer_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


def compute_drs(case_id: str, tenant_id: str) -> dict:
    try:
        drs_result, run = store.compute_drs(case_id=case_id, tenant_id=tenant_id)
        return {"drs": drs_result.value, "band": drs_result.band.value, "engine_run_id": run.id}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


def generate_report(case_id: str, tenant_id: str) -> dict:
    try:
        report = store.generate_report(case_id=case_id, tenant_id=tenant_id)
        return report.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


def evidence_index(case_id: str, request: EvidenceIndexQueryRequest) -> dict:
    try:
        items = store.evidence_index(
            case_id=case_id,
            tenant_id=request.tenant_id,
            query=request.query,
            category=request.category,
            freshness_status=request.freshness_status,
        )
        return {"items": [item.model_dump() for item in items]}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


if app is not None:
    app.get("/health")(health)
    app.post("/cases")(create_case)
    app.get("/cases/{case_id}")(get_case)
    app.post("/cases/{case_id}/evidence")(add_evidence)
    app.post("/tier-c/estimate")(preview_tier_c)
    app.post("/tier-b/estimate")(preview_tier_b)
    app.post("/cases/{case_id}/tier-c/ingest")(ingest_tier_c)
    app.post("/cases/{case_id}/tier-b/ingest")(ingest_tier_b)
    app.post("/cases/{case_id}/mapping")(map_evidence)
    app.post("/cases/{case_id}/review")(submit_review)
    app.get("/cases/{case_id}/review-board")(review_board)
    app.post("/cases/{case_id}/review-board/submit")(submit_review_board)
    app.get("/cases/{case_id}/workflow")(workflow_state)
    app.post("/cases/{case_id}/workflow/resume")(resume_workflow)
    app.post("/cases/{case_id}/evidence-index")(evidence_index)
    app.post("/cases/{case_id}/drs")(compute_drs)
    app.post("/cases/{case_id}/report")(generate_report)
