@echo off
setlocal
cd /d "%~dp0"
title liuliu Faithful H3 v1.1.2
set "PYTHONNOUSERSITE=1"

if not defined FAITHFUL_H3_MODEL_DIR (
  for /f "tokens=2,*" %%A in ('reg query "HKCU\Environment" /v "FAITHFUL_H3_MODEL_DIR" 2^>nul ^| find "FAITHFUL_H3_MODEL_DIR"') do set "FAITHFUL_H3_MODEL_DIR=%%B"
)

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] The application is not installed yet. Run install-and-run.bat first.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -c "import torch; assert torch.cuda.is_available(), 'CUDA is unavailable'; print('[OK] PyTorch', torch.__version__, '| CUDA', torch.version.cuda)"
if errorlevel 1 (
  echo [ERROR] PyTorch or CUDA self-check failed. Run install-and-run.bat to repair the isolated environment.
  pause
  exit /b 1
)

echo Starting liuliu Faithful H3 at http://127.0.0.1:7868/
start "" "http://127.0.0.1:7868/"
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 7868
if errorlevel 1 pause
