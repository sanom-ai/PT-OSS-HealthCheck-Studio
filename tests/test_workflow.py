from ptoss.models import AssessmentMode, ReviewAction, ReviewDecision, TierCFileInput, WorkflowStatus, WorkflowStep
from ptoss.models import (
    AssessmentMode,
    ReviewAction,
    ReviewDecision,
    TierCFileInput,
    WorkflowStatus,
    WorkflowStep,
)
from ptoss.repository import SQLiteCaseRepository
from ptoss.store import InMemoryPTOSSStore


def test_signal_review_submission_auto_advances_workflow() -> None:
    store = InMemoryPTOSSStore()
    case = store.create_case("tenant_1", "Acme", assessment_mode=AssessmentMode.PRIVATE)
    store.ingest_tier_c_pack(
        case.id,
        "tenant_1",
        [TierCFileInput(file_name="org_chart.docx", content_hash="hash-1", extracted_text="org chart")],
    )

    queue = store.review_board_queue(case.id)
    store.signal_review_submission(
        case_id=case.id,
        tenant_id="tenant_1",
        reviewer_id="reviewer_1",
        decisions=[ReviewDecision(mapping_id=queue[0].mapping_id, action=ReviewAction.CONFIRM)],
    )
    workflow = store.workflow_snapshot(case.id)

    assert workflow["workflow_status"] == WorkflowStatus.COMPLETED.value
    assert workflow["workflow_step"] == WorkflowStep.REPORT_GENERATED.value
    assert store.get_case(case.id).reports


def test_resume_workflow_completes_after_review_state() -> None:
    store = InMemoryPTOSSStore()
    case = store.create_case("tenant_1", "Acme", assessment_mode=AssessmentMode.PRIVATE)
    store.ingest_tier_c_pack(
        case.id,
        "tenant_1",
        [TierCFileInput(file_name="org_chart.docx", content_hash="hash-1", extracted_text="org chart")],
    )
    queue = store.review_board_queue(case.id)
    store.apply_review_decisions(
        case.id,
        "tenant_1",
        "reviewer_1",
        [ReviewDecision(mapping_id=queue[0].mapping_id, action=ReviewAction.CONFIRM)],
    )

    snapshot = store.resume_workflow(case.id, tenant_id="tenant_1")

    assert snapshot["workflow_status"] == WorkflowStatus.COMPLETED.value
    assert snapshot["workflow_step"] == WorkflowStep.REPORT_GENERATED.value
    assert store.get_case(case.id).reports


def test_signal_review_submission_waits_when_some_items_remain() -> None:
    store = InMemoryPTOSSStore()
    case = store.create_case("tenant_1", "Acme", assessment_mode=AssessmentMode.PRIVATE)
    store.ingest_tier_c_pack(
        case.id,
        "tenant_1",
        [
            TierCFileInput(file_name="org_chart.docx", content_hash="hash-1", extracted_text="org chart"),
            TierCFileInput(file_name="policy.pdf", content_hash="hash-2", extracted_text="policy text"),
        ],
    )

    queue = store.review_board_queue(case.id)
    store.signal_review_submission(
        case_id=case.id,
        tenant_id="tenant_1",
        reviewer_id="reviewer_1",
        decisions=[ReviewDecision(mapping_id=queue[0].mapping_id, action=ReviewAction.CONFIRM)],
    )
    workflow = store.workflow_snapshot(case.id)

    assert workflow["workflow_status"] == WorkflowStatus.WAITING_FOR_REVIEW.value
    assert workflow["workflow_step"] == WorkflowStep.WAITING_FOR_REVIEW.value
    assert len(store.review_board_queue(case.id)) == 1


def test_workflow_survives_store_restart_via_repository(tmp_path) -> None:
    repository = SQLiteCaseRepository(tmp_path / "ptoss.db")
    store = InMemoryPTOSSStore(repository=repository)
    case = store.create_case("tenant_1", "Acme", assessment_mode=AssessmentMode.PRIVATE)
    store.ingest_tier_c_pack(
        case.id,
        "tenant_1",
        [TierCFileInput(file_name="org_chart.docx", content_hash="hash-1", extracted_text="org chart")],
    )

    restarted = InMemoryPTOSSStore(repository=repository)
    snapshot = restarted.workflow_snapshot(case.id)

    assert snapshot["workflow_status"] == WorkflowStatus.WAITING_FOR_REVIEW.value
    assert snapshot["workflow_step"] == WorkflowStep.WAITING_FOR_REVIEW.value
