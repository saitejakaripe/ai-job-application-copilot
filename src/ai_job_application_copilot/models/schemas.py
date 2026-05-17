from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

