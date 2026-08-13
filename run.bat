@echo off
setlocal
cd /d "%~dp0"
title liusheng Faithful H3 v1.1.0

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] The application is not installed yet. Run install-and-run.bat first.
  pause
  exit /b 1
)

echo Starting liusheng Faithful H3 at http://127.0.0.1:7868/
start "" "http://127.0.0.1:7868/"
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 7868
if errorlevel 1 pause
