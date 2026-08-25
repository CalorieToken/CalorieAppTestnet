# Contributing to CalorieAppTestnet

> Legal Notice: By contributing (issues, PRs, discussions) you accept the beta/Testnet risk, absence of warranties, and non-advice clauses defined in `docs/LEGAL_DISCLAIMER.md`. Do not submit proprietary or sensitive personal data.

> IP Notice: A submission is not accepted or merged until authorship,
> provenance, employer/contractor rights, third-party licences, and any
> AI-assisted material are disclosed. Opening a pull request does not transfer
> ownership. A separate written assignment or project-compatible licence must
> be agreed with ICTHendrikse before merge.

This repository is an inactive historical Testnet prototype. It is retained for
evidence and review, not as a supported installation source. Do not publish a
package or binary from this repository without a fresh dependency, security,
licensing, and regulatory review.

## Historical development information

The earlier quick-start and runtime instructions are intentionally withdrawn.
`requirements.txt`, build files, and scripts document the prototype's former
environment but are not a lockfile or a presently supported build procedure.
Security reviewers may inspect the repository without executing it.

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

## Dependency records

The dependency manifests are historical inventories. They contain broad ranges
and a development-branch reference and therefore do not reproduce a reviewed
environment. Any revival must create a fresh lockfile and third-party notices
from verified upstream releases before code is run or distributed.

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
