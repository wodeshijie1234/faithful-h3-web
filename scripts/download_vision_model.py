"""Download and verify the optional local image-caption model."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.vision import VISION_MODEL, download_vision_model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", type=Path, default=ROOT / "models" / "vision")
    args = parser.parse_args()
    print(f"Downloading {VISION_MODEL.label} to: {args.destination}", flush=True)
    model_path, mmproj_path = download_vision_model(args.destination)
    print(f"Verified: {model_path}", flush=True)
    print(f"Verified: {mmproj_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
