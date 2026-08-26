import ctypes
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .model_files import MODEL_SPECS, download_gguf, missing_files
from .model_runtime import ModelRuntime
from .resources import ResourceMonitor
from .service import PromptService
from .vision import VISION_MODEL, VISION_MODELS, VisionCaptionRuntime, download_vision_model, vision_ready


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
VISION_ROOTS = {
    "fast": VISION_ROOT,
    "accurate": Path(os.environ.get("FAITHFUL_H3_VISION_ACCURATE_ROOT", GGUF_ROOT / "vision-accurate")),
}
if os.environ.get("FAITHFUL_H3_MODEL_DIR"):
    MODEL_DIRS["9b"] = Path(os.environ["FAITHFUL_H3_MODEL_DIR"])
if os.environ.get("FAITHFUL_H3_MODEL_4B_DIR"):
    MODEL_DIRS["4b"] = Path(os.environ["FAITHFUL_H3_MODEL_4B_DIR"])
runtime = ModelRuntime(MODEL_DIRS, gguf_paths=GGUF_PATHS,
                       gguf_binary=Path(os.environ["FAITHFUL_H3_LLAMA_BIN"]) if os.environ.get("FAITHFUL_H3_LLAMA_BIN") else None)
vision_runtimes = {
    model_id: VisionCaptionRuntime(
        VISION_ROOTS[model_id],
        binary=Path(os.environ["FAITHFUL_H3_LLAMA_BIN"]) if os.environ.get("FAITHFUL_H3_LLAMA_BIN") else None,
        port=int(os.environ.get("FAITHFUL_H3_VISION_PORT", "18766")),
        spec=spec,
    )
    for model_id, spec in VISION_MODELS.items()
}
vision_runtime = vision_runtimes["fast"]
service = PromptService(runtime)
download_state = {model_id: {"running": False, "error": ""} for model_id in MODEL_SPECS}
vision_download_states = {model_id: {"running": False, "error": ""} for model_id in VISION_MODELS}
vision_download_state = vision_download_states["fast"]
resource_monitor = ResourceMonitor()

app = FastAPI(title="liuliu Faithful H3", version="1.7.0")


@app.middleware("http")
async def prevent_stale_static_assets(request: Request, call_next):
    """Force the browser to revalidate UI code after an in-place desktop update."""
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store"
    return response


app.mount("/static", StaticFiles(directory=STATIC), name="static")


def _system_ram_snapshot() -> dict[str, int] | None:
    if os.name != "nt":
        return None

    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_physical", ctypes.c_ulonglong),
            ("available_physical", ctypes.c_ulonglong),
            ("total_page_file", ctypes.c_ulonglong),
            ("available_page_file", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended_virtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    try:
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return None
    except (AttributeError, OSError):
        return None
    mib = 1024 * 1024
    total = status.total_physical // mib
    return {"used_mib": (status.total_physical - status.available_physical) // mib, "total_mib": total}


def _vram_snapshot() -> dict[str, int] | None:
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.total,memory.used", "--format=csv,noheader,nounits"],
            text=True,
            errors="replace",
            timeout=8,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        total_text, used_text = output.splitlines()[0].split(",", 1)
        return {"used_mib": int(used_text.strip()), "total_mib": int(total_text.strip())}
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        return None


def _memory_snapshot() -> dict[str, dict[str, int] | None]:
    return {"ram": _system_ram_snapshot(), "vram": _vram_snapshot()}


def _released_memory(before: dict, after: dict) -> dict:
    result = {}
    for kind in ("ram", "vram"):
        current = after.get(kind)
        previous = before.get(kind)
        if current is None:
            result[kind] = None
            continue
        result[kind] = {
            "released_mib": max(0, int(previous["used_mib"]) - int(current["used_mib"])) if previous else 0,
            "used_mib": int(current["used_mib"]),
            "total_mib": int(current["total_mib"]),
        }
    return result


def _start_daemon(target, *args) -> None:
    threading.Thread(target=target, args=args, daemon=True).start()


class GenerateRequest(BaseModel):
    action: str
    mode: str = "fl2va"
    text: str = Field(min_length=1)
    strength: int = Field(default=40, ge=0, le=100)
    original: str = ""


class ModelRequest(BaseModel):
    model_id: str


class DownloadRequest(BaseModel):
    models: list[Literal["4b", "9b", "vision", "vision-fast", "vision-accurate"]] = Field(min_length=1)


class VisionCaptionRequest(BaseModel):
    image_data_url: str = Field(min_length=32, max_length=17_000_000)
    instruction: str = Field(default="", max_length=1000)
    language: Literal["en", "zh-CN", "zh-TW"] = "en"
    model_id: Literal["fast", "accurate"] = "fast"


class PanelBox(BaseModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)


class StoryboardRequest(BaseModel):
    image_data_url: str = Field(min_length=32, max_length=17_000_000)
    task_type: Literal["comic_panels", "viral_video"] = "comic_panels"
    goal: str = Field(default="", max_length=1200)
    language: Literal["en", "zh-CN", "zh-TW"] = "en"
    model_id: Literal["fast", "accurate"] = "accurate"
    panel_boxes: list[PanelBox] = Field(default_factory=list, max_length=40)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html", headers={"Cache-Control": "no-cache"})


def _vision_model_status(model_id: str) -> dict:
    spec = VISION_MODELS[model_id]
    ready = vision_ready(VISION_ROOTS[model_id], spec)
    state = vision_download_states[model_id]
    return {
        "id": model_id,
        "label": spec.label,
        "ready": ready,
        "loaded": vision_runtimes[model_id].loaded if ready else False,
        "downloading": state["running"],
        "error": state["error"],
        "download_bytes": spec.model_size + spec.mmproj_size,
    }


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
        "any_downloading": any(item["running"] for item in download_state.values()) or any(item["running"] for item in vision_download_states.values()),
        "vision_ready": vision_ready(VISION_ROOT),
        "vision_downloading": vision_download_state["running"],
        "vision_error": vision_download_state["error"],
        "error": model_download["error"],
        "missing": missing,
        "repo": spec.repo,
        "selected_model": runtime.selected_model,
        "models": [
            {"id": model_id, "label": item.label,
             "ready": GGUF_PATHS[model_id].is_file() or not missing_files(MODEL_DIRS[model_id], item),
             "downloading": download_state[model_id]["running"],
             "error": download_state[model_id]["error"]}
            for model_id, item in MODEL_SPECS.items()
        ],
        "vision_models": [_vision_model_status(model_id) for model_id in VISION_MODELS],
        "version": app.version,
    }


@app.get("/api/resources")
def resources():
    return resource_monitor.snapshot()


def _download_worker(model_id: str):
    model_download = download_state[model_id]
    model_download.update(running=True, error="")
    print(f"[download] Starting text model: {MODEL_SPECS[model_id].label}", flush=True)
    try:
        download_gguf(GGUF_ROOT, MODEL_SPECS[model_id])
        print(f"[download] Completed text model: {MODEL_SPECS[model_id].label}", flush=True)
    except Exception as exc:
        model_download["error"] = str(exc)
        print(f"[download] Failed text model {MODEL_SPECS[model_id].label}: {exc}", flush=True)
    finally:
        model_download["running"] = False


@app.post("/api/download")
def begin_download(request: DownloadRequest):
    requested = list(dict.fromkeys(request.models))
    started = []
    for model_id in requested:
        if model_id.startswith("vision"):
            vision_id = "accurate" if model_id == "vision-accurate" else "fast"
            spec = VISION_MODELS[vision_id]
            state = vision_download_states[vision_id]
            if not vision_ready(VISION_ROOTS[vision_id], spec) and not state["running"]:
                _start_daemon(_vision_download_worker, vision_id)
                started.append(model_id)
            continue
        if not GGUF_PATHS[model_id].is_file() and not download_state[model_id]["running"]:
            _start_daemon(_download_worker, model_id)
            started.append(model_id)
    return {
        "started": bool(started),
        "requested": requested,
        "started_models": started,
    }


@app.post("/api/model")
def select_model(request: ModelRequest):
    runtime.select(request.model_id)
    return {"selected_model": runtime.selected_model, "loaded": runtime.loaded}


@app.post("/api/release")
def release_memory():
    before = _memory_snapshot()
    text_result = runtime.release()
    vision_released = any([item.stop() for item in vision_runtimes.values()])
    after = _memory_snapshot()
    return {
        "released": bool(text_result.get("released") or vision_released),
        "loaded": False,
        "memory": _released_memory(before, after),
    }


@app.get("/api/progress")
def inference_progress():
    text_progress = runtime.progress
    vision_progresses = [item.progress for item in vision_runtimes.values()]
    active_vision = next((item for item in vision_progresses if item["active"]), None)
    if active_vision:
        return {**active_vision, "task": "vision"}
    if text_progress["active"]:
        return {**text_progress, "task": "text"}
    latest = max((text_progress, *vision_progresses), key=lambda item: item["elapsed_seconds"])
    return {**latest, "task": "idle"}


def _vision_download_worker(model_id: str = "fast"):
    spec = VISION_MODELS[model_id]
    state = vision_download_states[model_id]
    state.update(running=True, error="")
    print(f"[download] Starting vision model: {spec.label}", flush=True)
    try:
        download_vision_model(VISION_ROOTS[model_id], spec)
        print(f"[download] Completed vision model: {spec.label}", flush=True)
    except Exception as exc:
        state["error"] = str(exc)
        print(f"[download] Failed vision model {spec.label}: {exc}", flush=True)
    finally:
        state["running"] = False


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
        _start_daemon(_vision_download_worker)
    return {"started": True, "ready": False}


def _activate_vision_runtime(model_id: str) -> VisionCaptionRuntime:
    selected = vision_runtimes[model_id]
    for other_id, other in vision_runtimes.items():
        if other_id != model_id:
            other.stop()
    return selected


@app.post("/api/vision/caption")
def caption_image(request: VisionCaptionRequest):
    started = time.monotonic()
    try:
        runtime.release()
        selected = _activate_vision_runtime(request.model_id)
        output = selected.caption(request.image_data_url, request.instruction, request.language)
        return {
            "output": output,
            "runtime": {
                "backend": "gguf-vision",
                "model": VISION_MODELS[request.model_id].label,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "tokens_per_second": selected.progress["tokens_per_second"],
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/storyboard/generate")
def generate_storyboard(request: StoryboardRequest):
    started = time.monotonic()
    try:
        runtime.release()
        selected = _activate_vision_runtime(request.model_id)
        output = selected.storyboard(
            request.image_data_url,
            task_type=request.task_type,
            goal=request.goal,
            language=request.language,
            panel_boxes=[box.model_dump() for box in request.panel_boxes],
        )
        return {
            "output": output,
            "runtime": {
                "backend": "gguf-vision",
                "model": VISION_MODELS[request.model_id].label,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "tokens_per_second": selected.progress["tokens_per_second"],
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/generate")
def generate(request: GenerateRequest):
    started = time.monotonic()
    try:
        for item in vision_runtimes.values():
            item.stop()
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
                             "elapsed_seconds": round(time.monotonic() - started, 3),
                             "tokens_per_second": runtime.progress["tokens_per_second"]}
        if stages is not None:
            result["runtime"]["stages"] = stages
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
