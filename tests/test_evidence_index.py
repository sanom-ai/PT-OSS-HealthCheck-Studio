from datetime import datetime, timedelta, timezone

from datetime import datetime, timedelta, timezone

from ptoss.models import AssessmentMode, FreshnessStatus, TierBFileInput, TierCFileInput
from ptoss.store import InMemoryPTOSSStore


def test_evidence_index_surfaces_stale_and_searchable_documents() -> None:
    store = InMemoryPTOSSStore()
    case = store.create_case("tenant_1", "Acme", assessment_mode=AssessmentMode.PRIVATE)
    old_date = datetime.now(timezone.utc) - timedelta(days=500)

    store.ingest_tier_c_pack(
        case.id,
        "tenant_1",
        [
            TierCFileInput(
                file_name="org_chart.docx",
                content_hash="hash-1",
                extracted_text="organization chart",
                modified_at=old_date,
            ),
            TierCFileInput(
                file_name="policy.pdf",
                content_hash="hash-2",
                extracted_text="policy text",
            ),
        ],
    )

    index = store.evidence_index(case.id, "tenant_1", query="org")

    assert len(index) == 1
    assert index[0].file_name == "org_chart.docx"
    assert index[0].freshness_status == FreshnessStatus.STALE_BY_DEFAULT


def test_evidence_index_handles_cloud_folder_sources() -> None:
    store = InMemoryPTOSSStore()
    case = store.create_case("tenant_1", "CloudCo", assessment_mode=AssessmentMode.PRIVATE)

    store.ingest_tier_b_folder(
        case.id,
        "tenant_1",
        [
            TierBFileInput(file_name="org_chart.docx", content_hash="hash-1", extracted_text="org chart", owner="ops"),
            TierBFileInput(file_name="sop.pdf", content_hash="hash-2", extracted_text="procedure", owner="ops"),
        ],
    )

    index = store.evidence_index(case.id, "tenant_1", category="A")

    assert len(index) == 1
    assert index[0].mapped_category == "A"
