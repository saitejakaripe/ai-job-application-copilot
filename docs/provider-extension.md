# Provider Extension

The default provider is deterministic and should remain the baseline for tests. To enable LLM
generation, add a provider that implements `ContentProvider` in `services/providers.py`.

## Suggested Steps

1. Add provider dependencies under the optional `llm` extra in `pyproject.toml`.
2. Implement `generate_cover_letter`, `suggest_resume_improvements`, and
   `create_interview_questions`.
3. Add provider selection in `main.py` or a small provider factory using
   `AI_COPILOT_LLM_PROVIDER`.
4. Keep deterministic tests as the default CI path.
5. Add separate integration tests that are skipped unless provider credentials are present.

## Prompting Contract

When adding an LLM provider, pass structured inputs from `CandidateProfile`, `JobProfile`,
`MatchScore`, and `missing_skills`. Return validated Pydantic models rather than free-form JSON
whenever possible.

