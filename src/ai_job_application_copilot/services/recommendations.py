from __future__ import annotations

import json
from collections import Counter
from importlib import resources
from typing import Any
from urllib.parse import quote_plus

from ai_job_application_copilot.models import (
    ApplicationLink,
    JobRecommendation,
    JobRecommendationRequest,
    JobRecommendationResponse,
    JobSearchPreferences,
    ResumeImprovementBundle,
    ResumeProfile,
    ResumeProfileRequest,
    SourceLink,
)
from ai_job_application_copilot.services.resume_profile import ResumeProfileAnalyzer

SOURCE_LINKS = [
    SourceLink(
        label="LinkedIn Remote Developer Jobs Worldwide",
        url="https://www.linkedin.com/jobs/remote-developer-jobs-worldwide",
        region="global",
    ),
    SourceLink(
        label="LinkedIn Remote Software Developer Jobs Worldwide",
        url=(
            "https://www.linkedin.com/jobs/"
            "remote-software-developer-jobs-worldwide"
        ),
        region="global",
    ),
    SourceLink(
        label="Wellfound Remote Tech Jobs",
        url="https://wellfound.com/remote",
        region="global",
    ),
    SourceLink(
        label="We Work Remotely",
        url="https://weworkremotely.com/jobs",
        region="global",
    ),
    SourceLink(
        label="Remotive Software Development Jobs",
        url="https://remotive.com/remote-jobs/software-development",
        region="global",
    ),
    SourceLink(
        label="Indeed Worldwide Remote Software Jobs",
        url=(
            "https://www.indeed.com/"
            "q-worldwide-remote-software-engineering-jobs.html"
        ),
        region="global",
    ),
    SourceLink(
        label="Turing Remote Software Engineer Jobs",
        url="https://www.turing.com/jobs/remote-software-engineer-jobs",
        region="global",
    ),
    SourceLink(
        label="Arc Remote Developer Jobs",
        url="https://arc.dev/developers",
        region="global",
    ),
    SourceLink(
        label="Naukri India Tech Jobs",
        url="https://www.naukri.com/software-developer-jobs",
        region="india",
    ),
    SourceLink(
        label="Indeed India Tech Jobs",
        url="https://in.indeed.com/jobs?q=software+developer",
        region="india",
    ),
]

APPLICATION_SOURCES: list[dict[str, Any]] = [
    {"name": "LinkedIn", "regions": {"india", "global"}},
    {"name": "Naukri", "regions": {"india"}},
    {"name": "Indeed India", "regions": {"india"}},
    {"name": "Indeed", "regions": {"global"}},
    {"name": "Wellfound", "regions": {"india", "global"}},
    {"name": "We Work Remotely", "regions": {"global"}},
    {"name": "Remotive", "regions": {"global"}},
    {"name": "Turing", "regions": {"global"}},
    {"name": "Arc", "regions": {"global"}},
    {"name": "Company Career Pages", "regions": {"india", "global"}},
]

ROLE_TEMPLATES: list[dict[str, Any]] = [
    {
        "key": "ai-engineer",
        "title": "AI Engineer",
        "roles": ["AI Engineer", "AI Agent Developer"],
        "skills": ["python", "llm", "openai", "rag", "prompt engineering", "ai agents"],
        "salary": (8.0, 35.0),
    },
    {
        "key": "ai-agent-developer",
        "title": "AI Agent Developer",
        "roles": ["AI Agent Developer", "AI Engineer", "Prompt Engineer"],
        "skills": ["python", "llm", "openai", "rag", "ai agents", "api integration"],
        "salary": (6.0, 24.0),
    },
    {
        "key": "prompt-engineer",
        "title": "Prompt Engineer",
        "roles": ["Prompt Engineer", "AI Engineer"],
        "skills": ["prompt engineering", "llm", "nlp", "data analysis", "python"],
        "salary": (4.0, 18.0),
    },
    {
        "key": "python-developer",
        "title": "Python Developer",
        "roles": ["Python Developer", "Backend Developer"],
        "skills": ["python", "fastapi", "django", "sql", "rest api", "git"],
        "salary": (5.0, 24.0),
    },
    {
        "key": "backend-developer",
        "title": "Backend Developer",
        "roles": ["Backend Developer", "Software Developer"],
        "skills": ["python", "node.js", "sql", "postgresql", "docker", "rest api"],
        "salary": (6.0, 28.0),
    },
    {
        "key": "frontend-developer",
        "title": "Frontend Developer",
        "roles": ["Frontend Developer"],
        "skills": ["react", "javascript", "typescript", "html", "css", "git"],
        "salary": (4.5, 22.0),
    },
    {
        "key": "full-stack-developer",
        "title": "Full-Stack Developer",
        "roles": ["Full-Stack Developer", "Frontend Developer", "Backend Developer"],
        "skills": ["react", "node.js", "typescript", "sql", "docker", "rest api"],
        "salary": (7.0, 30.0),
    },
    {
        "key": "data-analyst",
        "title": "Data Analyst",
        "roles": ["Data Analyst", "Business Analyst"],
        "skills": ["sql", "excel", "data analysis", "power bi", "tableau", "python"],
        "salary": (3.5, 18.0),
    },
    {
        "key": "machine-learning-engineer",
        "title": "Machine Learning Engineer",
        "roles": ["Machine Learning Engineer", "Data Scientist"],
        "skills": ["python", "machine learning", "pytorch", "tensorflow", "nlp", "aws"],
        "salary": (8.0, 36.0),
    },
    {
        "key": "qa-automation-engineer",
        "title": "QA Automation Engineer",
        "roles": ["QA Automation Engineer", "Software Developer"],
        "skills": ["python", "javascript", "pytest", "git", "ci/cd", "rest api"],
        "salary": (4.0, 20.0),
    },
    {
        "key": "devops-engineer",
        "title": "DevOps Engineer",
        "roles": ["DevOps Engineer", "Backend Developer"],
        "skills": ["docker", "kubernetes", "aws", "terraform", "ci/cd", "observability"],
        "salary": (7.0, 34.0),
    },
]

INDIA_LOCATIONS = [
    "Remote, India",
    "Hyderabad",
    "Bengaluru",
    "Chennai",
    "Pune",
    "Mumbai",
    "Delhi NCR",
]
GLOBAL_LOCATIONS = [
    ("Worldwide Remote", "Worldwide"),
    ("US Remote / Worldwide", "United States"),
    ("Europe Remote", "Europe"),
    ("Canada Remote", "Canada"),
]
INDIA_CATALOG_SOURCES = ["LinkedIn", "Naukri", "Indeed India", "Wellfound", "Company Career Pages"]
FRESHER_INDIA_LOCATIONS = [
    "Remote, India",
    "Hyderabad",
    "Bengaluru",
    "Chennai",
    "Pune",
    "Mumbai",
    "Delhi NCR",
    "Noida",
    "Gurugram",
    "Kochi",
    "Ahmedabad",
    "Kolkata",
    "Jaipur",
    "Anywhere in India",
]
FRESHER_INDIA_SOURCES = [
    "LinkedIn",
    "Naukri",
    "Indeed India",
    "Wellfound",
    "Company Career Pages",
]
FRESHER_GLOBAL_SOURCES = [
    "LinkedIn",
    "Wellfound",
    "Indeed",
    "Arc",
    "Company Career Pages",
]
FRESHER_TITLE_PREFIX = "Fresher"
FRESHER_SALARY_MULTIPLIER = 0.5
GLOBAL_FRESHER_TITLE_PREFIX = "Entry-Level"
GLOBAL_FRESHER_SALARY_MULTIPLIER = 0.6
GLOBAL_CATALOG_SOURCES = [
    "LinkedIn",
    "Wellfound",
    "We Work Remotely",
    "Remotive",
    "Turing",
    "Arc",
    "Indeed",
    "Company Career Pages",
]
INTERN_CATALOG_SOURCES = ["LinkedIn", "Wellfound", "Company Career Pages"]


class JobRecommendationService:
    def __init__(self, profile_analyzer: ResumeProfileAnalyzer | None = None) -> None:
        self.profile_analyzer = profile_analyzer or ResumeProfileAnalyzer()
        self.catalog = _dedupe_catalog([*_load_catalog(), *_generated_catalog()])

    def recommend(self, request: JobRecommendationRequest) -> JobRecommendationResponse:
        profile = request.profile or self.profile_analyzer.analyze(
            ResumeProfileRequest(resume_text=request.resume_text or "")
        )
        preferences = request.preferences
        scored_jobs: list[tuple[int, JobRecommendation]] = []

        for job in self.catalog:
            if not _passes_strict_filters(job, profile, preferences):
                continue
            recommendation = _score_job(job, profile, preferences)
            if recommendation.resume_match_percentage < preferences.min_match_percentage:
                continue
            scored_jobs.append((_priority_score(job, recommendation, preferences), recommendation))

        scored_jobs.sort(key=lambda item: item[0], reverse=True)
        unique_scored_jobs = _dedupe_scored_jobs(scored_jobs)
        jobs = [job for _, job in unique_scored_jobs]
        application_links = _build_application_links(profile, preferences)

        return JobRecommendationResponse(
            profile=profile,
            preferences=preferences,
            jobs=jobs,
            resume_improvements=_build_resume_improvements(profile, jobs),
            source_links=_source_links_for(preferences),
            application_links=application_links,
            total_matches=len(jobs),
            returned_matches=len(jobs),
            generated_application_links_count=len(application_links),
        )


def _load_catalog() -> list[dict[str, Any]]:
    catalog_path = resources.files("ai_job_application_copilot").joinpath("data/job_catalog.json")
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def _generated_catalog() -> list[dict[str, Any]]:
    generated: list[dict[str, Any]] = []
    for role in ROLE_TEMPLATES:
        generated.extend(_generated_experienced_jobs(role))
        generated.extend(_generated_fresher_jobs(role))
        generated.extend(_generated_internships(role))
        generated.extend(_generated_contract_jobs(role))
    return generated


def _generated_experienced_jobs(role: dict[str, Any]) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for location in INDIA_LOCATIONS:
        remote = "remote" in location.lower()
        for source in INDIA_CATALOG_SOURCES:
            jobs.append(
                _catalog_job(
                    role=role,
                    source=source,
                    location=location,
                    country="India",
                    region="india",
                    job_type="Full-time",
                    min_experience=1,
                    max_experience=4,
                    candidate_levels=["experienced"],
                    remote=remote,
                )
            )

    for location, country in GLOBAL_LOCATIONS:
        for source in GLOBAL_CATALOG_SOURCES:
            jobs.append(
                _catalog_job(
                    role=role,
                    source=source,
                    location=location,
                    country=country,
                    region="global",
                    job_type="Full-time",
                    min_experience=1,
                    max_experience=5,
                    candidate_levels=["experienced"],
                    remote=True,
                )
            )
    return jobs


def _generated_fresher_jobs(role: dict[str, Any]) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for location in FRESHER_INDIA_LOCATIONS:
        for source in FRESHER_INDIA_SOURCES:
            jobs.append(
                _catalog_job(
                    role=role,
                    source=source,
                    location=location,
                    country="India",
                    region="india",
                    job_type="Full-time",
                    min_experience=0,
                    max_experience=1,
                    candidate_levels=["fresher"],
                    remote="remote" in location.lower(),
                    title_prefix=FRESHER_TITLE_PREFIX,
                    salary_multiplier=FRESHER_SALARY_MULTIPLIER,
                    id_variant="fresher",
                )
            )
    for location, country in GLOBAL_LOCATIONS:
        for source in FRESHER_GLOBAL_SOURCES:
            jobs.append(
                _catalog_job(
                    role=role,
                    source=source,
                    location=location,
                    country=country,
                    region="global",
                    job_type="Full-time",
                    min_experience=0,
                    max_experience=1,
                    candidate_levels=["fresher"],
                    remote=True,
                    title_prefix=GLOBAL_FRESHER_TITLE_PREFIX,
                    salary_multiplier=GLOBAL_FRESHER_SALARY_MULTIPLIER,
                    id_variant="fresher",
                )
            )
    return jobs


def _generated_internships(role: dict[str, Any]) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for location in ["Remote, India", "Hyderabad", "Bengaluru", "Chennai", "Pune"]:
        for source in INTERN_CATALOG_SOURCES:
            jobs.append(
                _catalog_job(
                    role=role,
                    source=source,
                    location=location,
                    country="India",
                    region="india",
                    job_type="Internship",
                    min_experience=0,
                    max_experience=1,
                    candidate_levels=["intern", "fresher"],
                    remote="remote" in location.lower(),
                    title_suffix="Intern",
                    salary_multiplier=0.25,
                )
            )
    for location, country in GLOBAL_LOCATIONS[:2]:
        for source in INTERN_CATALOG_SOURCES:
            jobs.append(
                _catalog_job(
                    role=role,
                    source=source,
                    location=location,
                    country=country,
                    region="global",
                    job_type="Internship",
                    min_experience=0,
                    max_experience=1,
                    candidate_levels=["intern", "fresher"],
                    remote=True,
                    title_suffix="Intern",
                    salary_multiplier=0.35,
                )
            )
    return jobs


def _generated_contract_jobs(role: dict[str, Any]) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for location, country in GLOBAL_LOCATIONS:
        for source in ["LinkedIn", "Arc", "Remotive", "Wellfound", "Company Career Pages"]:
            jobs.append(
                _catalog_job(
                    role=role,
                    source=source,
                    location=location,
                    country=country,
                    region="global",
                    job_type="Contract",
                    min_experience=2,
                    max_experience=6,
                    candidate_levels=["experienced"],
                    remote=True,
                    title_prefix="Contract",
                    salary_multiplier=1.2,
                )
            )
    for location in ["Remote, India", "Bengaluru", "Hyderabad", "Mumbai"]:
        for source in ["LinkedIn", "Indeed India", "Naukri", "Company Career Pages"]:
            jobs.append(
                _catalog_job(
                    role=role,
                    source=source,
                    location=location,
                    country="India",
                    region="india",
                    job_type="Contract",
                    min_experience=2,
                    max_experience=6,
                    candidate_levels=["experienced"],
                    remote="remote" in location.lower(),
                    title_prefix="Contract",
                    salary_multiplier=0.95,
                )
            )
    return jobs


def _catalog_job(
    *,
    role: dict[str, Any],
    source: str,
    location: str,
    country: str,
    region: str,
    job_type: str,
    min_experience: int,
    max_experience: int | None,
    candidate_levels: list[str],
    remote: bool,
    title_prefix: str = "",
    title_suffix: str = "",
    salary_multiplier: float = 1.0,
    id_variant: str = "",
) -> dict[str, Any]:
    title_parts = [title_prefix, role["title"], title_suffix]
    title = " ".join(part for part in title_parts if part)
    salary_min, salary_max = role["salary"]
    slug_parts = [
        "generated",
        region,
        source.lower().replace(" ", "-"),
        job_type.lower().replace(" ", "-"),
        role["key"],
        _slugify(location),
    ]
    if id_variant:
        slug_parts.append(id_variant)
    career_level = (
        "fresher"
        if "fresher" in candidate_levels and "experienced" not in candidate_levels
        else None
    )
    return {
        "id": "-".join(slug_parts),
        "title": title,
        "company": _generated_company_name(source, region, job_type),
        "location": location,
        "country": country,
        "region": region,
        "job_type": job_type,
        "min_experience": min_experience,
        "max_experience": max_experience,
        "candidate_levels": candidate_levels,
        "required_skills": role["skills"],
        "roles": role["roles"],
        "salary_min_lpa": round(salary_min * salary_multiplier, 1),
        "salary_max_lpa": round(salary_max * salary_multiplier, 1),
        "source_website": source,
        "apply_link": _build_source_url(
            source,
            role["title"],
            location,
            region,
            job_type,
            career_level=career_level,
        ),
        "remote": remote,
    }


def _generated_company_name(source: str, region: str, job_type: str) -> str:
    market = "global remote" if region == "global" else "India"
    if source == "Company Career Pages":
        return f"{market.title()} company career pages"
    if job_type == "Internship":
        return f"{market.title()} internship employers via {source}"
    return f"{market.title()} employers via {source}"


def _dedupe_catalog(catalog: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for job in catalog:
        job_id = job["id"]
        if job_id in seen:
            continue
        deduped.append(job)
        seen.add(job_id)
    return deduped


def _dedupe_scored_jobs(
    scored_jobs: list[tuple[int, JobRecommendation]],
) -> list[tuple[int, JobRecommendation]]:
    seen: set[tuple[str, str, str, str, str, str, str]] = set()
    deduped: list[tuple[int, JobRecommendation]] = []
    for priority, recommendation in scored_jobs:
        key = _recommendation_identity_key(recommendation)
        if key in seen:
            continue
        deduped.append((priority, recommendation))
        seen.add(key)
    return deduped


def _recommendation_identity_key(
    recommendation: JobRecommendation,
) -> tuple[str, str, str, str, str, str, str]:
    generated_source_card = _is_generated_source_company(recommendation.company_name)
    company_key = "" if generated_source_card else recommendation.company_name.strip().lower()
    location_key = "" if generated_source_card else _normalize_location(recommendation.location)
    source_key = "" if generated_source_card else recommendation.source_website.strip().lower()
    return (
        _normalize_job_title(recommendation.job_title),
        company_key,
        location_key,
        recommendation.job_type.strip().lower(),
        recommendation.required_experience.strip().lower(),
        recommendation.region.strip().lower(),
        source_key,
    )


def _normalize_job_title(title: str) -> str:
    normalized = " ".join(_slugify(title).split("-"))
    early_career_prefixes = (
        "fresher",
        "junior",
        "entry level",
        "graduate trainee",
        "associate",
    )
    for prefix in early_career_prefixes:
        if normalized.startswith(f"{prefix} "):
            return normalized.removeprefix(f"{prefix} ").strip()
    return normalized


def _is_generated_source_company(company_name: str) -> bool:
    normalized = company_name.strip().lower()
    return " employers via " in normalized or normalized.endswith("company career pages")


def _passes_strict_filters(
    job: dict[str, Any],
    profile: ResumeProfile,
    preferences: JobSearchPreferences,
) -> bool:
    if preferences.market_scope == "india" and job["region"] != "india":
        return False
    if preferences.market_scope == "abroad" and job["region"] != "global":
        return False
    if preferences.market_scope == "abroad" and not job["remote"]:
        return False

    selected_non_remote_types = {
        job_type for job_type in preferences.job_types if job_type != "Remote"
    }
    if "Internship" in preferences.job_types and job["job_type"] != "Internship":
        return False
    if selected_non_remote_types and job["job_type"] not in selected_non_remote_types:
        return False

    if preferences.source_filters:
        selected_sources = {source.lower() for source in preferences.source_filters}
        if job["source_website"].lower() not in selected_sources:
            return False

    if preferences.skill_filters:
        job_skills = {skill.lower() for skill in job["required_skills"]}
        selected_skills = {skill.lower() for skill in preferences.skill_filters}
        if not selected_skills <= job_skills:
            return False

    candidate_level = preferences.candidate_level
    years = _candidate_years(profile, preferences)
    min_experience = int(job["min_experience"])
    max_experience = job["max_experience"]
    candidate_levels = set(job["candidate_levels"])

    if candidate_level == "intern":
        return job["job_type"] == "Internship"
    if candidate_level == "fresher":
        return (
            "fresher" in candidate_levels
            and min_experience <= 1
            and (max_experience is None or int(max_experience) <= 1)
        )

    if "experienced" not in candidate_levels:
        return False
    if years < min_experience:
        return False
    if max_experience is not None and years > int(max_experience):
        return False

    expected_min = preferences.expected_salary_min_lpa
    return not (
        expected_min is not None
        and job["salary_max_lpa"] is not None
        and float(job["salary_max_lpa"]) < expected_min
    )


def _score_job(
    job: dict[str, Any],
    profile: ResumeProfile,
    preferences: JobSearchPreferences,
) -> JobRecommendation:
    candidate_skills = {skill.lower() for skill in profile.skills}
    required_skills = [skill.lower() for skill in job["required_skills"]]
    matched_skills = sorted(set(required_skills) & candidate_skills)
    missing_skills = sorted(set(required_skills) - candidate_skills)
    skill_score = len(matched_skills) / len(required_skills) if required_skills else 0.0
    role_score = _role_score(job, profile, preferences)
    location_score = _location_score(job, preferences)
    type_score = _job_type_score(job, preferences)
    salary_score = _salary_score(job, preferences)

    score = round(
        min(
            1.0,
            (skill_score * 0.55)
            + (role_score * 0.18)
            + (location_score * 0.15)
            + (type_score * 0.08)
            + (salary_score * 0.04),
        )
        * 100
    )

    return JobRecommendation(
        id=job["id"],
        job_title=job["title"],
        company_name=job["company"],
        location=job["location"],
        country=job["country"],
        job_type=job["job_type"],
        required_experience=_experience_label(job),
        required_skills=job["required_skills"],
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        resume_match_percentage=score,
        match_reason=_match_reason(job, matched_skills, missing_skills, preferences),
        direct_apply_link=job["apply_link"],
        source_website=job["source_website"],
        salary_range=_salary_label(job),
        is_remote=bool(job["remote"]),
        region=job["region"],
    )


def _candidate_years(profile: ResumeProfile, preferences: JobSearchPreferences) -> int:
    if preferences.years_experience is not None:
        return preferences.years_experience
    if profile.years_experience is not None:
        return profile.years_experience
    return 0


def _role_score(
    job: dict[str, Any],
    profile: ResumeProfile,
    preferences: JobSearchPreferences,
) -> float:
    interested = {role.lower() for role in preferences.interested_roles}
    suitable = {role.lower() for role in profile.suitable_roles}
    job_roles = {role.lower() for role in job["roles"]}
    if interested:
        return 1.0 if interested & job_roles else 0.25
    return 0.8 if suitable & job_roles else 0.4


def _location_score(job: dict[str, Any], preferences: JobSearchPreferences) -> float:
    locations = {_normalize_location(location) for location in preferences.locations}
    if preferences.custom_location:
        locations.add(_normalize_location(preferences.custom_location))

    job_location = _normalize_location(job["location"])
    job_country = _normalize_location(job["country"])

    if job["remote"] and ("remote" in locations or preferences.market_scope == "abroad"):
        return 1.0
    if "anywhere in india" in locations and job["region"] == "india":
        return 0.9
    if "worldwide" in job_location and preferences.market_scope in {"abroad", "both"}:
        return 0.9
    if job_location in locations or job_country in locations:
        return 1.0
    if preferences.open_to_relocation and job["region"] == "india":
        return 0.65
    return 0.35


def _job_type_score(job: dict[str, Any], preferences: JobSearchPreferences) -> float:
    if job["job_type"] in preferences.job_types:
        return 1.0
    if "Remote" in preferences.job_types and job["remote"]:
        return 0.9
    return 0.4


def _salary_score(job: dict[str, Any], preferences: JobSearchPreferences) -> float:
    expected_min = preferences.expected_salary_min_lpa
    expected_max = preferences.expected_salary_max_lpa
    if expected_min is None and expected_max is None:
        return 0.7
    job_min = job["salary_min_lpa"]
    job_max = job["salary_max_lpa"]
    if job_min is None or job_max is None:
        return 0.45
    if expected_min is not None and job_max < expected_min:
        return 0.0
    if expected_max is not None and job_min > expected_max:
        return 0.25
    return 1.0


def _priority_score(
    job: dict[str, Any],
    recommendation: JobRecommendation,
    preferences: JobSearchPreferences,
) -> int:
    priority = recommendation.resume_match_percentage
    if not _is_generated_source_company(job["company"]):
        priority += 16
    locations = {_normalize_location(location) for location in preferences.locations}
    if recommendation.is_remote and ("remote" in locations or preferences.market_scope == "abroad"):
        priority += 8
    if _normalize_location(recommendation.location) in locations:
        priority += 8
    if job["region"] == "global" and preferences.market_scope == "abroad":
        priority += 6
    return priority


def _match_reason(
    job: dict[str, Any],
    matched_skills: list[str],
    missing_skills: list[str],
    preferences: JobSearchPreferences,
) -> str:
    matched = ", ".join(matched_skills[:4]) if matched_skills else "role keywords"
    reason = f"Matches {matched} and fits the {job['job_type'].lower()} preference"
    if job["remote"]:
        reason += " with a remote-friendly listing"
    if preferences.market_scope == "abroad" and job["region"] == "global":
        reason += " from an abroad/global remote source"
    if missing_skills:
        reason += f"; improve match by adding {', '.join(missing_skills[:3])}"
    return reason + "."


def _build_resume_improvements(
    profile: ResumeProfile,
    jobs: list[JobRecommendation],
) -> ResumeImprovementBundle:
    missing_counter: Counter[str] = Counter()
    keyword_counter: Counter[str] = Counter()
    for job in jobs[:8]:
        missing_counter.update(job.missing_skills)
        keyword_counter.update(job.required_skills)

    missing_skills = [skill for skill, _ in missing_counter.most_common(8)]
    resume_skills = set(profile.skills)
    keywords_to_add = [
        skill
        for skill, _ in keyword_counter.most_common(10)
        if skill not in resume_skills
    ][:8]

    project_suggestions = [
        f"Build a small project that proves {skill} with a public GitHub README."
        for skill in missing_skills[:3]
    ]
    if not project_suggestions:
        project_suggestions = [
            "Add one measurable project bullet for your strongest matched role."
        ]

    certification_suggestions = [
        f"Consider a focused certification or course in {skill} if it matches your target role."
        for skill in missing_skills[:3]
    ]
    if not certification_suggestions:
        certification_suggestions = [
            "Add completion dates and issuing organizations for existing certifications."
        ]

    return ResumeImprovementBundle(
        missing_skills=missing_skills,
        keywords_to_add=keywords_to_add,
        project_suggestions=project_suggestions,
        certification_suggestions=certification_suggestions,
        ats_suggestions=[
            (
                "Use standard section names such as Skills, Experience, Projects, "
                "Education, and Certifications."
            ),
            "Add exact role keywords from target jobs naturally in bullets and project summaries.",
            (
                "Quantify impact with numbers such as users, accuracy, latency, "
                "revenue, cost, or hours saved."
            ),
            (
                "Keep formatting simple: avoid tables, image-only resumes, "
                "and dense multi-column layouts."
            ),
        ],
    )


def _source_links_for(preferences: JobSearchPreferences) -> list[SourceLink]:
    if preferences.market_scope == "india":
        return [source for source in SOURCE_LINKS if source.region == "india"]
    if preferences.market_scope == "abroad":
        return [source for source in SOURCE_LINKS if source.region == "global"]
    return SOURCE_LINKS


def _build_application_links(
    profile: ResumeProfile,
    preferences: JobSearchPreferences,
) -> list[ApplicationLink]:
    roles = _application_roles(profile, preferences)
    regions = _application_regions(preferences)
    job_types = _application_job_types(preferences)
    sources = _application_sources(preferences, regions)

    links: list[ApplicationLink] = []
    seen: set[tuple[str, str, str, str]] = set()
    for source in sources:
        for region in regions:
            if region not in source["regions"]:
                continue
            for location in _application_locations(preferences, region):
                for role in roles:
                    for job_type in job_types:
                        if not _source_supports_job_type(source["name"], job_type):
                            continue
                        url = _build_source_url(
                            source["name"],
                            role,
                            location,
                            region,
                            job_type,
                            career_level=preferences.candidate_level,
                        )
                        key = (
                            source["name"].strip().lower(),
                            _application_market_key(region, location),
                            _normalize_role(role),
                            job_type.strip().lower(),
                        )
                        if key in seen:
                            continue
                        display_location = _application_display_location(region, location)
                        links.append(
                            ApplicationLink(
                                label=(
                                    f"{role} {job_type} jobs on "
                                    f"{source['name']} - {display_location}"
                                ),
                                url=url,
                                source_website=source["name"],
                                role=role,
                                location=display_location,
                                job_type=job_type,
                                region=region,
                                is_remote=(
                                    _is_remote_location(display_location)
                                    or region == "global"
                                ),
                            )
                        )
                        seen.add(key)
    return links


def _application_roles(
    profile: ResumeProfile,
    preferences: JobSearchPreferences,
) -> list[str]:
    roles = preferences.interested_roles or profile.suitable_roles
    if not roles:
        roles = ["Software Developer"]
    return _dedupe_strings(roles)


def _application_market_key(region: str, location: str) -> str:
    if region == "global":
        return "global-remote"
    if _is_remote_location(location):
        return "india-remote"
    return "india"


def _application_display_location(region: str, location: str) -> str:
    if region == "global":
        return "Global remote"
    if _is_remote_location(location):
        return "Remote India"
    if _normalize_location(location) == "anywhere in india":
        return "India"
    return location


def _normalize_role(role: str) -> str:
    return " ".join(
        "".join(char.lower() if char.isalnum() else " " for char in role).split()
    )


def _application_regions(preferences: JobSearchPreferences) -> list[str]:
    if preferences.market_scope == "india":
        return ["india"]
    if preferences.market_scope == "abroad":
        return ["global"]
    return ["india", "global"]


def _application_locations(preferences: JobSearchPreferences, region: str) -> list[str]:
    locations = [*preferences.locations]
    if preferences.custom_location:
        locations.append(preferences.custom_location)
    if not locations:
        locations = ["Remote"]

    if region == "global":
        global_locations: list[str] = []
        for location in locations:
            normalized = _normalize_location(location)
            if normalized == "remote":
                global_locations.extend(location for location, _ in GLOBAL_LOCATIONS)
            elif _is_remote_location(location) or normalized in {"worldwide", "global"}:
                global_locations.append(location)
        return _dedupe_strings(global_locations or ["Worldwide Remote"])

    return _dedupe_strings(locations)


def _application_job_types(preferences: JobSearchPreferences) -> list[str]:
    if "Internship" in preferences.job_types:
        return ["Internship"]
    non_remote_types = [job_type for job_type in preferences.job_types if job_type != "Remote"]
    return _dedupe_strings(non_remote_types or ["Full-time"])


def _application_sources(
    preferences: JobSearchPreferences,
    regions: list[str],
) -> list[dict[str, Any]]:
    selected = {source.lower() for source in preferences.source_filters}
    region_set = set(regions)
    sources = []
    for source in APPLICATION_SOURCES:
        if selected and source["name"].lower() not in selected:
            continue
        if source["regions"] & region_set:
            sources.append(source)
    return sources


def _source_supports_job_type(source: str, job_type: str) -> bool:
    if source == "Turing":
        return job_type in {"Full-time", "Contract"}
    if source in {"We Work Remotely", "Remotive", "Arc"}:
        return job_type in {"Full-time", "Contract", "Part-time"}
    return True


def _build_source_url(
    source: str,
    role: str,
    location: str,
    region: str,
    job_type: str,
    career_level: str | None = None,
) -> str:
    query = " ".join(
        part
        for part in [
            role,
            _career_level_query(career_level),
            _job_type_query(job_type),
            "remote",
        ]
        if part
    )
    encoded_query = quote_plus(query)
    encoded_location = quote_plus(location)
    slug = _slugify(role)

    if source == "LinkedIn":
        market_location = "India" if region == "india" and location == "Remote" else location
        return (
            "https://www.linkedin.com/jobs/search/"
            f"?keywords={encoded_query}&location={quote_plus(market_location)}"
        )
    if source == "Naukri":
        source_slug = _slugify(
            " ".join(part for part in [role, _career_level_query(career_level)] if part)
        )
        location_slug = "" if location == "Anywhere in India" else f"-in-{_slugify(location)}"
        return f"https://www.naukri.com/{source_slug or slug}-jobs{location_slug}"
    if source == "Indeed India":
        return f"https://in.indeed.com/jobs?q={encoded_query}&l={encoded_location}"
    if source == "Indeed":
        return f"https://www.indeed.com/jobs?q={encoded_query}&l={encoded_location}"
    if source == "Wellfound":
        return f"https://wellfound.com/jobs?keyword={encoded_query}"
    if source == "We Work Remotely":
        return f"https://weworkremotely.com/remote-jobs/search?term={encoded_query}"
    if source == "Remotive":
        return f"https://remotive.com/remote-jobs/search?search={encoded_query}"
    if source == "Turing":
        return f"https://www.turing.com/jobs/remote-{slug}-jobs?search={encoded_query}"
    if source == "Arc":
        return f"https://arc.dev/remote-jobs?keywords={encoded_query}"
    if source == "Company Career Pages":
        company_query = " ".join(
            part
            for part in [
                role,
                _career_level_query(career_level),
                job_type,
                location,
                "company careers apply",
            ]
            if part
        )
        return (
            "https://www.google.com/search?q="
            f"{quote_plus(company_query)}"
        )
    return "https://www.linkedin.com/jobs/search/"


def _job_type_query(job_type: str) -> str:
    if job_type == "Full-time":
        return ""
    return job_type


def _career_level_query(career_level: str | None) -> str:
    if career_level == "fresher":
        return "fresher entry level 0-1 years"
    if career_level == "intern":
        return "internship fresher"
    return ""


def _is_remote_location(location: str) -> bool:
    normalized = _normalize_location(location)
    return any(term in normalized for term in ("remote", "worldwide", "global", "work from home"))


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        clean = value.strip()
        key = clean.lower()
        if clean and key not in seen:
            deduped.append(clean)
            seen.add(key)
    return deduped


def _slugify(value: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else " " for char in value)
    return "-".join(normalized.split())


def _salary_label(job: dict[str, Any]) -> str | None:
    if job["salary_min_lpa"] is None or job["salary_max_lpa"] is None:
        return None
    return f"{job['salary_min_lpa']:g}-{job['salary_max_lpa']:g} LPA"


def _experience_label(job: dict[str, Any]) -> str:
    min_experience = int(job["min_experience"])
    max_experience = job["max_experience"]
    if min_experience == 0 and max_experience == 1:
        return "0-1 year"
    if max_experience is None:
        return f"{min_experience}+ years"
    return f"{min_experience}-{int(max_experience)} years"


def _normalize_location(value: str) -> str:
    return value.strip().lower()
