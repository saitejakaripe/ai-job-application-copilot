from __future__ import annotations

import re

from ai_job_application_copilot.models import ResumeProfile, ResumeProfileRequest
from ai_job_application_copilot.services.text_tools import (
    extract_keywords,
    extract_skills,
    extract_years_of_experience,
    infer_candidate_name,
)

SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "education": ("education", "academic", "academics", "qualification", "qualifications"),
    "projects": ("projects", "project experience", "personal projects", "academic projects"),
    "certifications": ("certifications", "certificates", "licenses", "courses"),
    "work_experience": (
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "internships",
    ),
}

TOOL_ALIASES: dict[str, tuple[str, ...]] = {
    "VS Code": ("vs code", "visual studio code"),
    "GitHub": ("github",),
    "GitLab": ("gitlab",),
    "Jupyter": ("jupyter", "notebook"),
    "Postman": ("postman",),
    "Figma": ("figma",),
    "Linux": ("linux", "ubuntu"),
    "n8n": ("n8n",),
    "Make": ("make.com", "make automation"),
    "MongoDB": ("mongodb", "mongo db"),
    "Firebase": ("firebase",),
}


class ResumeProfileAnalyzer:
    """Deterministic resume parser for the job recommendation flow."""

    def analyze(self, request: ResumeProfileRequest) -> ResumeProfile:
        resume_text = request.resume_text
        skills = extract_skills(resume_text)
        keywords = extract_keywords(resume_text, limit=45)
        technical_tools = _extract_tools(resume_text, skills)

        return ResumeProfile(
            candidate_name=infer_candidate_name(resume_text, request.candidate_name),
            skills=skills,
            education=_extract_section_items(resume_text, "education", limit=5),
            projects=_extract_section_items(resume_text, "projects", limit=6),
            certifications=_extract_section_items(resume_text, "certifications", limit=5),
            work_experience=_extract_section_items(resume_text, "work_experience", limit=6),
            technical_tools=technical_tools,
            keywords=keywords,
            years_experience=extract_years_of_experience(resume_text),
            suitable_roles=_infer_suitable_roles(skills, keywords),
        )


def _extract_section_items(text: str, section: str, limit: int) -> list[str]:
    lines = [_clean_line(line) for line in text.splitlines()]
    current_section: str | None = None
    items: list[str] = []

    for line in lines:
        if not line:
            continue

        heading = _heading_for(line)
        if heading:
            current_section = heading
            continue

        if current_section == section and _looks_contentful(line):
            items.append(line)

    if items:
        return _dedupe(items, limit=limit)

    return _fallback_items(text, section, limit=limit)


def _heading_for(line: str) -> str | None:
    normalized = re.sub(r"[^a-z ]+", "", line.lower()).strip()
    if len(normalized.split()) > 4:
        return None
    for section, aliases in SECTION_ALIASES.items():
        if normalized in aliases:
            return section
    return None


def _fallback_items(text: str, section: str, limit: int) -> list[str]:
    patterns = {
        "education": (
            r"\b(?:b\.?tech|bachelor|master|m\.?tech|bca|mca|degree|"
            r"university|college)\b[^\n.]*"
        ),
        "projects": r"\b(?:built|developed|created|designed|implemented)\b[^\n.]{20,160}",
        "certifications": r"\b(?:certified|certification|certificate|course)\b[^\n.]{8,140}",
        "work_experience": (
            r"\b(?:intern|engineer|developer|analyst|worked|experience)\b"
            r"[^\n.]{20,170}"
        ),
    }
    matches = re.findall(patterns[section], text, flags=re.IGNORECASE)
    return _dedupe([_clean_line(match) for match in matches], limit=limit)


def _extract_tools(text: str, skills: list[str]) -> list[str]:
    normalized = text.lower()
    tools = [skill.title() if skill.islower() else skill for skill in skills]
    for tool, aliases in TOOL_ALIASES.items():
        if any(alias in normalized for alias in aliases):
            tools.append(tool)
    return _dedupe(tools, limit=18)


def _infer_suitable_roles(skills: list[str], keywords: list[str]) -> list[str]:
    skill_set = set(skills)
    keyword_set = set(keywords)
    roles: list[str] = []

    if skill_set & {"ai agents", "llm", "rag", "openai", "prompt engineering"}:
        roles.extend(["AI Engineer", "AI Agent Developer", "Prompt Engineer"])
    if skill_set & {"python", "fastapi", "django", "flask", "sql"}:
        roles.extend(["Python Developer", "Backend Developer"])
    if skill_set & {"react", "javascript", "typescript", "html", "css"}:
        roles.extend(["Frontend Developer", "Full-Stack Developer"])
    if skill_set & {"machine learning", "deep learning", "tensorflow", "pytorch", "nlp"}:
        roles.extend(["Machine Learning Engineer", "Data Scientist"])
    if skill_set & {"data analysis", "pandas", "numpy", "power bi", "tableau", "excel"}:
        roles.extend(["Data Analyst", "Business Analyst"])
    if "intern" in keyword_set:
        roles.append("Software Engineering Intern")

    return _dedupe(roles or ["Software Developer"], limit=8)


def _clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip(" \t-•*|")).strip()


def _looks_contentful(line: str) -> bool:
    if len(line) < 8 or "@" in line:
        return False
    return bool(re.search(r"[A-Za-z]{3,}", line))


def _dedupe(items: list[str], limit: int) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        clean = _clean_line(item)
        key = clean.lower()
        if clean and key not in seen:
            output.append(clean[:220])
            seen.add(key)
        if len(output) >= limit:
            break
    return output
