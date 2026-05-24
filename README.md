# AI Job Application Copilot

Production-style FastAPI backend for tailoring job applications with a deterministic
multi-agent workflow. The first version does not require paid LLM keys: it uses rule-based
analysis and templated generation so scoring, cover letters, resume suggestions, and interview
prep are repeatable in tests and CI.

## What It Does

- Accepts resume text or a plain text resume upload plus a job description.
- Calculates a deterministic job match score.
- Identifies missing skills from the job description.
- Generates a tailored cover letter.
- Suggests concrete resume improvements.
- Creates interview preparation questions.
- Persists analyses in SQLite.
- Uses LangGraph for the workflow when installed, with clear extension points for OpenAI or
  other LLM providers.

## Tech Stack

Python 3.11+, FastAPI, LangGraph, Pydantic, SQLite, pytest, Docker, GitHub Actions.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
uvicorn ai_job_application_copilot.main:app --reload
```

Open:

- API: <http://localhost:8000>
- Docs: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>

## Job Recommendation Website

The full-stack website analyzes a resume, collects candidate preferences, and recommends matching
India and abroad remote jobs from a curated catalog plus trusted source links.

Run the backend:

```bash
source .venv/bin/activate
uvicorn ai_job_application_copilot.main:app --host 127.0.0.1 --port 8000
```

Run the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open <http://127.0.0.1:5173>. If port 5173 is already busy, Vite will print the next local URL.

Build the frontend and serve it from FastAPI:

```bash
cd frontend
npm run build
cd ..
uvicorn ai_job_application_copilot.main:app --host 127.0.0.1 --port 8000
```

## Example Request

```bash
curl -X POST http://localhost:8000/v1/applications/analyze \
  -H "Content-Type: application/json" \
  --data @examples/analyze_request.json
```

Upload a resume text file:

```bash
curl -X POST http://localhost:8000/v1/applications/analyze-file \
  -F "resume_file=@examples/sample_resume.txt;type=text/plain" \
  -F "job_description=<examples/sample_job_description.txt" \
  -F "candidate_name=Avery Patel" \
  -F "role_title=AI Automation Engineer" \
  -F "company_name=Northstar Robotics"
```

## Local Checks

```bash
make install-dev
make lint
make test
```

## Docker

```bash
docker compose up --build
```

The API will be available at <http://localhost:8000>.

## Workflow

The LangGraph workflow is deterministic and decomposed into focused agents:

1. Parse resume and job description.
2. Calculate match score.
3. Identify missing skills.
4. Generate cover letter.
5. Suggest resume improvements.
6. Create interview prep questions.
7. Assemble the API response.

See [docs/architecture.md](docs/architecture.md) for the full design.

## LLM Extension Point

`DeterministicContentProvider` is the default. To add paid generation, implement the methods in
`OpenAIContentProvider` or add another provider that satisfies the `ContentProvider` protocol.
Keep the deterministic provider in tests so CI remains stable and free.

See [docs/provider-extension.md](docs/provider-extension.md).
