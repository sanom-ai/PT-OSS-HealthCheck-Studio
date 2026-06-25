from pathlib import Path

from ptoss.models import AssessmentMode
from ptoss.repository import SQLiteCaseRepository
from ptoss.store import InMemoryPTOSSStore


def test_sqlite_repository_roundtrip(tmp_path: Path) -> None:
    repo = SQLiteCaseRepository(tmp_path / "ptoss.db")
    store = InMemoryPTOSSStore(repository=repo)
    case = store.create_case("tenant_1", "Acme", assessment_mode=AssessmentMode.PRIVATE)

    loaded = repo.load_case(case.id)
    assert loaded.id == case.id
    assert loaded.organization.name == "Acme"
    assert loaded.tenant_id == "tenant_1"

