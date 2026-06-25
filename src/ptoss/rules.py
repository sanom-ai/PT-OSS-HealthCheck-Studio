from __future__ import annotations

from dataclasses import dataclass

from .models import CategoryInput, ItemStatus, ThresholdBand, ValidationAlert


STATUS_POINTS = {
    ItemStatus.AVAILABLE: 1.0,
    ItemStatus.PARTIAL: 0.5,
    ItemStatus.MISSING: 0.0,
    ItemStatus.NOT_PROVIDED: 0.0,
    ItemStatus.OUT_OF_SCOPE: None,
}

DEFAULT_CATEGORY_WEIGHTS = {
    "A": 15,
    "B": 15,
    "C": 10,
    "D": 20,
    "E": 15,
    "F": 15,
    "G": 10,
}


@dataclass(frozen=True)
class CategoryScore:
    code: str
    readiness: float
    weight: float
    weighted_score: float


@dataclass(frozen=True)
class DRSResult:
    value: float
    band: ThresholdBand
    category_scores: list[CategoryScore]
    critical_alerts: list[ValidationAlert]
    formula: str
    quality_score: float | None = None


def _points_for_status(status: ItemStatus) -> float | None:
    return STATUS_POINTS[status]


def _readiness(items: list[CategoryInput]) -> tuple[float, list[str], list[str]]:
    total = 0.0
    count = 0
    critical_missing: list[str] = []
    alerts: list[str] = []
    for category in items:
        for item in category.items:
            points = _points_for_status(item.status)
            if points is None:
                continue
            if item.required:
                total += points
                count += 1
            if item.critical and item.status in {ItemStatus.MISSING, ItemStatus.NOT_PROVIDED}:
                critical_missing.append(item.code)
            if item.status == ItemStatus.PARTIAL:
                alerts.append(item.code)
    readiness = total / count if count else 0.0
    return readiness, critical_missing, alerts


def _select_categories(inputs: list[CategoryInput], allowed: set[str]) -> list[CategoryInput]:
    return [category for category in inputs if category.code in allowed]


def calculate_drs(
    categories: list[CategoryInput],
    mode: str = "PRIVATE",
    rule_package_version: str = "pt-oss-rules-0.1.0",
    case_id: str = "case_unknown",
    tenant_id: str = "tenant_unknown",
) -> DRSResult:
    allowed = {"A", "B", "C", "D", "E", "F"}
    if mode == "PUBLIC":
        allowed = allowed | {"G"}

    selected = _select_categories(categories, allowed)
    quality_categories = [c for c in categories if c.code == "H"]

    category_scores: list[CategoryScore] = []
    weighted_total = 0.0
    weight_total = 0.0
    critical_alerts: list[ValidationAlert] = []

    for code in sorted(allowed):
        category = next((item for item in selected if item.code == code), None)
        if category is None:
            continue
        applicable_items = [item for item in category.items if item.required or item.status == ItemStatus.OUT_OF_SCOPE]
        readiness_total = 0.0
        readiness_count = 0
        for item in applicable_items:
            points = _points_for_status(item.status)
            if points is None:
                continue
            if item.required:
                readiness_total += points
                readiness_count += 1
            if item.critical and item.status in {ItemStatus.MISSING, ItemStatus.NOT_PROVIDED}:
                critical_alerts.append(
                    ValidationAlert(
                        case_id=case_id,
                        tenant_id=tenant_id,
                        severity="HIGH",
                        rule_code=f"CRIT_{code}_{item.code}",
                        message=f"Critical evidence item {item.code} is missing or not provided.",
                        required_action="Review the evidence gap and provide the required document or an explicit justification.",
                        triggered_metric_ids=[],
                    )
                )
        readiness = readiness_total / readiness_count if readiness_count else 0.0
        weight = DEFAULT_CATEGORY_WEIGHTS[code]
        weighted_score = weight * readiness
        category_scores.append(
            CategoryScore(
                code=code,
                readiness=readiness,
                weight=weight,
                weighted_score=weighted_score,
            )
        )
        weighted_total += weighted_score
        weight_total += weight

    drs_value = (weighted_total / weight_total * 100.0) if weight_total else 0.0
    if drs_value >= 70:
        band = ThresholdBand.GO
    elif drs_value >= 50:
        band = ThresholdBand.GO_WITH_CAUTION
    else:
        band = ThresholdBand.NO_GO

    quality_score = None
    if quality_categories:
        q_total = 0.0
        q_count = 0
        for item in quality_categories[0].items:
            points = _points_for_status(item.status)
            if points is None:
                continue
            if item.required:
                q_total += points
                q_count += 1
        quality_score = q_total / q_count if q_count else 0.0

    return DRSResult(
        value=round(drs_value, 2),
        band=band,
        category_scores=category_scores,
        critical_alerts=critical_alerts,
        formula="sum(weighted category scores) / sum(applicable weights) * 100",
        quality_score=quality_score,
    )

