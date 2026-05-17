from __future__ import annotations

from ai_job_application_copilot.db import AnalysisRepository
from ai_job_application_copilot.models import AnalysisRequest, ApplicationAnalysis
from ai_job_application_copilot.services.workflow import ApplicationWorkflow


class ApplicationService:
    def __init__(
        self,
        repository: AnalysisRepository,
        workflow: ApplicationWorkflow | None = None,
    ) -> None:
        self.repository = repository
        self.workflow = workflow or ApplicationWorkflow()

    def analyze(self, request: AnalysisRequest) -> ApplicationAnalysis:
        analysis = self.workflow.run(request)
        if not request.persist:
            return analysis
        return self.repository.save(request, analysis)
