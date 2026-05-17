from __future__ import annotations

import re
from collections import Counter

STOPWORDS = {
    "a",
    "about",
    "across",
    "after",
    "all",
    "also",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "their",
    "this",
    "to",
    "with",
    "will",
    "we",
    "you",
    "your",
}


SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "python": ("python",),
    "fastapi": ("fastapi", "fast api"),
    "django": ("django",),
    "flask": ("flask",),
    "pydantic": ("pydantic",),
    "sql": ("sql", "relational database", "relational databases"),
    "sqlite": ("sqlite", "sqlite3"),
    "postgresql": ("postgresql", "postgres", "postgresql database"),
    "mysql": ("mysql",),
    "redis": ("redis",),
    "docker": ("docker", "container", "containers", "containerization"),
    "kubernetes": ("kubernetes", "k8s"),
    "terraform": ("terraform", "infrastructure as code", "iac"),
    "aws": ("aws", "amazon web services", "lambda", "ecs", "s3"),
    "azure": ("azure", "microsoft azure"),
    "gcp": ("gcp", "google cloud", "google cloud platform"),
    "git": ("git", "github", "version control"),
    "github actions": ("github actions",),
    "ci/cd": ("ci cd", "cicd", "continuous integration", "continuous delivery"),
    "pytest": ("pytest", "unit tests", "test automation", "automated tests"),
    "rest api": ("rest", "rest api", "restful", "api development"),
    "graphql": ("graphql",),
    "microservices": ("microservices", "microservice"),
    "langchain": ("langchain",),
    "langgraph": ("langgraph", "lang graph"),
    "openai": ("openai", "gpt", "chatgpt"),
    "llm": ("llm", "llms", "large language model", "large language models"),
    "rag": ("rag", "retrieval augmented generation", "retrieval-augmented generation"),
    "machine learning": ("machine learning", "ml"),
    "nlp": ("nlp", "natural language processing"),
    "data analysis": ("data analysis", "analytics", "data analytics"),
    "pandas": ("pandas",),
    "numpy": ("numpy",),
    "spark": ("spark", "pyspark"),
    "airflow": ("airflow", "dag orchestration"),
    "celery": ("celery",),
    "security": ("security", "auth", "authentication", "authorization", "oauth"),
    "observability": ("observability", "monitoring", "logging", "metrics", "tracing"),
    "agile": ("agile", "scrum"),
    "leadership": ("leadership", "mentoring", "team lead", "tech lead"),
}


def normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = lowered.replace("ci/cd", "ci cd").replace("ci-cd", "ci cd")
    lowered = lowered.replace("fast-api", "fast api").replace("lang graph", "langgraph")
    return re.sub(r"[^a-z0-9+#./-]+", " ", lowered).strip()


def extract_skills(text: str) -> list[str]:
    normalized = normalize_text(text)
    found: list[str] = []
    for skill, aliases in SKILL_ALIASES.items():
        if any(_contains_alias(normalized, alias) for alias in aliases):
            found.append(skill)
    return sorted(found)


def extract_keywords(text: str, limit: int = 35) -> list[str]:
    tokens = [
        token
        for token in re.findall(r"[a-z][a-z0-9+#.-]*", normalize_text(text))
        if len(token) > 2 and token not in STOPWORDS and not token.isdigit()
    ]
    counts = Counter(tokens)
    return [word for word, _ in counts.most_common(limit)]


def extract_years_of_experience(text: str) -> int | None:
    matches = re.findall(r"(\d{1,2})\+?\s*(?:years|yrs)\b", normalize_text(text))
    if not matches:
        return None
    return max(int(match) for match in matches)


def infer_candidate_name(resume_text: str, explicit_name: str | None = None) -> str:
    if explicit_name:
        return explicit_name.strip()
    for line in resume_text.splitlines()[:8]:
        clean = line.strip()
        words = clean.split()
        if 2 <= len(words) <= 5 and "@" not in clean and not any(char.isdigit() for char in clean):
            return clean
    return "Candidate"


def infer_role_title(job_description: str, explicit_title: str | None = None) -> str:
    if explicit_title:
        return explicit_title.strip()
    labeled = re.search(
        r"(?:job title|role|position)\s*[:|-]\s*([^\n.]{4,120})",
        job_description,
        flags=re.IGNORECASE,
    )
    if labeled:
        return labeled.group(1).strip()
    title_like = re.compile(
        r"\b(engineer|developer|architect|scientist|analyst|manager|specialist|lead|intern)\b",
        flags=re.IGNORECASE,
    )
    for line in job_description.splitlines()[:12]:
        clean = line.strip(" -\t")
        if 4 <= len(clean) <= 120 and title_like.search(clean):
            return clean
    return "Target Role"


def infer_company_name(job_description: str, explicit_company: str | None = None) -> str:
    if explicit_company:
        return explicit_company.strip()
    labeled = re.search(
        r"(?:company|organization)\s*[:|-]\s*([^\n.]{2,100})",
        job_description,
        flags=re.IGNORECASE,
    )
    if labeled:
        return labeled.group(1).strip()
    about = re.search(r"\babout\s+([A-Z][A-Za-z0-9&., -]{2,80})", job_description)
    if about:
        return about.group(1).strip(" .,-")
    return "the hiring team"


def infer_seniority(job_description: str) -> str | None:
    normalized = normalize_text(job_description)
    if re.search(r"\b(senior|staff|principal|lead)\b", normalized):
        return "senior"
    if re.search(r"\b(junior|entry|graduate|intern)\b", normalized):
        return "early-career"
    if re.search(r"\b(manager|director|head of)\b", normalized):
        return "leadership"
    return None


def _contains_alias(normalized_text: str, alias: str) -> bool:
    normalized_alias = normalize_text(alias)
    if " " in normalized_alias:
        return normalized_alias in normalized_text
    pattern = rf"(?<![a-z0-9+#]){re.escape(normalized_alias)}(?![a-z0-9+#])"
    return re.search(pattern, normalized_text) is not None
