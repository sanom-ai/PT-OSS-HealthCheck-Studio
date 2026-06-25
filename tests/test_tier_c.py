from ptoss.connectors.tier_c import scan_tier_c_files
from ptoss.models import TierCFileInput


def test_tier_c_scan_estimate_and_dedupe() -> None:
    result = scan_tier_c_files(
        case_id="case_1",
        tenant_id="tenant_1",
        files=[
            TierCFileInput(file_name="org_chart.docx", content_hash="hash-1", extracted_text="org chart"),
            TierCFileInput(file_name="org_chart_copy.docx", content_hash="hash-1", extracted_text="org chart"),
            TierCFileInput(file_name="policy.pdf", content_hash="hash-2"),
            TierCFileInput(file_name="virus.exe", content_hash="hash-3"),
        ],
    )

    assert result.estimate.files_seen == 4
    assert result.estimate.files_accepted == 2
    assert result.estimate.duplicates_skipped == 1
    assert "virus.exe" in result.estimate.allowlist_violations
    assert result.items[0].mapping.mapped_category == "A"

