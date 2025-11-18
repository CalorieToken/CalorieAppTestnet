#!/usr/bin/env bash
set -euo pipefail
python -m pytest -q --disable-warnings --maxfail=1 --cov=src --cov-report=term-missing
