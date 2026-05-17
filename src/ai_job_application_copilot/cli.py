from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_job_application_copilot.db import AnalysisRepository
from ai_job_application_copilot.models import AnalysisRequest
from ai_job_application_copilot.services.application import ApplicationService


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AI Job Application Copilot locally.")
    parser.add_argument("--resume", required=True, help="Path to a plain text resume.")
    parser.add_argument("--job", required=True, help="Path to a plain text job description.")
    parser.add_argument("--candidate-name")
    parser.add_argument("--role-title")
    parser.add_argument("--company-name")
    parser.add_argument("--database-url", default="sqlite:///./data/copilot.db")
    parser.add_argument("--no-persist", action="store_true")
    args = parser.parse_args()

    request = AnalysisRequest(
        resume_text=Path(args.resume).read_text(encoding="utf-8"),
        job_description=Path(args.job).read_text(encoding="utf-8"),
        candidate_name=args.candidate_name,
        role_title=args.role_title,
        company_name=args.company_name,
        persist=not args.no_persist,
    )
    repository = AnalysisRepository(args.database_url)
    result = ApplicationService(repository).analyze(request)
    print(json.dumps(result.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()

