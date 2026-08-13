"""Verify a downloaded GGUF and its official llama.cpp runtime."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.gguf_runtime import GgufRuntime
from app.model_files import MODEL_SPECS, ModelSpec, verify_gguf_file


def run_self_check(model: Path, spec: ModelSpec, binary: Path, *, port: int = 18765,
                   runtime: GgufRuntime | None = None) -> dict:
    model = Path(model)
    verify_gguf_file(model, spec)
    runtime = runtime or GgufRuntime(model, binary=Path(binary), port=port)
    try:
        runtime.ensure_started()
        output = runtime.generate(
            "Reply with exactly OK.",
            "Return only the requested answer without reasoning.",
            temperature=0.01,
            top_p=0.1,
            max_new_tokens=8,
        ).strip()
        if not output or any(character == "\ufffd" for character in output):
            raise RuntimeError("The runtime did not return readable text.")
        return {"model": spec.id, "backend": "gguf", "output": output}
    finally:
        runtime.stop()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model_id", choices=MODEL_SPECS)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--model-root", type=Path, default=Path("models"))
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--port", type=int, default=18765)
    args = parser.parse_args()
    spec = MODEL_SPECS[args.model_id]
    model = args.model or args.model_root / spec.gguf_filename
    result = run_self_check(model, spec, args.binary, port=args.port)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
