from pathlib import Path
from zipfile import ZipFile

from ptoss.models import AssessmentMode, ReviewAction, ReviewDecision, TierCFileInput
from ptoss.store import InMemoryPTOSSStore


def test_provisional_report_exports_docx_artifact(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PTOSS_REPORT_DIR", str(tmp_path / "reports"))

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

    report = store.generate_report(case.id, "tenant_1")
    report_path = Path(report.artifact_uri)

    assert report.file_format == "DOCX"
    assert report_path.exists()
    assert report_path.suffix == ".docx"

    with ZipFile(report_path) as archive:
        assert "word/document.xml" in archive.namelist()
