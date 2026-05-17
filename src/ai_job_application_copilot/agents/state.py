from __future__ import annotations

from typing import TypedDict

from ai_job_application_copilot.models import (
    AnalysisRequest,
    ApplicationAnalysis,
    CandidateProfile,
    InterviewQuestion,
    JobProfile,
    MatchScore,
    ResumeImprovement,
)


class ApplicationState(TypedDict, total=False):
    request: AnalysisRequest
    candidate: CandidateProfile
    job: JobProfile
    match: MatchScore
    missing_skills: list[str]
    cover_letter: str
    resume_improvements: list[ResumeImprovement]
    interview_questions: list[InterviewQuestion]
    analysis: ApplicationAnalysis

