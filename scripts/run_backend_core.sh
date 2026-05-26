#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../backend"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-core.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
