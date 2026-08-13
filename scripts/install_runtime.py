"""Install the official llama.cpp runtime selected for the current Windows GPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

from app.hardware import recommend_model_from_vram


RELEASE = "b10375"
BASE = f"https://github.com/ggml-org/llama.cpp/releases/download/{RELEASE}"
ASSET_SHA256 = {
    f"llama-{RELEASE}-bin-win-cuda-12.4-x64.zip": "dd840b604c508b2f57f2ed467f70c711d1840c07b0d09a3bba8f6dfbd8b3da84",
    "cudart-llama-bin-win-cuda-12.4-x64.zip": "8c79a9b226de4b3cacfd1f83d24f962d0773be79f1e7b75c6af4ded7e32ae1d6",
    f"llama-{RELEASE}-bin-win-vulkan-x64.zip": "1fef77a8b7742485c3f9f0acd16b68330ca9d5f447b73eb80d32862e4b2c7cfa",
    f"llama-{RELEASE}-bin-win-cpu-x64.zip": "c18ad6aa9cef9d119e957472d71e34eb5183848eb9c57f51647fd18692a456c7",
}


def detect_backend() -> tuple[str, str]:
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            text=True, timeout=8, stderr=subprocess.DEVNULL,
        ).strip().splitlines()[0]
        return "cuda", output
    except (FileNotFoundError, subprocess.SubprocessError, IndexError):
        return "vulkan", "No usable NVIDIA CUDA device was detected; Vulkan will be self-tested."


def download_zip(url: str, target: Path) -> None:
    with urllib.request.urlopen(url, timeout=180) as response, target.open("wb") as handle:
        shutil.copyfileobj(response, handle, length=4 * 1024 * 1024)


def verify_asset(path: Path) -> None:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != ASSET_SHA256[path.name]:
        raise RuntimeError(f"Runtime SHA256 mismatch: {path.name}")


def install(runtime_dir: Path) -> dict:
    backend, detail = detect_backend()
    runtime_dir.mkdir(parents=True, exist_ok=True)
    assets = [f"llama-{RELEASE}-bin-win-{backend}-x64.zip"]
    if backend == "cuda":
        assets.append("cudart-llama-bin-win-cuda-12.4-x64.zip")
    for asset in assets:
        archive = runtime_dir / asset
        if not archive.is_file():
            download_zip(f"{BASE}/{asset}", archive)
        verify_asset(archive)
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(runtime_dir)
    binary = next(runtime_dir.rglob("llama-server.exe"), None)
    if not binary:
        raise RuntimeError("llama-server.exe was not found after extraction.")
    return {"backend": backend, "detail": detail, "binary": str(binary), "release": RELEASE}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-dir", type=Path, default=Path("runtime") / RELEASE)
    parser.add_argument("--recommend-model", action="store_true")
    args = parser.parse_args()
    if args.recommend_model:
        try:
            raw = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                text=True, timeout=8, stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.SubprocessError):
            raw = ""
        print(recommend_model_from_vram(raw))
        return
    print(json.dumps(install(args.runtime_dir), ensure_ascii=False))


if __name__ == "__main__":
    main()
