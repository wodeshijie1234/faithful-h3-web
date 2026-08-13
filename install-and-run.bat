@echo off
setlocal
cd /d "%~dp0"
title liuliu Faithful H3 - Setup
set "PYTHONNOUSERSITE=1"

set "FH3_PYTHON="
where py >nul 2>nul && py -3.11 -c "import sys; assert sys.version_info[:2] == (3, 11)" >nul 2>nul && set "FH3_PYTHON=py -3.11"
if not defined FH3_PYTHON where py >nul 2>nul && py -3.10 -c "import sys; assert sys.version_info[:2] == (3, 10)" >nul 2>nul && set "FH3_PYTHON=py -3.10"
if not defined FH3_PYTHON (
  echo [ERROR] Python 3.10 or 3.11 was not found.
  echo Install 64-bit Python from https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/5] Creating isolated Python environment...
  %FH3_PYTHON% -m venv .venv || goto :fail
)

echo [2/5] Installing the web application...
".venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel || goto :fail
".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :fail

echo [3/5] Detecting GPU and installing the official inference runtime...
for /f "delims=" %%L in ('".venv\Scripts\python.exe" scripts\install_runtime.py --runtime-dir runtime') do set "FH3_RUNTIME_RESULT=%%L"
if errorlevel 1 goto :fail
for /f "delims=" %%L in ('where /r runtime llama-server.exe') do set "FAITHFUL_H3_LLAMA_BIN=%%L"
if not defined FAITHFUL_H3_LLAMA_BIN goto :fail

for /f "delims=" %%M in ('".venv\Scripts\python.exe" scripts\install_runtime.py --recommend-model') do set "FH3_MODEL=%%M"
if not defined FH3_MODEL set "FH3_MODEL=4b"

echo [4/5] Downloading the recommended %FH3_MODEL% model with resume support...
".venv\Scripts\python.exe" scripts\download_model.py %FH3_MODEL% || goto :fail

echo [5/5] Running startup checks...
".venv\Scripts\python.exe" scripts\self_check.py %FH3_MODEL% --model-root models --binary "%FAITHFUL_H3_LLAMA_BIN%" || goto :fail
call run.bat
exit /b %errorlevel%

:fail
echo.
echo [ERROR] Setup did not complete. Review the message above and run this file again.
pause
exit /b 1
