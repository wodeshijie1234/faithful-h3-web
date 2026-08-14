"""Run one real image-caption request against the local GGUF vision model."""

from __future__ import annotations

import argparse
import base64
import mimetypes
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.vision import VisionCaptionRuntime, verify_vision_model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--model-root", type=Path, default=ROOT / "models" / "vision")
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--port", type=int, default=18767)
    parser.add_argument("--language", choices=("en", "zh-CN", "zh-TW"), default="en")
    args = parser.parse_args()

    verify_vision_model(args.model_root)
    mime_type = mimetypes.guess_type(args.image.name)[0] or ""
    if mime_type == "image/jpg":
        mime_type = "image/jpeg"
    encoded = base64.b64encode(args.image.read_bytes()).decode("ascii")
    data_url = f"data:{mime_type};base64,{encoded}"
    runtime = VisionCaptionRuntime(args.model_root, binary=args.binary, port=args.port)
    started = time.monotonic()
    try:
        output = runtime.caption(data_url, "Focus on composition and subject positions.", args.language)
        print(f"Elapsed: {time.monotonic() - started:.3f}s")
        print(output)
    finally:
        runtime.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
