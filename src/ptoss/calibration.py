from dataclasses import dataclass

from dataclasses import dataclass

from .models import CategoryInput, EvidenceItem, ItemStatus


@dataclass(frozen=True)
class CalibrationExpectation:
    drs_min: float
    drs_max: float
    band: str
    critical_alert_count: int


@dataclass(frozen=True)
class CalibrationCase:
    case_id: str
    name: str
    mode: str
    categories: list[CategoryInput]
    expectation: CalibrationExpectation


def build_ExampleOrg_case() -> CalibrationCase:
    categories = [
        CategoryInput(code="A", items=[EvidenceItem(code="A_ORG", status=ItemStatus.AVAILABLE, critical=True)]),
        CategoryInput(code="B", items=[EvidenceItem(code="B_SOP", status=ItemStatus.AVAILABLE, critical=True)]),
        CategoryInput(code="C", items=[EvidenceItem(code="C_JD", status=ItemStatus.PARTIAL)]),
        CategoryInput(code="D", items=[EvidenceItem(code="D_LOGS", status=ItemStatus.MISSING, critical=True)]),
        CategoryInput(code="E", items=[EvidenceItem(code="E_KPI", status=ItemStatus.AVAILABLE)]),
        CategoryInput(code="F", items=[EvidenceItem(code="F_MATRIX", status=ItemStatus.MISSING)]),
        CategoryInput(code="H", items=[EvidenceItem(code="H_QUALITY", status=ItemStatus.AVAILABLE)]),
    ]
    expectation = CalibrationExpectation(
        drs_min=55.0,
        drs_max=56.0,
        band="GO_WITH_CAUTION",
        critical_alert_count=1,
    )
    return CalibrationCase(
        case_id="ExampleOrg_private_baseline",
        name="ExampleOrg",
        mode="PRIVATE",
        categories=categories,
        expectation=expectation,
    )

