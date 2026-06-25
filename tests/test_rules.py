from ptoss.models import CategoryInput, EvidenceItem, ItemStatus, ThresholdBand
from ptoss.rules import calculate_drs


def test_drs_go_band_when_all_available() -> None:
    categories = [
        CategoryInput(code=code, items=[EvidenceItem(code=f"{code}-1", status=ItemStatus.AVAILABLE)])
        for code in ["A", "B", "C", "D", "E", "F"]
    ]
    result = calculate_drs(categories, mode="PRIVATE")
    assert result.band == ThresholdBand.GO
    assert result.value == 100.0


def test_drs_nogo_when_all_missing() -> None:
    categories = [
        CategoryInput(code=code, items=[EvidenceItem(code=f"{code}-1", status=ItemStatus.MISSING)])
        for code in ["A", "B", "C", "D", "E", "F"]
    ]
    result = calculate_drs(categories, mode="PRIVATE")
    assert result.band == ThresholdBand.NO_GO
    assert result.value == 0.0


def test_critical_alert_emitted_for_missing_critical_item() -> None:
    categories = [
        CategoryInput(code="A", items=[EvidenceItem(code="DoA", status=ItemStatus.MISSING, critical=True)]),
        CategoryInput(code="B", items=[EvidenceItem(code="SOP", status=ItemStatus.AVAILABLE)]),
        CategoryInput(code="C", items=[EvidenceItem(code="JD", status=ItemStatus.AVAILABLE)]),
        CategoryInput(code="D", items=[EvidenceItem(code="Log", status=ItemStatus.AVAILABLE)]),
        CategoryInput(code="E", items=[EvidenceItem(code="CAPA", status=ItemStatus.AVAILABLE)]),
        CategoryInput(code="F", items=[EvidenceItem(code="Form", status=ItemStatus.AVAILABLE)]),
    ]
    result = calculate_drs(categories, mode="PRIVATE", case_id="case_1", tenant_id="tenant_1")
    assert result.critical_alerts
    assert result.critical_alerts[0].rule_code.startswith("CRIT_A_")

