from ptoss.calibration import build_ExampleOrg_case
from ptoss.calibration import build_ExampleOrg_case
from ptoss.rules import calculate_drs


def test_ExampleOrg_calibration_case_stays_in_expected_band() -> None:
    case = build_ExampleOrg_case()
    result = calculate_drs(
        categories=case.categories,
        mode=case.mode,
        case_id=case.case_id,
        tenant_id="tenant_1",
    )

    assert case.expectation.drs_min <= result.value <= case.expectation.drs_max
    assert result.band.value == case.expectation.band
    assert len(result.critical_alerts) == case.expectation.critical_alert_count

