from __future__ import annotations

from .models import AssessmentMode, SourceType
from .reporting import render_provisional_report
from .repository import CaseRepository, SQLiteCaseRepository
from .store import InMemoryPTOSSStore


class PTOSSService:
    def __init__(self, repository: CaseRepository | None = None) -> None:
        self.repository = repository or SQLiteCaseRepository()
        self.memory = InMemoryPTOSSStore()

    def create_case(self, tenant_id: str, organization_name: str, assessment_mode: AssessmentMode):
        case = self.memory.create_case(tenant_id, organization_name, assessment_mode)
        self.repository.save_case(case)
        return case

    def add_evidence(self, *args, **kwargs):
        evidence = self.memory.add_evidence(*args, **kwargs)
        case = self.memory.get_case(kwargs["case_id"] if "case_id" in kwargs else args[0])
        self.repository.save_case(case)
        return evidence

    def map_evidence(self, *args, **kwargs):
        mapping = self.memory.map_evidence(*args, **kwargs)
        case = self.memory.get_case(kwargs["case_id"] if "case_id" in kwargs else args[0])
        self.repository.save_case(case)
        return mapping

    def submit_review(self, *args, **kwargs):
        result = self.memory.submit_review(*args, **kwargs)
        case = self.memory.get_case(kwargs["case_id"] if "case_id" in kwargs else args[0])
        self.repository.save_case(case)
        return result

    def compute_drs(self, *args, **kwargs):
        drs_result, run = self.memory.compute_drs(*args, **kwargs)
        case = self.memory.get_case(kwargs["case_id"] if "case_id" in kwargs else args[0])
        self.repository.save_case(case)
        return drs_result, run

    def generate_report(self, *args, **kwargs):
        report = self.memory.generate_report(*args, **kwargs)
        case = self.memory.get_case(kwargs["case_id"] if "case_id" in kwargs else args[0])
        self.repository.save_case(case)
        return report

