from __future__ import annotations

from ai_job_application_copilot.services.workflow import ApplicationWorkflow


def test_workflow_returns_complete_analysis(sample_request) -> None:
    analysis = ApplicationWorkflow().run(sample_request)

    assert analysis.candidate_name == "Avery Patel"
    assert analysis.role_title == "AI Automation Engineer"
    assert analysis.company_name == "Northstar Robotics"
    assert analysis.match.score >= 60
    assert "python" in analysis.match.matched_skills
    assert "langgraph" in analysis.missing_skills
    assert "Dear Northstar Robotics" in analysis.cover_letter
    assert analysis.resume_improvements
    assert analysis.interview_questions

