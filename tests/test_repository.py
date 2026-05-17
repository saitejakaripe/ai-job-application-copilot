from __future__ import annotations

from ai_job_application_copilot.db import AnalysisRepository
from ai_job_application_copilot.services.workflow import ApplicationWorkflow


def test_repository_saves_and_fetches_analysis(tmp_path, sample_request) -> None:
    repository = AnalysisRepository(f"sqlite:///{tmp_path / 'copilot.db'}")
    analysis = ApplicationWorkflow().run(sample_request)

    saved = repository.save(sample_request, analysis)
    fetched = repository.get(saved.id or "")
    summaries = repository.list_summaries()

    assert saved.id is not None
    assert fetched == saved
    assert summaries[0].id == saved.id
    assert summaries[0].match_score == saved.match.score

