from __future__ import annotations

from typing import Protocol

from ai_job_application_copilot.models import (
    AnalysisRequest,
    CandidateProfile,
    InterviewQuestion,
    JobProfile,
    MatchScore,
    ResumeImprovement,
)


class ContentProvider(Protocol):
    name: str

    def generate_cover_letter(
        self,
        request: AnalysisRequest,
        candidate: CandidateProfile,
        job: JobProfile,
        match: MatchScore,
        missing_skills: list[str],
    ) -> str:
        ...

    def suggest_resume_improvements(
        self,
        request: AnalysisRequest,
        candidate: CandidateProfile,
        job: JobProfile,
        missing_skills: list[str],
    ) -> list[ResumeImprovement]:
        ...

    def create_interview_questions(
        self,
        candidate: CandidateProfile,
        job: JobProfile,
        match: MatchScore,
        missing_skills: list[str],
    ) -> list[InterviewQuestion]:
        ...


class DeterministicContentProvider:
    """Template-based content provider for repeatable tests and no-key local use."""

    name = "deterministic"

    def generate_cover_letter(
        self,
        request: AnalysisRequest,
        candidate: CandidateProfile,
        job: JobProfile,
        match: MatchScore,
        missing_skills: list[str],
    ) -> str:
        matched = _join_human(match.matched_skills[:5]) or "the core backend requirements"
        gaps = _join_human(missing_skills[:3])
        gap_sentence = (
            f"I also noticed the role values {gaps}; I would close those gaps quickly through "
            "hands-on delivery and focused onboarding."
            if gaps
            else (
                "The detected requirements align closely with the experience represented in "
                "my resume."
            )
        )
        company = job.company_name if job.company_name != "the hiring team" else "your team"

        return "\n\n".join(
            [
                f"Dear {company},",
                f"I am excited to apply for the {job.role_title} role. My background combines "
                f"{matched}, and I have a track record of turning ambiguous automation needs into "
                "testable, maintainable systems.",
                f"For this role, I would emphasize the projects in my resume that map to your "
                f"highest-signal requirements: {matched}. The deterministic match score is "
                f"{match.score}/100, which gives me a clear view of where my application "
                "is already strong and where it should be sharpened.",
                gap_sentence,
                "Thank you for your time and consideration. I would welcome the chance to discuss "
                "how I can help build reliable AI-enabled workflows with clear engineering "
                "discipline.",
                f"Sincerely,\n{candidate.name}",
            ]
        )

    def suggest_resume_improvements(
        self,
        request: AnalysisRequest,
        candidate: CandidateProfile,
        job: JobProfile,
        missing_skills: list[str],
    ) -> list[ResumeImprovement]:
        improvements: list[ResumeImprovement] = []
        for skill in missing_skills[:5]:
            improvements.append(
                ResumeImprovement(
                    priority="high",
                    section="Skills and Projects",
                    recommendation=(
                        f"Add a concrete bullet that demonstrates {skill} if you have real "
                        "experience with it; otherwise keep it out of the skills list and "
                        "prepare a learning plan."
                    ),
                    rationale=(
                        f"The job description explicitly signals {skill}, but it was not "
                        "detected in the resume."
                    ),
                    missing_skill=skill,
                )
            )

        if not any(char.isdigit() for char in request.resume_text):
            improvements.append(
                ResumeImprovement(
                    priority="medium",
                    section="Experience",
                    recommendation=(
                        "Add measurable outcomes such as latency reduced, hours saved, model "
                        "accuracy, deployment frequency, cost reduction, or user adoption."
                    ),
                    rationale="Quantified bullets make the match stronger and easier to verify.",
                )
            )

        role_keywords = [
            keyword for keyword in job.keywords[:10] if keyword not in candidate.keywords
        ]
        if role_keywords:
            improvements.append(
                ResumeImprovement(
                    priority="medium",
                    section="Summary",
                    recommendation=(
                        "Mirror the role language naturally in the summary, especially: "
                        f"{', '.join(role_keywords[:5])}."
                    ),
                    rationale=(
                        "Applicant tracking systems and recruiters both reward relevant "
                        "terminology."
                    ),
                )
            )

        improvements.append(
            ResumeImprovement(
                priority="low",
                section="Cover Letter",
                recommendation=(
                    f"Open with a direct connection to the {job.role_title} role and one "
                    "proof point from the strongest matched skill."
                ),
                rationale="A concise role-specific opening improves recruiter scanning.",
            )
        )
        return improvements[:8]

    def create_interview_questions(
        self,
        candidate: CandidateProfile,
        job: JobProfile,
        match: MatchScore,
        missing_skills: list[str],
    ) -> list[InterviewQuestion]:
        questions: list[InterviewQuestion] = []
        role_article = _article_for(job.role_title)
        for skill in match.matched_skills[:4]:
            questions.append(
                InterviewQuestion(
                    category="technical",
                    question=(
                        f"Walk me through a project where you used {skill} to solve a "
                        "production problem."
                    ),
                    why_it_matters="This validates depth behind a matched resume skill.",
                )
            )

        for skill in missing_skills[:3]:
            questions.append(
                InterviewQuestion(
                    category="gap",
                    question=(
                        f"This role mentions {skill}. What adjacent experience would help "
                        "you ramp up quickly?"
                    ),
                    why_it_matters="This turns a detected gap into a credible preparation topic.",
                )
            )

        questions.extend(
            [
                InterviewQuestion(
                    category="behavioral",
                    question=(
                        "Tell me about a time you automated a manual workflow and had to "
                        "earn stakeholder trust."
                    ),
                    why_it_matters="AI automation roles require adoption, not just implementation.",
                ),
                InterviewQuestion(
                    category="behavioral",
                    question=(
                        "Describe a system you made more reliable after discovering "
                        "brittle behavior."
                    ),
                    why_it_matters=(
                        "The role likely values production ownership and debugging "
                        "judgment."
                    ),
                ),
                InterviewQuestion(
                    category="company",
                    question=(
                        "What would you want to learn in your first 30 days as "
                        f"{role_article} "
                        f"{job.role_title}?"
                    ),
                    why_it_matters="This tests role curiosity and onboarding maturity.",
                ),
            ]
        )
        return questions[:10]


class OpenAIContentProvider:
    """Extension point for replacing deterministic templates with an LLM provider."""

    name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4.1-mini") -> None:
        self.api_key = api_key
        self.model = model

    def generate_cover_letter(
        self,
        request: AnalysisRequest,
        candidate: CandidateProfile,
        job: JobProfile,
        match: MatchScore,
        missing_skills: list[str],
    ) -> str:
        raise NotImplementedError(
            "Wire the OpenAI Responses API here when enabling paid LLM generation."
        )

    def suggest_resume_improvements(
        self,
        request: AnalysisRequest,
        candidate: CandidateProfile,
        job: JobProfile,
        missing_skills: list[str],
    ) -> list[ResumeImprovement]:
        raise NotImplementedError("Wire provider-specific resume critique generation here.")

    def create_interview_questions(
        self,
        candidate: CandidateProfile,
        job: JobProfile,
        match: MatchScore,
        missing_skills: list[str],
    ) -> list[InterviewQuestion]:
        raise NotImplementedError("Wire provider-specific interview question generation here.")


def _join_human(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def _article_for(phrase: str) -> str:
    if not phrase:
        return "a"
    first = phrase.strip()[0].lower()
    return "an" if first in {"a", "e", "i", "o", "u"} else "a"
