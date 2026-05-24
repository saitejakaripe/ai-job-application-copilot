from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AnalysisRequest(BaseModel):
    """Input payload for a job application analysis."""

    resume_text: str = Field(..., min_length=50, description="Plain text resume content.")
    job_description: str = Field(..., min_length=50, description="Plain text job description.")
    candidate_name: str | None = Field(None, max_length=120)
    role_title: str | None = Field(None, max_length=160)
    company_name: str | None = Field(None, max_length=160)
    persist: bool = Field(True, description="Persist the analysis to SQLite.")
    tags: list[str] = Field(default_factory=list, max_length=12)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "candidate_name": "Avery Patel",
                "role_title": "AI Automation Engineer",
                "company_name": "Northstar Robotics",
                "resume_text": "Avery Patel\nPython engineer with FastAPI, Docker, SQL, "
                "pytest, GitHub Actions, and LangChain experience...",
                "job_description": "We need an AI Automation Engineer with Python, "
                "FastAPI, LangGraph, Docker, SQLite, CI/CD, and LLM integration experience...",
                "persist": True,
                "tags": ["backend", "ai-automation"],
            }
        }
    )

    @field_validator("resume_text", "job_description")
    @classmethod
    def require_word_rich_text(cls, value: str) -> str:
        cleaned = value.strip()
        if len(re.findall(r"[A-Za-z][A-Za-z0-9+#./-]*", cleaned)) < 12:
            raise ValueError("Text must contain enough words for deterministic analysis.")
        return cleaned

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: list[str]) -> list[str]:
        normalized = []
        for tag in value:
            clean = re.sub(r"[^a-z0-9-]+", "-", tag.lower()).strip("-")
            if clean and clean not in normalized:
                normalized.append(clean)
        return normalized[:12]


class CandidateProfile(BaseModel):
    name: str
    skills: list[str]
    keywords: list[str]
    years_experience: int | None = None


class ResumeProfileRequest(BaseModel):
    """Input payload for standalone resume analysis."""

    resume_text: str = Field(..., min_length=50, description="Plain text resume content.")
    candidate_name: str | None = Field(None, max_length=120)

    @field_validator("resume_text")
    @classmethod
    def require_word_rich_resume(cls, value: str) -> str:
        cleaned = value.strip()
        if len(re.findall(r"[A-Za-z][A-Za-z0-9+#./-]*", cleaned)) < 12:
            raise ValueError("Resume text must contain enough words for analysis.")
        return cleaned


class ResumeProfile(BaseModel):
    candidate_name: str
    skills: list[str]
    education: list[str]
    projects: list[str]
    certifications: list[str]
    work_experience: list[str]
    technical_tools: list[str]
    keywords: list[str]
    years_experience: int | None = None
    suitable_roles: list[str]


class JobProfile(BaseModel):
    role_title: str
    company_name: str
    required_skills: list[str]
    keywords: list[str]
    seniority: str | None = None


class MatchScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    matched_skills: list[str]
    required_skills: list[str]
    keyword_overlap: list[str]
    explanation: str


class ResumeImprovement(BaseModel):
    priority: Literal["high", "medium", "low"]
    section: str
    recommendation: str
    rationale: str
    missing_skill: str | None = None


class InterviewQuestion(BaseModel):
    category: Literal["technical", "behavioral", "company", "gap"]
    question: str
    why_it_matters: str


class ApplicationAnalysis(BaseModel):
    id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    candidate_name: str
    role_title: str
    company_name: str
    match: MatchScore
    missing_skills: list[str]
    cover_letter: str
    resume_improvements: list[ResumeImprovement]
    interview_questions: list[InterviewQuestion]
    provider: str = "deterministic"
    workflow_version: str = "0.1.0"


class AnalysisSummary(BaseModel):
    id: str
    created_at: datetime
    candidate_name: str
    role_title: str
    company_name: str
    match_score: int


CandidateLevel = Literal["fresher", "intern", "experienced"]
JobTypePreference = Literal["Internship", "Full-time", "Part-time", "Contract", "Remote"]
MarketScope = Literal["india", "abroad", "both"]


class JobSearchPreferences(BaseModel):
    candidate_level: CandidateLevel
    years_experience: int | None = Field(None, ge=0, le=50)
    job_types: list[JobTypePreference] = Field(default_factory=lambda: ["Full-time"])
    locations: list[str] = Field(default_factory=lambda: ["Remote"])
    custom_location: str | None = Field(None, max_length=120)
    interested_roles: list[str] = Field(default_factory=list, max_length=12)
    open_to_relocation: bool = False
    expected_salary_min_lpa: float | None = Field(None, ge=0, le=500)
    expected_salary_max_lpa: float | None = Field(None, ge=0, le=500)
    market_scope: MarketScope = "both"
    min_match_percentage: int = Field(40, ge=0, le=100)
    skill_filters: list[str] = Field(default_factory=list, max_length=20)
    source_filters: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("job_types")
    @classmethod
    def require_job_type(cls, value: list[JobTypePreference]) -> list[JobTypePreference]:
        return _dedupe_non_empty(value) or ["Full-time"]

    @field_validator("locations", "interested_roles", "skill_filters", "source_filters")
    @classmethod
    def normalize_string_lists(cls, value: list[str]) -> list[str]:
        return _dedupe_non_empty(value)

    @model_validator(mode="after")
    def validate_salary_range(self) -> JobSearchPreferences:
        if (
            self.expected_salary_min_lpa is not None
            and self.expected_salary_max_lpa is not None
            and self.expected_salary_min_lpa > self.expected_salary_max_lpa
        ):
            raise ValueError("Minimum salary cannot be greater than maximum salary.")
        return self


class JobRecommendationRequest(BaseModel):
    resume_text: str | None = Field(None, min_length=50)
    profile: ResumeProfile | None = None
    preferences: JobSearchPreferences

    @model_validator(mode="after")
    def require_resume_or_profile(self) -> JobRecommendationRequest:
        if self.profile is None and not self.resume_text:
            raise ValueError("Provide either resume_text or a previously analyzed resume profile.")
        return self


class JobRecommendation(BaseModel):
    id: str
    job_title: str
    company_name: str
    location: str
    country: str
    job_type: str
    required_experience: str
    required_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    resume_match_percentage: int = Field(..., ge=0, le=100)
    match_reason: str
    direct_apply_link: str
    source_website: str
    salary_range: str | None = None
    is_remote: bool = False
    region: Literal["india", "global"] = "india"


class ResumeImprovementBundle(BaseModel):
    missing_skills: list[str]
    keywords_to_add: list[str]
    project_suggestions: list[str]
    certification_suggestions: list[str]
    ats_suggestions: list[str]


class SourceLink(BaseModel):
    label: str
    url: str
    region: Literal["india", "global"]


class ApplicationLink(BaseModel):
    label: str
    url: str
    source_website: str
    role: str
    location: str
    job_type: str
    region: Literal["india", "global"]
    is_remote: bool = False


class JobRecommendationResponse(BaseModel):
    profile: ResumeProfile
    preferences: JobSearchPreferences
    jobs: list[JobRecommendation]
    resume_improvements: ResumeImprovementBundle
    source_links: list[SourceLink]
    application_links: list[ApplicationLink]
    total_matches: int = Field(..., ge=0)
    returned_matches: int = Field(..., ge=0)
    generated_application_links_count: int = Field(..., ge=0)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


def _dedupe_non_empty(values: list[str]) -> list[str]:
    normalized: list[str] = []
    for item in values:
        clean = item.strip()
        if clean and clean not in normalized:
            normalized.append(clean)
    return normalized
