from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_job_application_copilot import __version__
from ai_job_application_copilot.api.routes import router
from ai_job_application_copilot.core.config import get_settings
from ai_job_application_copilot.db import AnalysisRepository
from ai_job_application_copilot.services.workflow import ApplicationWorkflow


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    repository = AnalysisRepository(settings.database_url)
    repository.init_db()
    app.state.repository = repository
    app.state.workflow = ApplicationWorkflow()
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
    return app


app = create_app()

