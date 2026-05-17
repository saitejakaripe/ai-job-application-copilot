from __future__ import annotations

from ai_job_application_copilot.agents.state import ApplicationState
from ai_job_application_copilot.models import ApplicationAnalysis
from ai_job_application_copilot.services.analyzer import DeterministicAnalyzer
from ai_job_application_copilot.services.providers import ContentProvider


def parse_inputs_agent(
    state: ApplicationState,
    analyzer: DeterministicAnalyzer,
) -> ApplicationState:
    request = state["request"]
    return {
        "candidate": analyzer.parse_candidate(request),
        "job": analyzer.parse_job(request),
    }


def match_score_agent(state: ApplicationState, analyzer: DeterministicAnalyzer) -> ApplicationState:
    return {"match": analyzer.calculate_match(state["candidate"], state["job"])}


def missing_skills_agent(
    state: ApplicationState,
    analyzer: DeterministicAnalyzer,
) -> ApplicationState:
    return {"missing_skills": analyzer.identify_missing_skills(state["candidate"], state["job"])}


def cover_letter_agent(state: ApplicationState, provider: ContentProvider) -> ApplicationState:
    return {
        "cover_letter": provider.generate_cover_letter(
            state["request"],
            state["candidate"],
            state["job"],
            state["match"],
            state["missing_skills"],
        )
    }


def resume_improvement_agent(
    state: ApplicationState,
    provider: ContentProvider,
) -> ApplicationState:
    return {
        "resume_improvements": provider.suggest_resume_improvements(
            state["request"],
            state["candidate"],
            state["job"],
            state["missing_skills"],
        )
    }


def interview_prep_agent(state: ApplicationState, provider: ContentProvider) -> ApplicationState:
    return {
        "interview_questions": provider.create_interview_questions(
            state["candidate"],
            state["job"],
            state["match"],
            state["missing_skills"],
        )
    }


def assemble_response_agent(state: ApplicationState, provider: ContentProvider) -> ApplicationState:
    candidate = state["candidate"]
    job = state["job"]
    return {
        "analysis": ApplicationAnalysis(
            candidate_name=candidate.name,
            role_title=job.role_title,
            company_name=job.company_name,
            match=state["match"],
            missing_skills=state["missing_skills"],
            cover_letter=state["cover_letter"],
            resume_improvements=state["resume_improvements"],
            interview_questions=state["interview_questions"],
            provider=provider.name,
        )
    }
