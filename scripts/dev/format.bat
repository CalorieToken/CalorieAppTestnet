@echo off
setlocal
python -m isort src tests
python -m black src tests
endlocal
