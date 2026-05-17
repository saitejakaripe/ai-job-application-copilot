from __future__ import annotations

from ai_job_application_copilot.agents import build_application_graph
from ai_job_application_copilot.models import AnalysisRequest, ApplicationAnalysis
from ai_job_application_copilot.services.analyzer import DeterministicAnalyzer
from ai_job_application_copilot.services.providers import (
    ContentProvider,
    DeterministicContentProvider,
)


class ApplicationWorkflow:
    def __init__(
        self,
        analyzer: DeterministicAnalyzer | None = None,
        provider: ContentProvider | None = None,
    ) -> None:
        self.analyzer = analyzer or DeterministicAnalyzer()
        self.provider = provider or DeterministicContentProvider()
        self.graph = build_application_graph(self.analyzer, self.provider)

    def run(self, request: AnalysisRequest) -> ApplicationAnalysis:
        final_state = self.graph.invoke({"request": request})
        return final_state["analysis"]
