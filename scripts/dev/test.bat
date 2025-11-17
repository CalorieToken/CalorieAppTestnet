@echo off
setlocal
python -m pytest -q --disable-warnings --maxfail=1 --cov=src --cov-report=term-missing
endlocal
