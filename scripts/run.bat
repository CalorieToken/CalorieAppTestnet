@echo off
REM CalorieApp Windows Launch Script
REM Convenient batch file to launch the app on Windows

echo 🚀 Starting CalorieApp...
cd /d "%~dp0.."
python main.py
pause