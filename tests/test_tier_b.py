from ptoss.connectors.tier_b import scan_tier_b_files
from ptoss.models import TierBFileInput


def test_tier_b_scan_estimate_and_version_candidates() -> None:
    result = scan_tier_b_files(
        case_id="case_1",
        tenant_id="tenant_1",
        files=[
            TierBFileInput(file_name="Org Chart.docx", content_hash="hash-1", extracted_text="organization chart", owner="ops"),
            TierBFileInput(file_name="Org Chart.docx", content_hash="hash-2", extracted_text="organization chart v2", owner="ops"),
            TierBFileInput(file_name="folder.exe", content_hash="hash-3"),
        ],
    )

    assert result.estimate.files_seen == 3
    assert result.estimate.files_accepted == 2
    assert result.estimate.duplicates_skipped == 0
    assert "Org Chart.docx" in result.estimate.version_candidates
    assert "folder.exe" in result.estimate.allowlist_violations
    assert result.items[0].mapping.mapped_category == "A"
