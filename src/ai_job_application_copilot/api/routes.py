from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile, status

from ai_job_application_copilot.db import AnalysisRepository
from ai_job_application_copilot.models import (
    AnalysisRequest,
    AnalysisSummary,
    ApplicationAnalysis,
    JobRecommendationRequest,
    JobRecommendationResponse,
    ResumeProfile,
    ResumeProfileRequest,
)
from ai_job_application_copilot.services.application import ApplicationService
from ai_job_application_copilot.services.recommendations import JobRecommendationService
from ai_job_application_copilot.services.resume_profile import ResumeProfileAnalyzer
from ai_job_application_copilot.services.workflow import ApplicationWorkflow

router = APIRouter()


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-job-application-copilot"}


@router.post(
    "/v1/resumes/analyze",
    response_model=ResumeProfile,
    status_code=status.HTTP_201_CREATED,
    tags=["resume"],
)
def analyze_resume(payload: ResumeProfileRequest, http_request: Request) -> ResumeProfile:
    return _resume_analyzer(http_request).analyze(payload)


@router.post(
    "/v1/resumes/analyze-file",
    response_model=ResumeProfile,
    status_code=status.HTTP_201_CREATED,
    tags=["resume"],
)
async def analyze_resume_file(
    http_request: Request,
    resume_file: UploadFile = File(...),
    candidate_name: str | None = Form(None),
) -> ResumeProfile:
    raw_resume = await resume_file.read()
    if len(raw_resume) > 5_000_000:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Resume upload must be smaller than 5 MB.",
        )

    resume_text = _extract_resume_text(
        raw_resume,
        filename=resume_file.filename or "",
        content_type=resume_file.content_type or "",
    )
    return _resume_analyzer(http_request).analyze(
        ResumeProfileRequest(resume_text=resume_text, candidate_name=candidate_name)
    )


@router.post(
    "/v1/jobs/recommend",
    response_model=JobRecommendationResponse,
    status_code=status.HTTP_200_OK,
    tags=["recommendations"],
)
def recommend_jobs(
    payload: JobRecommendationRequest,
    http_request: Request,
) -> JobRecommendationResponse:
    return _recommendation_service(http_request).recommend(payload)


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


def _resume_analyzer(request: Request) -> ResumeProfileAnalyzer:
    return request.app.state.resume_analyzer


def _recommendation_service(request: Request) -> JobRecommendationService:
    return request.app.state.recommendation_service


def create_workflow() -> ApplicationWorkflow:
    return ApplicationWorkflow()


def _extract_resume_text(raw_resume: bytes, filename: str, content_type: str) -> str:
    lower_name = filename.lower()
    normalized_content_type = content_type.lower()
    if lower_name.endswith((".txt", ".md")) or normalized_content_type in {
        "text/plain",
        "text/markdown",
        "application/octet-stream",
    }:
        return _decode_text_resume(raw_resume)
    if lower_name.endswith(".docx") or normalized_content_type == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        return _extract_docx_text(raw_resume)
    if lower_name.endswith(".pdf") or normalized_content_type == "application/pdf":
        return _extract_pdf_text(raw_resume)

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Upload a .txt, .md, .pdf, or .docx resume.",
    )


def _decode_text_resume(raw_resume: bytes) -> str:
    try:
        return raw_resume.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text resume uploads must be UTF-8 encoded.",
        ) from exc


def _extract_docx_text(raw_resume: bytes) -> str:
    try:
        with zipfile.ZipFile(BytesIO(raw_resume)) as archive:
            document_xml = archive.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not read the DOCX resume.",
        ) from exc

    try:
        root = ET.fromstring(document_xml)
    except ET.ParseError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not parse the DOCX resume.",
        ) from exc

    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", namespace):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", namespace))
        if text.strip():
            paragraphs.append(text.strip())
    return "\n".join(paragraphs)


def _extract_pdf_text(raw_resume: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - depends on optional local install state.
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="PDF resume parsing requires the pypdf dependency to be installed.",
        ) from exc

    try:
        reader = PdfReader(BytesIO(raw_resume))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:  # pragma: no cover - pypdf raises several parser-specific errors.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from the PDF resume.",
        ) from exc
