import os
import threading
import time
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .model_files import MODEL_SPECS, download_gguf, missing_files
from .model_runtime import ModelRuntime
from .service import PromptService
from .vision import VISION_MODEL, VisionCaptionRuntime, download_vision_model, vision_ready


ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
MODEL_ROOT = Path(os.environ.get("FAITHFUL_H3_MODEL_ROOT", ROOT / "models"))
MODEL_DIRS = {model_id: MODEL_ROOT / spec.directory for model_id, spec in MODEL_SPECS.items()}
GGUF_ROOT = Path(os.environ.get("FAITHFUL_H3_GGUF_ROOT", ROOT / "models"))
GGUF_PATHS = {
    "4b": Path(os.environ.get("FAITHFUL_H3_GGUF_4B_PATH", GGUF_ROOT / MODEL_SPECS["4b"].gguf_filename)),
    "9b": Path(os.environ.get("FAITHFUL_H3_GGUF_9B_PATH", GGUF_ROOT / MODEL_SPECS["9b"].gguf_filename)),
}
VISION_ROOT = Path(os.environ.get("FAITHFUL_H3_VISION_ROOT", GGUF_ROOT / "vision"))
if os.environ.get("FAITHFUL_H3_MODEL_DIR"):
    MODEL_DIRS["9b"] = Path(os.environ["FAITHFUL_H3_MODEL_DIR"])
if os.environ.get("FAITHFUL_H3_MODEL_4B_DIR"):
    MODEL_DIRS["4b"] = Path(os.environ["FAITHFUL_H3_MODEL_4B_DIR"])
runtime = ModelRuntime(MODEL_DIRS, gguf_paths=GGUF_PATHS,
                       gguf_binary=Path(os.environ["FAITHFUL_H3_LLAMA_BIN"]) if os.environ.get("FAITHFUL_H3_LLAMA_BIN") else None)
vision_runtime = VisionCaptionRuntime(
    VISION_ROOT,
    binary=Path(os.environ["FAITHFUL_H3_LLAMA_BIN"]) if os.environ.get("FAITHFUL_H3_LLAMA_BIN") else None,
    port=int(os.environ.get("FAITHFUL_H3_VISION_PORT", "18766")),
)
service = PromptService(runtime)
download_state = {model_id: {"running": False, "error": ""} for model_id in MODEL_SPECS}
vision_download_state = {"running": False, "error": ""}

app = FastAPI(title="liuliu Faithful H3", version="1.4.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class GenerateRequest(BaseModel):
    action: str
    mode: str = "fl2va"
    text: str = Field(min_length=1)
    strength: int = Field(default=40, ge=0, le=100)
    original: str = ""


class ModelRequest(BaseModel):
    model_id: str


class VisionCaptionRequest(BaseModel):
    image_data_url: str = Field(min_length=32, max_length=17_000_000)
    instruction: str = Field(default="", max_length=1000)
    language: Literal["en", "zh-CN", "zh-TW"] = "en"


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html", headers={"Cache-Control": "no-cache"})


@app.get("/api/status")
def status():
    spec = MODEL_SPECS[runtime.selected_model]
    model_download = download_state[runtime.selected_model]
    gguf_ready = GGUF_PATHS[runtime.selected_model].is_file()
    missing = [] if gguf_ready else missing_files(MODEL_DIRS[runtime.selected_model], spec)
    return {
        "ready": not missing,
        "loaded": runtime.loaded,
        "backend": runtime.backend,
        "downloading": model_download["running"],
        "error": model_download["error"],
        "missing": missing,
        "repo": spec.repo,
        "selected_model": runtime.selected_model,
        "models": [
            {"id": model_id, "label": item.label,
             "ready": GGUF_PATHS[model_id].is_file() or not missing_files(MODEL_DIRS[model_id], item)}
            for model_id, item in MODEL_SPECS.items()
        ],
        "version": app.version,
    }


def _download_worker(model_id: str):
    model_download = download_state[model_id]
    model_download.update(running=True, error="")
    try:
        download_gguf(GGUF_ROOT, MODEL_SPECS[model_id])
    except Exception as exc:
        model_download["error"] = str(exc)
    finally:
        model_download["running"] = False


@app.post("/api/download")
def begin_download():
    model_id = runtime.selected_model
    if GGUF_PATHS[model_id].is_file():
        return {"started": False, "ready": True}
    if not download_state[model_id]["running"]:
        threading.Thread(target=_download_worker, args=(model_id,), daemon=True).start()
    return {"started": True, "ready": False}


@app.post("/api/model")
def select_model(request: ModelRequest):
    runtime.select(request.model_id)
    return {"selected_model": runtime.selected_model, "loaded": runtime.loaded}


@app.post("/api/release")
def release_memory():
    text_result = runtime.release()
    vision_released = vision_runtime.stop()
    return {"released": bool(text_result.get("released") or vision_released), "loaded": False}


def _vision_download_worker():
    vision_download_state.update(running=True, error="")
    try:
        download_vision_model(VISION_ROOT)
    except Exception as exc:
        vision_download_state["error"] = str(exc)
    finally:
        vision_download_state["running"] = False


@app.get("/api/vision/status")
def vision_status():
    return {
        "ready": vision_ready(VISION_ROOT),
        "loaded": vision_runtime.loaded,
        "downloading": vision_download_state["running"],
        "error": vision_download_state["error"],
        "label": VISION_MODEL.label,
        "repo": VISION_MODEL.repo,
        "download_bytes": VISION_MODEL.model_size + VISION_MODEL.mmproj_size,
    }


@app.post("/api/vision/download")
def begin_vision_download():
    if vision_ready(VISION_ROOT):
        return {"started": False, "ready": True}
    if not vision_download_state["running"]:
        threading.Thread(target=_vision_download_worker, daemon=True).start()
    return {"started": True, "ready": False}


@app.post("/api/vision/caption")
def caption_image(request: VisionCaptionRequest):
    started = time.monotonic()
    try:
        runtime.release()
        output = vision_runtime.caption(request.image_data_url, request.instruction, request.language)
        return {
            "output": output,
            "runtime": {
                "backend": "gguf-vision",
                "model": VISION_MODEL.label,
                "elapsed_seconds": round(time.monotonic() - started, 3),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/generate")
def generate(request: GenerateRequest):
    started = time.monotonic()
    try:
        vision_runtime.stop()
        if request.action == "enrich":
            result = {"output": service.enrich(request.text, request.strength)}
        elif request.action == "convert":
            result = service.convert(request.text, request.mode)
        elif request.action == "micro":
            result = service.micro_edit(request.text, request.mode, request.original)
        else:
            raise ValueError("Unknown action.")
        stages = result.pop("_stages", None)
        result["runtime"] = {"backend": runtime.backend, "model": runtime.selected_model,
                             "elapsed_seconds": round(time.monotonic() - started, 3)}
        if stages is not None:
            result["runtime"]["stages"] = stages
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
