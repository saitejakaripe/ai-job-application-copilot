#!/usr/bin/env bash
set -euo pipefail

curl -X POST http://localhost:8000/v1/applications/analyze \
  -H "Content-Type: application/json" \
  --data @examples/analyze_request.json

