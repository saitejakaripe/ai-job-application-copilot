from __future__ import annotations


def test_resume_analysis_endpoint_extracts_profile(client) -> None:
    response = client.post(
        "/v1/resumes/analyze",
        json={
            "candidate_name": "Riya Sharma",
            "resume_text": _resume_text(),
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["candidate_name"] == "Riya Sharma"
    assert "python" in payload["skills"]
    assert "react" in payload["skills"]
    assert payload["suitable_roles"]


def test_resume_file_endpoint_accepts_text_upload(client) -> None:
    response = client.post(
        "/v1/resumes/analyze-file",
        files={
            "resume_file": (
                "resume.txt",
                _resume_text().encode("utf-8"),
                "text/plain",
            )
        },
        data={"candidate_name": "Riya Sharma"},
    )

    assert response.status_code == 201
    assert response.json()["candidate_name"] == "Riya Sharma"


def test_fresher_recommendations_only_return_early_career_jobs(client) -> None:
    payload = _recommendation_payload(
        candidate_level="fresher",
        years_experience=0,
        job_types=["Full-time", "Remote"],
        market_scope="both",
    )

    response = client.post("/v1/jobs/recommend", json=payload)

    assert response.status_code == 200
    jobs = response.json()["jobs"]
    assert jobs
    assert all(job["required_experience"] == "0-1 year" for job in jobs)


def test_fresher_recommendations_cover_target_ai_and_developer_roles(client) -> None:
    target_roles = [
        "AI Engineer",
        "AI Agent Developer",
        "Prompt Engineer",
        "Python Developer",
        "Backend Developer",
        "Frontend Developer",
        "Full-Stack Developer",
        "Machine Learning Engineer",
    ]
    payload = _recommendation_payload(
        candidate_level="fresher",
        years_experience=0,
        job_types=["Full-time", "Remote"],
        market_scope="both",
    )
    payload["preferences"]["interested_roles"] = target_roles
    payload["preferences"]["min_match_percentage"] = 0

    response = client.post("/v1/jobs/recommend", json=payload)

    assert response.status_code == 200
    payload = response.json()
    jobs = payload["jobs"]
    job_titles = {job["job_title"] for job in jobs}
    application_roles = {link["role"] for link in payload["application_links"]}
    assert len(jobs) >= 20
    assert payload["total_matches"] == len(jobs)
    assert all(job["required_experience"] == "0-1 year" for job in jobs)
    assert all("fresher" in link["url"].lower() for link in payload["application_links"])
    assert set(target_roles) <= application_roles
    assert all(
        any(role in title for title in job_titles)
        for role in target_roles
    )


def test_fresher_recommendations_do_not_repeat_logical_jobs(client) -> None:
    payload = _recommendation_payload(
        candidate_level="fresher",
        years_experience=0,
        job_types=["Full-time", "Remote"],
        market_scope="both",
    )
    payload["preferences"]["min_match_percentage"] = 0

    response = client.post("/v1/jobs/recommend", json=payload)

    assert response.status_code == 200
    jobs = response.json()["jobs"]
    logical_keys = [_logical_job_key(job) for job in jobs]
    assert jobs
    assert len(logical_keys) == len(set(logical_keys))


def test_generated_source_jobs_do_not_repeat_by_location_or_source(client) -> None:
    payload = _recommendation_payload(
        candidate_level="fresher",
        years_experience=0,
        job_types=["Full-time", "Remote"],
        market_scope="both",
    )
    payload["preferences"]["min_match_percentage"] = 0

    response = client.post("/v1/jobs/recommend", json=payload)

    assert response.status_code == 200
    generated_jobs = [
        job
        for job in response.json()["jobs"]
        if _is_generated_source_company(job["company_name"])
    ]
    generated_keys = [
        (
            _normalized_title(job["job_title"]),
            job["job_type"].strip().lower(),
            job["required_experience"].strip().lower(),
            job["region"].strip().lower(),
        )
        for job in generated_jobs
    ]
    assert generated_jobs
    assert len(generated_keys) == len(set(generated_keys))


def test_application_links_are_unique_by_source_role_type_and_market(client) -> None:
    payload = _recommendation_payload(
        candidate_level="fresher",
        years_experience=0,
        job_types=["Full-time", "Remote"],
        market_scope="both",
    )
    payload["preferences"]["interested_roles"] = [
        "AI Engineer",
        "Python Developer",
        "Backend Developer",
    ]
    payload["preferences"]["min_match_percentage"] = 0

    response = client.post("/v1/jobs/recommend", json=payload)

    assert response.status_code == 200
    links = response.json()["application_links"]
    link_keys = [_application_link_key(link) for link in links]
    assert links
    assert len(link_keys) == len(set(link_keys))
    replaced_locations = {"Worldwide Remote", "US Remote / Worldwide"}
    assert all(link["location"] not in replaced_locations for link in links)


def test_internship_preference_returns_only_internships(client) -> None:
    payload = _recommendation_payload(
        candidate_level="intern",
        years_experience=0,
        job_types=["Internship"],
        market_scope="both",
    )

    response = client.post("/v1/jobs/recommend", json=payload)

    assert response.status_code == 200
    jobs = response.json()["jobs"]
    assert jobs
    assert {job["job_type"] for job in jobs} == {"Internship"}


def test_experienced_candidate_never_gets_jobs_above_their_experience(client) -> None:
    payload = _recommendation_payload(
        candidate_level="experienced",
        years_experience=2,
        job_types=["Full-time", "Remote"],
        market_scope="abroad",
    )

    response = client.post("/v1/jobs/recommend", json=payload)

    assert response.status_code == 200
    job_ids = {job["id"] for job in response.json()["jobs"]}
    assert "global-remote-python-turing" not in job_ids
    assert "global-remote-backend-gitlab" not in job_ids


def test_abroad_remote_recommendations_prioritize_global_remote_sources(client) -> None:
    payload = _recommendation_payload(
        candidate_level="experienced",
        years_experience=3,
        job_types=["Full-time", "Remote"],
        market_scope="abroad",
    )

    response = client.post("/v1/jobs/recommend", json=payload)

    assert response.status_code == 200
    jobs = response.json()["jobs"]
    assert jobs
    assert all(job["region"] == "global" for job in jobs)
    assert all(job["is_remote"] for job in jobs)


def test_recommendations_return_more_than_top_thirty_when_relevant(client) -> None:
    payload = _recommendation_payload(
        candidate_level="experienced",
        years_experience=3,
        job_types=["Full-time", "Remote"],
        market_scope="both",
    )
    payload["preferences"]["min_match_percentage"] = 0

    response = client.post("/v1/jobs/recommend", json=payload)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["jobs"]) > 30
    assert payload["total_matches"] == len(payload["jobs"])
    assert payload["returned_matches"] == len(payload["jobs"])


def test_application_links_are_generated_for_selected_roles_and_sources(client) -> None:
    payload = _recommendation_payload(
        candidate_level="experienced",
        years_experience=3,
        job_types=["Full-time", "Remote"],
        market_scope="abroad",
    )

    response = client.post("/v1/jobs/recommend", json=payload)

    assert response.status_code == 200
    payload = response.json()
    links = payload["application_links"]
    assert payload["generated_application_links_count"] == len(links)
    assert len(links) >= 12
    assert {link["region"] for link in links} == {"global"}
    assert {"LinkedIn", "Turing", "Arc"} <= {link["source_website"] for link in links}
    assert all(link["url"].startswith("https://") for link in links)


def test_internshala_is_not_returned_in_jobs_or_links(client) -> None:
    payload = _recommendation_payload(
        candidate_level="intern",
        years_experience=0,
        job_types=["Internship"],
        market_scope="both",
    )

    response = client.post("/v1/jobs/recommend", json=payload)

    assert response.status_code == 200
    payload = response.json()
    all_text = [
        *(source["label"] for source in payload["source_links"]),
        *(link["label"] for link in payload["application_links"]),
    ]
    all_urls = [
        *(job["direct_apply_link"] for job in payload["jobs"]),
        *(source["url"] for source in payload["source_links"]),
        *(link["url"] for link in payload["application_links"]),
    ]
    assert payload["jobs"]
    assert payload["application_links"]
    assert all(job["source_website"] != "Internshala" for job in payload["jobs"])
    assert all(link["source_website"] != "Internshala" for link in payload["application_links"])
    assert all("internshala" not in text.lower() for text in all_text)
    assert all("internshala" not in url.lower() for url in all_urls)


def test_salary_expectation_filters_low_salary_jobs(client) -> None:
    payload = _recommendation_payload(
        candidate_level="experienced",
        years_experience=4,
        job_types=["Full-time", "Remote"],
        market_scope="abroad",
    )
    payload["preferences"]["expected_salary_min_lpa"] = 70

    response = client.post("/v1/jobs/recommend", json=payload)

    assert response.status_code == 200
    jobs = response.json()["jobs"]
    assert jobs
    assert "global-remote-ai-wellfound" not in {job["id"] for job in jobs}


def _recommendation_payload(
    candidate_level: str,
    years_experience: int,
    job_types: list[str],
    market_scope: str,
) -> dict:
    return {
        "resume_text": _resume_text(),
        "preferences": {
            "candidate_level": candidate_level,
            "years_experience": years_experience,
            "job_types": job_types,
            "locations": ["Remote"],
            "interested_roles": ["AI Engineer", "Full-Stack Developer"],
            "open_to_relocation": True,
            "market_scope": market_scope,
            "min_match_percentage": 35,
        },
    }


def _resume_text() -> str:
    return """
    Riya Sharma
    Software developer with 3 years of experience building Python FastAPI services,
    React dashboards, TypeScript interfaces, SQL data models, Docker deployments,
    REST API integrations, GitHub Actions workflows, LLM prototypes, RAG search,
    prompt engineering tools, and AI agent automation projects.

    Education
    B.Tech in Computer Science from Hyderabad Institute of Technology.

    Projects
    Built a resume matching platform using Python, React, SQL, and OpenAI workflows.
    Developed a dashboard that reduced manual job tracking time by 30 percent.

    Certifications
    Machine Learning fundamentals certificate and cloud deployment course.
    """


def _logical_job_key(job: dict) -> tuple[str, str, str, str, str, str, str]:
    title = _normalized_title(job["job_title"])
    generated_source_card = _is_generated_source_company(job["company_name"])
    company_key = "" if generated_source_card else job["company_name"].strip().lower()
    location_key = "" if generated_source_card else job["location"].strip().lower()
    source_key = "" if generated_source_card else job["source_website"].strip().lower()
    return (
        title,
        company_key,
        location_key,
        job["job_type"].strip().lower(),
        job["required_experience"].strip().lower(),
        job["region"].strip().lower(),
        source_key,
    )


def _normalized_title(title: str) -> str:
    normalized = " ".join(
        "".join(char.lower() if char.isalnum() else " " for char in title).split()
    )
    for prefix in (
        "fresher",
        "junior",
        "entry level",
        "graduate trainee",
        "associate",
    ):
        if normalized.startswith(f"{prefix} "):
            return normalized.removeprefix(f"{prefix} ").strip()
    return normalized


def _is_generated_source_company(company_name: str) -> bool:
    normalized = company_name.strip().lower()
    return " employers via " in normalized or normalized.endswith("company career pages")


def _application_link_key(link: dict) -> tuple[str, str, str, str]:
    return (
        link["source_website"].strip().lower(),
        _application_market_key(link),
        _normalized_title(link["role"]),
        link["job_type"].strip().lower(),
    )


def _application_market_key(link: dict) -> str:
    if link["region"] == "global":
        return "global-remote"
    if "remote" in link["location"].lower():
        return "india-remote"
    return "india"
