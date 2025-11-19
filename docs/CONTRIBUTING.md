# Contributing to CalorieAppTestnet

> Legal Notice: By contributing (issues, PRs, discussions) you accept the beta/Testnet risk, absence of warranties, and non-advice clauses defined in `docs/LEGAL_DISCLAIMER.md`. Do not submit proprietary or sensitive personal data.

Thanks for contributing! This guide helps you set up a consistent dev environment and workflow.

## Quick Start

1. Python 3.12 recommended.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run locally:
   ```bash
   python -u run.py
   ```
4. Validate KV files:
   ```bash
   python -u scripts/kv_sanity_check.py
   ```

## Code Style
- Black (line length 100), isort (black profile), flake8.
- EditorConfig is included for consistent whitespace and newlines.

## Pre-commit hooks (recommended)
```bash
pip install pre-commit
pre-commit install
# run on all files
pre-commit run --all-files
```

What it does:
- Runs linters/formatters from `.pre-commit-config.yaml` before each commit.
- Ensures Black, isort, and flake8 consistency across contributors.

If a hook modifies files, re-add them and commit again.

## Dependency management with pip-tools (optional, recommended)
We keep `requirements.txt` checked in for easy installs. For clean upgrades and lockfiles, use pip-tools:

```bash
pip install pip-tools

# Edit high-level deps in requirements.in, then compile a locked requirements.txt
pip-compile --upgrade

# Install exactly what's in requirements.txt
pip-sync
```

Notes:
- Edit `requirements.in` for top-level packages. `requirements.txt` is generated.
- CI installs from `requirements.txt`.
- Use `--upgrade` only when you intend to refresh versions.

## Tests
```bash
python -m pytest -q --disable-warnings --maxfail=1 --cov=src --cov-report=term-missing
```

## CI
- GitHub Actions runs lint, format check, tests (Ubuntu + Windows), and a KV sanity check.
- CodeQL code scanning runs on push/PR and weekly schedule for Python.
- Please keep PRs focused, with clear descriptions and screenshots for UI changes.

## PR Tips
- Update or add docs for new behaviors.
- Avoid large unrelated refactors.
- Prefer small focused commits; link issues when applicable.
