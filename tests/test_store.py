from ptoss.models import AssessmentMode, ItemStatus, SourceType
from ptoss.models import AssessmentMode, ReviewAction, ReviewDecision, TierBFileInput
from ptoss.store import InMemoryPTOSSStore


def test_case_flow_to_report() -> None:
    store = InMemoryPTOSSStore()
    case = store.create_case("tenant_1", "Acme", assessment_mode=AssessmentMode.PRIVATE)

    estimate = store.scan_tier_c_pack(
        case.id,
        "tenant_1",
        [
            {
                "file_name": "org_chart.docx",
                "content_hash": "hash-1",
                "extracted_text": "organization chart",
            },
            {
                "file_name": "org_chart.docx",
                "content_hash": "hash-1",
                "extracted_text": "organization chart",
            },
            {
                "file_name": "policy.pdf",
                "content_hash": "hash-2",
                "extracted_text": "policy text",
            },
        ],
    )
    assert estimate.files_seen == 3
    assert estimate.files_accepted == 2
    assert estimate.duplicates_skipped == 1

    queue = store.review_board_queue(case.id)
    assert queue

    updated = store.apply_review_decisions(
        case.id,
        "tenant_1",
        "reviewer_1",
        [
            {"mapping_id": queue[0].mapping_id, "action": "CONFIRM"},
            {"mapping_id": queue[1].mapping_id, "action": "MARK_PARTIAL"},
        ],
    )
    assert updated

    drs_result, run = store.compute_drs(case.id, tenant_id="tenant_1")
    assert run.case_id == case.id
    assert drs_result.value >= 0.0

    report = store.generate_report(case.id, tenant_id="tenant_1")
    assert report.official_status == "PROVISIONAL"
    assert "PT-OSS HealthCheck Studio Provisional Report" in report.content


def test_tier_b_cloud_folder_flow_reaches_review_board() -> None:
    store = InMemoryPTOSSStore()
    case = store.create_case("tenant_1", "CloudCo", assessment_mode=AssessmentMode.PRIVATE)

    estimate = store.ingest_tier_b_folder(
        case.id,
        "tenant_1",
        [
            TierBFileInput(file_name="org_chart.docx", content_hash="hash-1", extracted_text="organization chart", owner="ops"),
            TierBFileInput(file_name="policy.pdf", content_hash="hash-2", extracted_text="policy text"),
            TierBFileInput(file_name="policy.pdf", content_hash="hash-2", extracted_text="policy text"),
        ],
    )
    assert estimate.files_seen == 3
    assert estimate.files_accepted == 2
    assert estimate.duplicates_skipped == 1

    queue = store.review_board_queue(case.id)
    assert len(queue) == 2

    store.apply_review_decisions(
        case.id,
        "tenant_1",
        "reviewer_1",
        [ReviewDecision(mapping_id=item.mapping_id, action=ReviewAction.CONFIRM) for item in queue],
    )
    drs_result, _ = store.compute_drs(case.id, tenant_id="tenant_1")
    assert drs_result.value >= 0.0
