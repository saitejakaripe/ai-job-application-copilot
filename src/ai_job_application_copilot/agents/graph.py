from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ai_job_application_copilot.agents.state import ApplicationState
from ai_job_application_copilot.agents.steps import (
    assemble_response_agent,
    cover_letter_agent,
    interview_prep_agent,
    match_score_agent,
    missing_skills_agent,
    parse_inputs_agent,
    resume_improvement_agent,
)
from ai_job_application_copilot.services.analyzer import DeterministicAnalyzer
from ai_job_application_copilot.services.providers import (
    ContentProvider,
    DeterministicContentProvider,
)

try:
    from langgraph.graph import END, StateGraph
except ImportError:  # pragma: no cover - CI installs LangGraph; this aids local bootstrapping.
    END = "__end__"
    StateGraph = None  # type: ignore[assignment]


class SequentialGraph:
    """Small fallback with LangGraph-like invoke behavior for dependency-free smoke tests."""

    def __init__(self, steps: list[Callable[[ApplicationState], ApplicationState]]) -> None:
        self.steps = steps

    def invoke(self, initial_state: ApplicationState) -> ApplicationState:
        state = dict(initial_state)
        for step in self.steps:
            state.update(step(state))
        return state


def build_application_graph(
    analyzer: DeterministicAnalyzer | None = None,
    provider: ContentProvider | None = None,
) -> Any:
    analyzer = analyzer or DeterministicAnalyzer()
    provider = provider or DeterministicContentProvider()

    nodes: dict[str, Callable[[ApplicationState], ApplicationState]] = {
        "parse_inputs": lambda state: parse_inputs_agent(state, analyzer),
        "match_score": lambda state: match_score_agent(state, analyzer),
        "missing_skills": lambda state: missing_skills_agent(state, analyzer),
        "cover_letter": lambda state: cover_letter_agent(state, provider),
        "resume_improvements": lambda state: resume_improvement_agent(state, provider),
        "interview_prep": lambda state: interview_prep_agent(state, provider),
        "assemble_response": lambda state: assemble_response_agent(state, provider),
    }

    if StateGraph is None:
        return SequentialGraph(list(nodes.values()))

    workflow = StateGraph(ApplicationState)
    for name, fn in nodes.items():
        workflow.add_node(name, fn)

    workflow.set_entry_point("parse_inputs")
    workflow.add_edge("parse_inputs", "match_score")
    workflow.add_edge("match_score", "missing_skills")
    workflow.add_edge("missing_skills", "cover_letter")
    workflow.add_edge("cover_letter", "resume_improvements")
    workflow.add_edge("resume_improvements", "interview_prep")
    workflow.add_edge("interview_prep", "assemble_response")
    workflow.add_edge("assemble_response", END)
    return workflow.compile()
