import pytest

import pytest

from ptoss.models import AssessmentMode, TierCFileInput
from ptoss.store import InMemoryPTOSSStore


def test_tenant_mismatch_is_rejected_for_case_operations() -> None:
    store = InMemoryPTOSSStore()
    case = store.create_case("tenant_1", "Acme", assessment_mode=AssessmentMode.PRIVATE)
    store.ingest_tier_c_pack(
        case.id,
        "tenant_1",
        [TierCFileInput(file_name="org_chart.docx", content_hash="hash-1", extracted_text="org chart")],
    )

    with pytest.raises(PermissionError):
        store.evidence_index(case.id, "tenant_2")

    with pytest.raises(PermissionError):
        store.compute_drs(case.id, "tenant_2")
