import pytest

from ptoss.models import AssessmentMode, ReviewAction, ReviewDecision, TierCFileInput
from ptoss.store import InMemoryPTOSSStore


def test_drs_is_blocked_until_review_submitted() -> None:
    store = InMemoryPTOSSStore()
    case = store.create_case("tenant_1", "Acme", assessment_mode=AssessmentMode.PRIVATE)
    store.ingest_tier_c_pack(
        case.id,
        "tenant_1",
        [TierCFileInput(file_name="org_chart.docx", content_hash="hash-1", extracted_text="org chart")],
    )

    with pytest.raises(ValueError):
        store.compute_drs(case.id, "tenant_1")


def test_review_board_submission_unblocks_drs() -> None:
    store = InMemoryPTOSSStore()
    case = store.create_case("tenant_1", "Acme", assessment_mode=AssessmentMode.PRIVATE)
    store.ingest_tier_c_pack(
        case.id,
        "tenant_1",
        [
            TierCFileInput(file_name="org_chart.docx", content_hash="hash-1", extracted_text="org chart"),
            TierCFileInput(file_name="sop.pdf", content_hash="hash-2"),
        ],
    )

    queue = store.review_board_queue(case.id)
    decisions = [ReviewDecision(mapping_id=item.mapping_id, action=ReviewAction.CONFIRM) for item in queue]
    updated = store.apply_review_decisions(case.id, "tenant_1", "reviewer_1", decisions)

    assert len(updated) == 2
    drs_result, run = store.compute_drs(case.id, "tenant_1")

    assert drs_result.value >= 0
    assert run.case_id == case.id
