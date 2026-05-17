from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from ai_job_application_copilot.core.config import get_settings
from ai_job_application_copilot.main import create_app
from ai_job_application_copilot.models import AnalysisRequest


@pytest.fixture
def sample_resume() -> str:
    return """
    Avery Patel
    Backend automation engineer with 6 years of Python experience building FastAPI services,
    REST APIs, SQL data workflows, Docker deployments, pytest suites, GitHub Actions pipelines,
    and observability dashboards. Delivered production automation that saved 25 hours per week
    and improved incident response with structured logging and metrics.
    """


@pytest.fixture
def sample_job_description() -> str:
    return """
    Company: Northstar Robotics
    Role: AI Automation Engineer
    We are looking for an engineer to build Python FastAPI services with LangGraph workflows,
    SQLite persistence, Docker packaging, CI/CD automation, pytest coverage, and OpenAI or
    LLM provider extension points. Experience with observability and REST API design is valued.
    """


@pytest.fixture
def sample_request(sample_resume: str, sample_job_description: str) -> AnalysisRequest:
    return AnalysisRequest(
        resume_text=sample_resume,
        job_description=sample_job_description,
        candidate_name="Avery Patel",
        role_title="AI Automation Engineer",
        company_name="Northstar Robotics",
    )


@pytest.fixture
def client(tmp_path, monkeypatch) -> TestClient:
    monkeypatch.setenv("AI_COPILOT_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    get_settings.cache_clear()
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
    get_settings.cache_clear()

