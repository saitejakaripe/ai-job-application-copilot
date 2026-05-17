from __future__ import annotations

from ai_job_application_copilot.models import (
    AnalysisRequest,
    CandidateProfile,
    JobProfile,
    MatchScore,
)
from ai_job_application_copilot.services.text_tools import (
    extract_keywords,
    extract_skills,
    extract_years_of_experience,
    infer_candidate_name,
    infer_company_name,
    infer_role_title,
    infer_seniority,
)


class DeterministicAnalyzer:
    """Rule-based analyzer used by the first production-ready version."""

    def parse_candidate(self, request: AnalysisRequest) -> CandidateProfile:
        return CandidateProfile(
            name=infer_candidate_name(request.resume_text, request.candidate_name),
            skills=extract_skills(request.resume_text),
            keywords=extract_keywords(request.resume_text),
            years_experience=extract_years_of_experience(request.resume_text),
        )

    def parse_job(self, request: AnalysisRequest) -> JobProfile:
        required_skills = extract_skills(request.job_description)
        return JobProfile(
            role_title=infer_role_title(request.job_description, request.role_title),
            company_name=infer_company_name(request.job_description, request.company_name),
            required_skills=required_skills,
            keywords=extract_keywords(request.job_description),
            seniority=infer_seniority(request.job_description),
        )

    def calculate_match(self, candidate: CandidateProfile, job: JobProfile) -> MatchScore:
        required = set(job.required_skills)
        candidate_skills = set(candidate.skills)
        matched = sorted(required & candidate_skills)
        missing = sorted(required - candidate_skills)

        job_keywords = set(job.keywords[:30])
        resume_keywords = set(candidate.keywords[:45])
        keyword_overlap = sorted(job_keywords & resume_keywords)[:12]

        skill_ratio = len(matched) / len(required) if required else 0.0
        keyword_denominator = min(max(len(job_keywords), 1), 12)
        keyword_ratio = min(len(keyword_overlap), keyword_denominator) / keyword_denominator

        experience_bonus = 0.0
        if job.seniority == "senior" and (candidate.years_experience or 0) >= 5:
            experience_bonus = 0.05
        elif job.seniority in {None, "early-career"} and candidate.years_experience is not None:
            experience_bonus = 0.03

        score = round(
            min(1.0, (skill_ratio * 0.72) + (keyword_ratio * 0.23) + experience_bonus) * 100
        )
        explanation = (
            f"Matched {len(matched)} of {len(required)} detected role skills"
            if required
            else "No explicit skills were detected, so keyword overlap drove the score"
        )
        if missing:
            explanation += f"; strongest gaps: {', '.join(missing[:4])}."
        else:
            explanation += "; no major detected skill gaps."

        return MatchScore(
            score=score,
            matched_skills=matched,
            required_skills=sorted(required),
            keyword_overlap=keyword_overlap,
            explanation=explanation,
        )

    def identify_missing_skills(self, candidate: CandidateProfile, job: JobProfile) -> list[str]:
        return sorted(set(job.required_skills) - set(candidate.skills))
