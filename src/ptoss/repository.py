from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import AssessmentCase


class CaseRepository:
    def save_case(self, case: AssessmentCase) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def load_case(self, case_id: str) -> AssessmentCase:  # pragma: no cover - interface
        raise NotImplementedError

    def list_cases(self) -> list[AssessmentCase]:  # pragma: no cover - interface
        raise NotImplementedError


class SQLiteCaseRepository(CaseRepository):
    def __init__(self, db_path: str | Path = "ptoss.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS assessment_case (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_event (
                    id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save_case(self, case: AssessmentCase) -> None:
        payload = case.model_dump(mode="json")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO assessment_case (id, tenant_id, payload, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    tenant_id=excluded.tenant_id,
                    payload=excluded.payload,
                    updated_at=excluded.updated_at
                """,
                (case.id, case.tenant_id, json.dumps(payload), case.updated_at if hasattr(case, "updated_at") else ""),
            )
            conn.commit()

    def load_case(self, case_id: str) -> AssessmentCase:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM assessment_case WHERE id = ?", (case_id,)).fetchone()
        if row is None:
            raise KeyError(case_id)
        return AssessmentCase.model_validate(json.loads(row["payload"]))

    def list_cases(self) -> list[AssessmentCase]:
        with self._connect() as conn:
            rows = conn.execute("SELECT payload FROM assessment_case ORDER BY updated_at DESC").fetchall()
        return [AssessmentCase.model_validate(json.loads(row["payload"])) for row in rows]

