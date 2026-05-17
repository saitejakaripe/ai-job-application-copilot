.PHONY: install install-dev run test lint format docker-build docker-run

install:
	python -m pip install -e .

install-dev:
	python -m pip install -e ".[dev]"

run:
	uvicorn ai_job_application_copilot.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

docker-build:
	docker build -t ai-job-application-copilot:latest .

docker-run:
	docker run --rm -p 8000:8000 -v "$$(pwd)/data:/data" ai-job-application-copilot:latest

