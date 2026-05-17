# API

Base URL: `http://localhost:8000`

## `GET /health`

Returns service health.

```json
{
  "status": "ok",
  "service": "ai-job-application-copilot"
}
```

## `POST /v1/applications/analyze`

Analyze resume text and a job description.

```bash
curl -X POST http://localhost:8000/v1/applications/analyze \
  -H "Content-Type: application/json" \
  --data @examples/analyze_request.json
```

## `POST /v1/applications/analyze-file`

Analyze a plain text or markdown resume upload.

```bash
curl -X POST http://localhost:8000/v1/applications/analyze-file \
  -F "resume_file=@examples/sample_resume.txt;type=text/plain" \
  -F "job_description=<examples/sample_job_description.txt"
```

## `GET /v1/applications`

List persisted analysis summaries.

```bash
curl http://localhost:8000/v1/applications
```

## `GET /v1/applications/{analysis_id}`

Fetch a persisted analysis.

```bash
curl http://localhost:8000/v1/applications/00000000-0000-0000-0000-000000000000
```

