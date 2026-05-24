from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ai_job_application_copilot import __version__
from ai_job_application_copilot.api.routes import router
from ai_job_application_copilot.core.config import get_settings
from ai_job_application_copilot.db import AnalysisRepository
from ai_job_application_copilot.services.recommendations import JobRecommendationService
from ai_job_application_copilot.services.resume_profile import ResumeProfileAnalyzer
from ai_job_application_copilot.services.workflow import ApplicationWorkflow


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    repository = AnalysisRepository(settings.database_url)
    repository.init_db()
    app.state.repository = repository
    app.state.workflow = ApplicationWorkflow()
    app.state.resume_analyzer = ResumeProfileAnalyzer()
    app.state.recommendation_service = JobRecommendationService(app.state.resume_analyzer)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "Deterministic AI job application copilot with a LangGraph-style multi-agent workflow."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    mount_frontend(app)
    return app


def mount_frontend(app: FastAPI) -> None:
    app_root = Path(__file__).resolve().parents[2]
    dist_path = app_root / "frontend" / "dist"
    assets_path = dist_path / "assets"
    if not dist_path.exists():
        return

    if assets_path.exists():
        app.mount("/assets", StaticFiles(directory=assets_path), name="frontend-assets")

    def frontend_response(full_path: str) -> FileResponse:
        requested = dist_path / full_path
        if full_path and requested.is_file():
            return FileResponse(requested)
        return FileResponse(dist_path / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend(full_path: str) -> FileResponse:
        return frontend_response(full_path)

    @app.head("/{full_path:path}", include_in_schema=False)
    def serve_frontend_head(full_path: str) -> FileResponse:
        return frontend_response(full_path)


app = create_app()
