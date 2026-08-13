import os
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .model_files import MODEL_REPO, download_model, missing_files
from .model_runtime import ModelRuntime
from .service import PromptService


ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
MODEL_DIR = Path(os.environ.get("FAITHFUL_H3_MODEL_DIR", ROOT / "models" / "qwen35-9b-abliterated-v2"))
runtime = ModelRuntime(MODEL_DIR)
service = PromptService(runtime)
download_state = {"running": False, "error": ""}

app = FastAPI(title="liuliu Faithful H3", version="1.2.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class GenerateRequest(BaseModel):
    action: str
    mode: str = "fl2va"
    text: str = Field(min_length=1)
    strength: int = Field(default=40, ge=0, le=100)
    original: str = ""
    modules: dict | None = None


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/status")
def status():
    missing = missing_files(MODEL_DIR)
    return {
        "ready": not missing,
        "loaded": runtime.loaded,
        "downloading": download_state["running"],
        "error": download_state["error"],
        "missing": missing,
        "repo": MODEL_REPO,
        "version": app.version,
    }


def _download_worker():
    download_state.update(running=True, error="")
    try:
        download_model(MODEL_DIR)
    except Exception as exc:
        download_state["error"] = str(exc)
    finally:
        download_state["running"] = False


@app.post("/api/download")
def begin_download():
    if not missing_files(MODEL_DIR):
        return {"started": False, "ready": True}
    if not download_state["running"]:
        threading.Thread(target=_download_worker, daemon=True).start()
    return {"started": True, "ready": False}


@app.post("/api/release")
def release_memory():
    return runtime.release()


@app.post("/api/generate")
def generate(request: GenerateRequest):
    try:
        if request.action == "enrich":
            return {"output": service.enrich(request.text, request.strength)}
        if request.action == "convert":
            return service.convert(request.text, request.mode)
        if request.action == "decompose":
            return service.decompose(request.text, request.mode)
        if request.action == "convert_modules":
            return service.convert_modules(request.modules or {}, request.mode)
        if request.action == "micro":
            return service.micro_edit(request.text, request.mode, request.original)
        raise ValueError("Unknown action.")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
