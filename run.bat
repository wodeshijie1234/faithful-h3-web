@echo off
setlocal
cd /d "%~dp0"
title liuliu Faithful H3 v1.3.0
set "PYTHONNOUSERSITE=1"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] The application is not installed yet. Run install-and-run.bat first.
  pause
  exit /b 1
)

if not defined FAITHFUL_H3_LLAMA_BIN (
  for /f "delims=" %%L in ('where /r runtime llama-server.exe 2^>nul') do if not defined FAITHFUL_H3_LLAMA_BIN set "FAITHFUL_H3_LLAMA_BIN=%%L"
)
if not defined FAITHFUL_H3_LLAMA_BIN (
  echo [ERROR] The local inference runtime is missing. Run install-and-run.bat to repair it.
  pause
  exit /b 1
)

echo Starting liuliu Faithful H3 at http://127.0.0.1:7868/
start "" "http://127.0.0.1:7868/"
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 7868
if errorlevel 1 pause
