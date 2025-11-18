#!/usr/bin/env bash
set -euo pipefail
python -m isort src tests
python -m black src tests
