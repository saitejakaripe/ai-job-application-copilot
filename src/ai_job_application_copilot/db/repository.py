from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from ai_job_application_copilot.models import AnalysisRequest, AnalysisSummary, ApplicationAnalysis


class AnalysisRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.database_path = sqlite_path_from_url(database_url)

    def init_db(self) -> None:
        self._ensure_parent_dir()
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    candidate_name TEXT NOT NULL,
                    role_title TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    match_score INTEGER NOT NULL,
                    request_json TEXT NOT NULL,
                    result_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC)"
            )

    def save(self, request: AnalysisRequest, analysis: ApplicationAnalysis) -> ApplicationAnalysis:
        self.init_db()
        analysis_id = analysis.id or str(uuid4())
        saved = analysis.model_copy(update={"id": analysis_id})
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO analyses (
                    id, created_at, candidate_name, role_title, company_name, match_score,
                    request_json, result_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    saved.id,
                    saved.created_at.isoformat(),
                    saved.candidate_name,
                    saved.role_title,
                    saved.company_name,
                    saved.match.score,
                    request.model_dump_json(),
                    saved.model_dump_json(),
                ),
            )
        return saved

    def get(self, analysis_id: str) -> ApplicationAnalysis | None:
        self.init_db()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT result_json FROM analyses WHERE id = ?",
                (analysis_id,),
            ).fetchone()
        if row is None:
            return None
        return ApplicationAnalysis.model_validate_json(row["result_json"])

    def list_summaries(self, limit: int = 20) -> list[AnalysisSummary]:
        self.init_db()
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at, candidate_name, role_title, company_name, match_score
                FROM analyses
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [AnalysisSummary.model_validate(dict(row)) for row in rows]

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _ensure_parent_dir(self) -> None:
        if self.database_path == ":memory:":
            return
        Path(self.database_path).expanduser().parent.mkdir(parents=True, exist_ok=True)


def sqlite_path_from_url(database_url: str) -> str:
    if database_url == "sqlite:///:memory:":
        return ":memory:"
    if database_url.startswith("sqlite:///"):
        return database_url.removeprefix("sqlite:///")
    if database_url.startswith("sqlite://"):
        return database_url.removeprefix("sqlite://")
    return database_url
