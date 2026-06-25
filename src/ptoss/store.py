from __future__ import annotations

from collections import defaultdict

from .models import (
    AssessmentCase,
    AssessmentMode,
    AssessmentScope,
    AuditEvent,
    CaseState,
    CategoryInput,
    EvidenceIndexEntry,
    EvidenceDocument,
    EvidenceMapping,
    EngineRun,
    MetricResult,
    ItemStatus,
    FreshnessStatus,
    Organization,
    ReviewAction,
    ReviewDecision,
    ReviewQueueItem,
    SourceType,
    WorkflowStatus,
    WorkflowStep,
    TierBFileInput,
    TierBScanEstimate,
    TierCFileInput,
    TierCScanEstimate,
    new_id,
)
from .connectors.tier_b import scan_tier_b_files
from .connectors.tier_c import scan_tier_c_files
from .repository import CaseRepository
from .reporting import render_provisional_report
from .rules import calculate_drs


class InMemoryPTOSSStore:
    def __init__(self, repository: CaseRepository | None = None) -> None:
        self.cases: dict[str, AssessmentCase] = {}
        self.case_by_organization: dict[str, str] = {}
        self.repository = repository
        if self.repository is not None:
            for case in self.repository.list_cases():
                self.cases[case.id] = case
                self.case_by_organization[case.organization.id] = case.id

    def create_case(
        self,
        tenant_id: str,
        organization_name: str,
        assessment_mode: AssessmentMode = AssessmentMode.PRIVATE,
    ) -> AssessmentCase:
        organization = Organization(name=organization_name)
        scope = AssessmentScope(assessment_mode=assessment_mode)
        case = AssessmentCase(tenant_id=tenant_id, organization=organization, scope=scope)
        self.cases[case.id] = case
        self.case_by_organization[organization.id] = case.id
        self._audit(case, "CASE_CREATED", to_state=case.state.value)
        self._persist(case)
        return case

    def workflow_snapshot(self, case_id: str) -> dict:
        case = self.get_case(case_id)
        return {
            "case_id": case.id,
            "tenant_id": case.tenant_id,
            "workflow_status": case.workflow_status.value,
            "workflow_step": case.workflow_step.value,
            "workflow_signal_id": case.workflow_signal_id,
            "workflow_error": case.workflow_error,
            "workflow_started_at": case.workflow_started_at,
            "workflow_updated_at": case.workflow_updated_at,
            "case_state": case.state.value,
        }

    def evidence_index(
        self,
        case_id: str,
        tenant_id: str,
        query: str | None = None,
        category: str | None = None,
        freshness_status: FreshnessStatus | str | None = None,
    ) -> list[EvidenceIndexEntry]:
        case = self.get_case(case_id)
        self._ensure_tenant(case, tenant_id)
        normalized_query = query.lower().strip() if query else None
        normalized_freshness = freshness_status.value if isinstance(freshness_status, FreshnessStatus) else freshness_status
        mappings_by_doc = {mapping.evidence_document_id: mapping for mapping in case.evidence_mappings}
        results: list[EvidenceIndexEntry] = []
        for document in case.evidence_documents:
            mapping = mappings_by_doc.get(document.id)
            entry = EvidenceIndexEntry(
                evidence_document_id=document.id,
                case_id=document.case_id,
                tenant_id=document.tenant_id,
                file_name=document.file_name,
                source_type=document.source_type,
                document_type=document.document_type,
                mapped_category=mapping.mapped_category if mapping else None,
                mapping_status=mapping.mapping_status if mapping else None,
                owner=document.owner,
                approver=document.approver,
                revision=document.revision,
                freshness_status=document.freshness_status,
                metadata_completeness=document.metadata_completeness,
                evidence_quality=document.evidence_quality,
                content_hash=document.content_hash,
                source_uri=document.source_uri,
                extracted_text=document.extracted_text,
                created_at=document.created_at,
            )
            if category and entry.mapped_category != category:
                continue
            if normalized_freshness and entry.freshness_status.value != normalized_freshness:
                continue
            if normalized_query:
                haystack = " ".join(
                    part
                    for part in [
                        entry.file_name,
                        entry.document_type or "",
                        entry.mapped_category or "",
                        entry.mapping_status or "",
                        entry.owner or "",
                        entry.approver or "",
                        entry.revision or "",
                        entry.extracted_text or "",
                    ]
                    if part
                ).lower()
                if normalized_query not in haystack:
                    continue
            results.append(entry)
        return results

    def get_case(self, case_id: str) -> AssessmentCase:
        case = self.cases.get(case_id)
        if case is not None:
            return case
        if self.repository is not None:
            case = self.repository.load_case(case_id)
            self.cases[case.id] = case
            self.case_by_organization[case.organization.id] = case.id
            return case
        raise KeyError(case_id)

    def _ensure_tenant(self, case: AssessmentCase, tenant_id: str) -> None:
        if case.tenant_id != tenant_id:
            raise PermissionError("Tenant does not match case.")

    def add_evidence(
        self,
        case_id: str,
        tenant_id: str,
        source_type: SourceType,
        file_name: str,
        content_hash: str,
        document_type: str | None = None,
        source_uri: str | None = None,
        extracted_text: str | None = None,
    ) -> EvidenceDocument:
        case = self.get_case(case_id)
        self._ensure_tenant(case, tenant_id)
        document = EvidenceDocument(
            case_id=case_id,
            tenant_id=tenant_id,
            source_type=source_type,
            file_name=file_name,
            content_hash=content_hash,
            document_type=document_type,
            source_uri=source_uri,
            extracted_text=extracted_text,
            extraction_status="COMPLETED" if extracted_text else "QUEUED",
        )
        case.evidence_documents.append(document)
        case.state = CaseState.EVIDENCE_COLLECTION
        case.evidence_index_version = f"evidx_{len(case.evidence_documents)}"
        self._audit(case, "EVIDENCE_ADDED", metadata={"document_id": document.id})
        self._persist(case)
        return document

    def scan_tier_c_pack(
        self,
        case_id: str,
        tenant_id: str,
        files: list[TierCFileInput | dict],
    ) -> TierCScanEstimate:
        return self.ingest_tier_c_pack(case_id=case_id, tenant_id=tenant_id, files=files)

    def preview_tier_c_pack(
        self,
        files: list[TierCFileInput | dict],
    ) -> TierCScanEstimate:
        normalized_files = [file if isinstance(file, TierCFileInput) else TierCFileInput.model_validate(file) for file in files]
        scan_result = scan_tier_c_files(case_id="preview", tenant_id="preview", files=normalized_files, existing_hashes=set())
        return scan_result.estimate

    def preview_tier_b_folder(
        self,
        files: list[TierBFileInput | dict],
    ) -> TierBScanEstimate:
        normalized_files = [file if isinstance(file, TierBFileInput) else TierBFileInput.model_validate(file) for file in files]
        scan_result = scan_tier_b_files(case_id="preview", tenant_id="preview", files=normalized_files, existing_hashes=set())
        return scan_result.estimate

    def ingest_tier_c_pack(
        self,
        case_id: str,
        tenant_id: str,
        files: list[TierCFileInput | dict],
    ) -> TierCScanEstimate:
        case = self.get_case(case_id)
        self._ensure_tenant(case, tenant_id)
        existing_hashes = {doc.content_hash for doc in case.evidence_documents}
        normalized_files = [file if isinstance(file, TierCFileInput) else TierCFileInput.model_validate(file) for file in files]
        scan_result = scan_tier_c_files(case_id=case_id, tenant_id=tenant_id, files=normalized_files, existing_hashes=existing_hashes)

        for item in scan_result.items:
            case.evidence_documents.append(item.document)
            case.evidence_mappings.append(item.mapping)
            self._audit(
                case,
                "TIER_C_FILE_SCANNED",
                metadata={
                    "document_id": item.document.id,
                    "mapping_id": item.mapping.id,
                    "estimated_pages": item.extracted_pages,
                    "estimated_ocr_pages": item.ocr_pages,
                    "estimated_ai_pages": item.ai_pages,
                },
            )

        if scan_result.items:
            case.state = CaseState.AWAITING_EVIDENCE_REVIEW
            case.workflow_status = WorkflowStatus.WAITING_FOR_REVIEW
            case.workflow_step = WorkflowStep.WAITING_FOR_REVIEW
            case.workflow_started_at = case.workflow_started_at or case.updated_at
            case.workflow_updated_at = case.updated_at
            case.evidence_index_version = f"evidx_{len(case.evidence_documents)}"
            self._persist(case)

        return scan_result.estimate

    def ingest_tier_b_folder(
        self,
        case_id: str,
        tenant_id: str,
        files: list[TierBFileInput | dict],
    ) -> TierBScanEstimate:
        case = self.get_case(case_id)
        self._ensure_tenant(case, tenant_id)
        existing_hashes = {doc.content_hash for doc in case.evidence_documents}
        normalized_files = [file if isinstance(file, TierBFileInput) else TierBFileInput.model_validate(file) for file in files]
        scan_result = scan_tier_b_files(case_id=case_id, tenant_id=tenant_id, files=normalized_files, existing_hashes=existing_hashes)

        for item in scan_result.items:
            case.evidence_documents.append(item.document)
            case.evidence_mappings.append(item.mapping)
            self._audit(
                case,
                "TIER_B_FILE_SCANNED",
                metadata={
                    "document_id": item.document.id,
                    "mapping_id": item.mapping.id,
                    "sync_status": scan_result.estimate.sync_status,
                    "estimated_metadata_confidence": scan_result.estimate.estimated_metadata_confidence,
                },
            )

        if scan_result.items:
            case.state = CaseState.AWAITING_EVIDENCE_REVIEW
            case.workflow_status = WorkflowStatus.WAITING_FOR_REVIEW
            case.workflow_step = WorkflowStep.WAITING_FOR_REVIEW
            case.workflow_started_at = case.workflow_started_at or case.updated_at
            case.workflow_updated_at = case.updated_at
            case.evidence_index_version = f"evidx_{len(case.evidence_documents)}"
            self._persist(case)

        return scan_result.estimate

    def review_board_queue(self, case_id: str) -> list[ReviewQueueItem]:
        case = self.get_case(case_id)
        documents_by_id = {doc.id: doc for doc in case.evidence_documents}
        queue: list[ReviewQueueItem] = []
        for mapping in case.evidence_mappings:
            if mapping.mapping_status not in {"AUTO_SUGGESTED", "REMAP_PENDING"}:
                continue
            document = documents_by_id.get(mapping.evidence_document_id)
            queue.append(
                ReviewQueueItem(
                    mapping_id=mapping.id,
                    evidence_document_id=mapping.evidence_document_id,
                    file_name=document.file_name if document else mapping.evidence_document_id,
                    mapped_category=mapping.mapped_category,
                    mapping_status=mapping.mapping_status,
                    mapping_method=mapping.mapping_method,
                    confidence=mapping.confidence,
                    document_type=document.document_type if document else None,
                    freshness_status=document.freshness_status if document else FreshnessStatus.UNKNOWN_FRESHNESS,
                    review_note=mapping.review_note,
                )
            )
        return queue

    def apply_review_decisions(
        self,
        case_id: str,
        tenant_id: str,
        reviewer_id: str,
        decisions: list[ReviewDecision | dict],
    ) -> list[EvidenceMapping]:
        case = self.get_case(case_id)
        self._ensure_tenant(case, tenant_id)
        case.state = CaseState.REVIEW_IN_PROGRESS
        updated: list[EvidenceMapping] = []
        mapping_index = {mapping.id: mapping for mapping in case.evidence_mappings}
        for raw in decisions:
            decision = raw if isinstance(raw, ReviewDecision) else ReviewDecision.model_validate(raw)
            mapping = mapping_index.get(decision.mapping_id)
            if mapping is None:
                continue
            previous_status = mapping.mapping_status
            previous_category = mapping.mapped_category
            if decision.action == ReviewAction.CONFIRM:
                mapping.mapping_status = "HUMAN_CONFIRMED"
            elif decision.action == ReviewAction.REJECT:
                mapping.mapping_status = "REJECTED"
            elif decision.action == ReviewAction.REMAP:
                mapping.mapping_status = "REMAPPED"
                if decision.mapped_category:
                    mapping.mapped_category = decision.mapped_category
            elif decision.action == ReviewAction.MARK_MISSING:
                mapping.mapping_status = "MARKED_MISSING"
            elif decision.action == ReviewAction.MARK_PARTIAL:
                mapping.mapping_status = "MARKED_PARTIAL"
            elif decision.action == ReviewAction.MARK_DUPLICATE:
                mapping.mapping_status = "MARKED_DUPLICATE"
            elif decision.action == ReviewAction.SELECT_LATEST_APPROVED:
                mapping.mapping_status = "LATEST_APPROVED_SELECTED"
            elif decision.action == ReviewAction.MARK_OUT_OF_SCOPE:
                mapping.mapping_status = "OUT_OF_SCOPE"
            if decision.review_note:
                mapping.review_note = decision.review_note
            updated.append(mapping)
            self._audit(
                case,
                "REVIEW_DECISION_APPLIED",
                user_id=reviewer_id,
                metadata={
                    "mapping_id": mapping.id,
                    "decision": decision.action.value,
                    "from_status": previous_status,
                    "to_status": mapping.mapping_status,
                    "from_category": previous_category,
                    "to_category": mapping.mapped_category,
                },
            )
        case.state = CaseState.REVIEW_SUBMITTED
        self._persist(case)
        return updated

    def map_evidence(
        self,
        case_id: str,
        tenant_id: str,
        evidence_document_id: str,
        mapped_category: str,
        mapping_method: str,
        confidence: float,
        review_note: str | None = None,
        mapped_to_metrics: list[str] | None = None,
    ) -> EvidenceMapping:
        case = self.get_case(case_id)
        mapping = EvidenceMapping(
            case_id=case_id,
            tenant_id=tenant_id,
            evidence_document_id=evidence_document_id,
            mapped_category=mapped_category,
            mapping_status="AUTO_SUGGESTED",
            mapping_method=mapping_method,
            confidence=confidence,
            review_note=review_note,
            mapped_to_metrics=mapped_to_metrics or [],
        )
        case.evidence_mappings.append(mapping)
        self._audit(case, "EVIDENCE_MAPPED", metadata={"mapping_id": mapping.id})
        self._persist(case)
        return mapping

    def submit_review(
        self,
        case_id: str,
        tenant_id: str,
        reviewer_id: str,
        decisions: list[dict],
    ) -> list[dict]:
        return self.signal_review_submission(
            case_id=case_id,
            tenant_id=tenant_id,
            reviewer_id=reviewer_id,
            decisions=decisions,
        )

    def signal_review_submission(
        self,
        case_id: str,
        tenant_id: str,
        reviewer_id: str,
        decisions: list[ReviewDecision | dict],
        signal_id: str | None = None,
        auto_advance: bool = True,
    ) -> list[dict]:
        case = self.get_case(case_id)
        self._ensure_tenant(case, tenant_id)
        case.workflow_status = WorkflowStatus.ADVANCING
        case.workflow_step = WorkflowStep.REVIEW_SIGNAL_RECEIVED
        case.workflow_signal_id = signal_id or new_id("signal")
        case.workflow_updated_at = case.updated_at
        self._audit(
            case,
            "WORKFLOW_SIGNAL_RECEIVED",
            user_id=reviewer_id,
            metadata={"signal_id": case.workflow_signal_id, "signal_type": "EvidenceReviewSubmitted"},
        )
        updated = self.apply_review_decisions(
            case_id=case_id,
            tenant_id=tenant_id,
            reviewer_id=reviewer_id,
            decisions=decisions,
        )
        if auto_advance:
            self.advance_workflow_after_review(case_id=case_id, tenant_id=tenant_id, reviewer_id=reviewer_id)
        return [
            {
                "mapping_id": mapping.id,
                "mapped_category": mapping.mapped_category,
                "mapping_status": mapping.mapping_status,
                "review_note": mapping.review_note,
            }
            for mapping in updated
        ]

    def advance_workflow_after_review(self, case_id: str, tenant_id: str, reviewer_id: str | None = None) -> dict:
        case = self.get_case(case_id)
        self._ensure_tenant(case, tenant_id)
        pending = self.review_board_queue(case_id)
        if pending:
            case.workflow_status = WorkflowStatus.WAITING_FOR_REVIEW
            case.workflow_step = WorkflowStep.WAITING_FOR_REVIEW
            case.workflow_updated_at = case.updated_at
            self._audit(case, "WORKFLOW_WAITING_FOR_REVIEW", user_id=reviewer_id, metadata={"pending_items": len(pending)})
            self._persist(case)
            return self.workflow_snapshot(case_id)

        case.workflow_status = WorkflowStatus.RUNNING
        case.workflow_step = WorkflowStep.DRS_COMPUTED
        case.workflow_updated_at = case.updated_at
        self._persist(case)
        self.compute_drs(case_id=case_id, tenant_id=tenant_id)
        case.workflow_step = WorkflowStep.REPORT_GENERATED
        self._persist(case)
        self.generate_report(case_id=case_id, tenant_id=tenant_id)
        case.workflow_status = WorkflowStatus.COMPLETED
        case.workflow_updated_at = case.updated_at
        self._audit(case, "WORKFLOW_COMPLETED", user_id=reviewer_id, metadata={"signal_id": case.workflow_signal_id})
        self._persist(case)
        return self.workflow_snapshot(case_id)

    def resume_workflow(self, case_id: str, tenant_id: str, reviewer_id: str | None = None) -> dict:
        case = self.get_case(case_id)
        self._ensure_tenant(case, tenant_id)
        if case.reports:
            case.workflow_status = WorkflowStatus.COMPLETED
            case.workflow_step = WorkflowStep.REPORT_GENERATED
            case.workflow_updated_at = case.updated_at
            self._persist(case)
            return self.workflow_snapshot(case_id)
        if any(metric.metric_code == "DRS" for metric in case.metric_results):
            case.workflow_status = WorkflowStatus.RUNNING
            case.workflow_step = WorkflowStep.DRS_COMPUTED
            case.workflow_updated_at = case.updated_at
            self._persist(case)
            self.generate_report(case_id=case_id, tenant_id=tenant_id)
            case.workflow_status = WorkflowStatus.COMPLETED
            case.workflow_step = WorkflowStep.REPORT_GENERATED
            case.workflow_updated_at = case.updated_at
            self._audit(case, "WORKFLOW_RESUMED", user_id=reviewer_id, metadata={"resume_path": "REPORT"})
            self._persist(case)
            return self.workflow_snapshot(case_id)
        if case.workflow_status in {WorkflowStatus.WAITING_FOR_REVIEW, WorkflowStatus.ADVANCING}:
            return self.advance_workflow_after_review(case_id=case_id, tenant_id=tenant_id, reviewer_id=reviewer_id)
        return self.workflow_snapshot(case_id)

    def compute_drs(self, case_id: str, tenant_id: str, engine_version: str = "ptoss-engine-0.1.0"):
        case = self.get_case(case_id)
        self._ensure_tenant(case, tenant_id)
        if any(mapping.mapping_status in {"AUTO_SUGGESTED", "REMAP_PENDING"} for mapping in case.evidence_mappings):
            raise ValueError("Evidence review must be submitted before DRS computation.")
        case.state = CaseState.DRS_RUNNING
        categories = self._build_category_inputs(case)
        drs_result = calculate_drs(
            categories=categories,
            mode=case.scope.assessment_mode.value,
            rule_package_version=case.rule_package_version,
            case_id=case.id,
            tenant_id=tenant_id,
        )
        run = EngineRun(
            case_id=case.id,
            tenant_id=tenant_id,
            rule_package_version=case.rule_package_version,
            evidence_index_version=case.evidence_index_version,
            engine_version=engine_version,
            mode=case.scope.assessment_mode,
        )
        case.engine_runs.append(run)
        case.metric_results.append(
            MetricResult(
                case_id=case.id,
                tenant_id=tenant_id,
                metric_code="DRS",
                metric_name="Document Readiness Score",
                value=drs_result.value,
                unit="PERCENT",
                threshold_band=drs_result.band,
                status=drs_result.band.value,
                formula=drs_result.formula,
                confidence="MEDIUM" if drs_result.critical_alerts else "HIGH",
                error_margin="+/-10%",
                rule_package_version=case.rule_package_version,
                engine_run_id=run.id,
            )
        )
        case.validation_alerts.extend(drs_result.critical_alerts)
        case.state = CaseState.DRS_READY
        self._audit(case, "DRS_COMPUTED", metadata={"engine_run_id": run.id, "drs": drs_result.value})
        self._persist(case)
        return drs_result, run

    def generate_report(self, case_id: str, tenant_id: str, engine_version: str = "ptoss-engine-0.1.0"):
        case = self.get_case(case_id)
        self._ensure_tenant(case, tenant_id)
        latest_metric = next((metric for metric in reversed(case.metric_results) if metric.metric_code == "DRS"), None)
        if latest_metric is None:
            drs_result, _ = self.compute_drs(case_id, tenant_id, engine_version=engine_version)
        else:
            class _DRSProxy:
                value = latest_metric.value
                band = latest_metric.threshold_band
                critical_alerts = case.validation_alerts

            drs_result = _DRSProxy()
        report = render_provisional_report(case, drs_result, engine_version=engine_version)
        case.reports.append(report)
        case.state = CaseState.REPORT_READY
        self._audit(case, "REPORT_GENERATED", metadata={"report_id": report.id})
        self._persist(case)
        return report

    def _build_category_inputs(self, case: AssessmentCase) -> list[CategoryInput]:
        by_category: dict[str, list] = defaultdict(list)
        for mapping in case.evidence_mappings:
            if mapping.mapping_status in {"REJECTED"}:
                continue
            by_category[mapping.mapped_category].append(mapping)

        categories: list[CategoryInput] = []
        for code in ["A", "B", "C", "D", "E", "F", "G", "H"]:
            items = []
            for mapping in by_category.get(code, []):
                status = self._status_from_mapping(mapping.mapping_status, mapping.confidence)
                items.append(
                    {
                        "code": mapping.evidence_document_id,
                        "status": status,
                        "required": True,
                        "critical": code in {"A", "B", "D"},
                    }
                )
            if not items and code != "H":
                items.append(
                    {
                        "code": f"{code}_PLACEHOLDER",
                        "status": ItemStatus.MISSING,
                        "required": True,
                        "critical": code in {"A", "B", "D"},
                    }
                )
            if code == "H":
                items.append(
                    {
                        "code": "H_PLACEHOLDER",
                        "status": ItemStatus.AVAILABLE if case.evidence_documents else ItemStatus.MISSING,
                        "required": True,
                        "critical": False,
                    }
                )
            categories.append(
                CategoryInput(
                    code=code,
                    items=items,
                )
            )
        return categories

    def _status_from_mapping(self, mapping_status: str, confidence: float) -> ItemStatus:
        if mapping_status in {"OUT_OF_SCOPE"}:
            return ItemStatus.OUT_OF_SCOPE
        if mapping_status in {"MARKED_MISSING", "REJECTED"}:
            return ItemStatus.MISSING
        if mapping_status in {"MARKED_PARTIAL"}:
            return ItemStatus.PARTIAL
        if mapping_status in {"MARKED_DUPLICATE"}:
            return ItemStatus.MISSING
        if mapping_status in {"HUMAN_CONFIRMED", "LATEST_APPROVED_SELECTED", "REMAPPED"}:
            return ItemStatus.AVAILABLE if confidence >= 0.75 else ItemStatus.PARTIAL
        return ItemStatus.AVAILABLE if confidence >= 0.75 else ItemStatus.PARTIAL

    def _audit(
        self,
        case: AssessmentCase,
        event_type: str,
        user_id: str | None = None,
        from_state: str | None = None,
        to_state: str | None = None,
        metadata: dict | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            tenant_id=case.tenant_id,
            case_id=case.id,
            user_id=user_id,
            event_type=event_type,
            from_state=from_state,
            to_state=to_state,
            metadata=metadata or {},
        )
        case.audit_events.append(event)
        case.updated_at = event.timestamp
        self._persist(case)
        return event

    def _persist(self, case: AssessmentCase) -> None:
        if self.repository is not None:
            self.repository.save_case(case)
