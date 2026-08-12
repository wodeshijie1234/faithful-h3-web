@echo off
setlocal
cd /d "%~dp0"
title liusheng Faithful H3 - Setup

where nvidia-smi >nul 2>nul
if errorlevel 1 (
  echo [ERROR] An NVIDIA GPU and driver are required.
  pause
  exit /b 1
)

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

echo [2/5] Updating package tools...
".venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel || goto :fail

echo [3/5] Installing CUDA PyTorch...
".venv\Scripts\python.exe" -m pip install --upgrade torch --index-url https://download.pytorch.org/whl/cu128 || goto :fail

echo [4/5] Installing application dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :fail

echo [5/5] Downloading and verifying the Qwen3.5 9B v2 model...
".venv\Scripts\python.exe" scripts\download_model.py || goto :fail

call run.bat
exit /b %errorlevel%

:fail
echo.
echo [ERROR] Setup did not complete. Review the message above and run this file again.
pause
exit /b 1
