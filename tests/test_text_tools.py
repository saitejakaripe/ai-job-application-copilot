from __future__ import annotations

from ai_job_application_copilot.services.text_tools import extract_keywords, extract_skills


def test_extract_skills_normalizes_common_aliases() -> None:
    text = "Built Fast API services, CI/CD pipelines, k8s jobs, and Lang Graph agents in Python."

    skills = extract_skills(text)

    assert "fastapi" in skills
    assert "ci/cd" in skills
    assert "kubernetes" in skills
    assert "langgraph" in skills
    assert "python" in skills


def test_extract_keywords_removes_stopwords() -> None:
    keywords = extract_keywords("The Python automation service improves automation for the team.")

    assert keywords[0] == "automation"
    assert "the" not in keywords

