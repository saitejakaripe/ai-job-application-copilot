from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile, status

from ai_job_application_copilot.db import AnalysisRepository
from ai_job_application_copilot.models import AnalysisRequest, AnalysisSummary, ApplicationAnalysis
from ai_job_application_copilot.services.application import ApplicationService
from ai_job_application_copilot.services.workflow import ApplicationWorkflow

router = APIRouter()


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-job-application-copilot"}


@router.post(
    "/v1/applications/analyze",
    response_model=ApplicationAnalysis,
    status_code=status.HTTP_201_CREATED,
    tags=["analysis"],
)
def analyze_application(payload: AnalysisRequest, http_request: Request) -> ApplicationAnalysis:
    service = _service(http_request)
    return service.analyze(payload)


@router.post(
    "/v1/applications/analyze-file",
    response_model=ApplicationAnalysis,
    status_code=status.HTTP_201_CREATED,
    tags=["analysis"],
)
async def analyze_application_file(
    http_request: Request,
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    candidate_name: str | None = Form(None),
    role_title: str | None = Form(None),
    company_name: str | None = Form(None),
    persist: bool = Form(True),
) -> ApplicationAnalysis:
    if resume_file.content_type not in {
        "text/plain",
        "text/markdown",
        "application/octet-stream",
    }:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only plain text or markdown resume uploads are supported in v1.",
        )

    raw_resume = await resume_file.read()
    if len(raw_resume) > 1_000_000:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Resume upload must be smaller than 1 MB.",
        )

    try:
        resume_text = raw_resume.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume upload must be UTF-8 text.",
        ) from exc

    payload = AnalysisRequest(
        resume_text=resume_text,
        job_description=job_description,
        candidate_name=candidate_name,
        role_title=role_title,
        company_name=company_name,
        persist=persist,
    )
    return _service(http_request).analyze(payload)


@router.get(
    "/v1/applications",
    response_model=list[AnalysisSummary],
    tags=["analysis"],
)
def list_applications(
    http_request: Request,
    limit: int = Query(20, ge=1, le=100),
) -> list[AnalysisSummary]:
    return _repository(http_request).list_summaries(limit=limit)


@router.get(
    "/v1/applications/{analysis_id}",
    response_model=ApplicationAnalysis,
    tags=["analysis"],
)
def get_application(analysis_id: str, http_request: Request) -> ApplicationAnalysis:
    analysis = _repository(http_request).get(analysis_id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    return analysis


def _repository(request: Request) -> AnalysisRepository:
    return request.app.state.repository


def _service(request: Request) -> ApplicationService:
    return ApplicationService(
        repository=_repository(request),
        workflow=request.app.state.workflow,
    )


def create_workflow() -> ApplicationWorkflow:
    return ApplicationWorkflow()

