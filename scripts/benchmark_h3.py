from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROMPT = (
    "镜头1：女人站在左边，男人站在右边，女人抬起右手。"
    "镜头2：男人向前走一步，女人保持原位。"
    "镜头3：仰拍，女人和男人同时抬头。"
)


def count_output_shots(output: str) -> int:
    description = str(output).partition("integrated_multimodal_description:")[2]
    description = description.partition("\noverall_soundscape:")[0]
    return len(re.findall(r"\[Shot \d+\]", description))


def post(base_url: str, path: str, payload: dict, timeout: float) -> tuple[int, bytes]:
    request = Request(
        base_url + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except HTTPError as exc:
        return exc.code, exc.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=("4b", "9b"), required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:7868")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=180.0)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    post(args.base_url, "/api/release", {}, 20)
    post(args.base_url, "/api/model", {"model_id": args.model}, 20)
    payload = {"action": "convert", "mode": "fl2va", "text": PROMPT, "strength": 40}

    for index, phase in enumerate(("cold", "warm1", "warm2", "warm3")):
        stem = args.output_dir / f"{args.model}-{phase}"
        stem.with_suffix(".request.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        meta = {"model": args.model, "phase": phase, "timeout_seconds": args.timeout,
                "started_unix": time.time(), "state": "started"}
        stem.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        started = time.monotonic()
        try:
            status, body = post(args.base_url, "/api/generate", payload, args.timeout)
            elapsed = time.monotonic() - started
            stem.with_suffix(".response.json").write_bytes(body)
            meta.update(state="completed", http_status=status, http_elapsed_seconds=round(elapsed, 3),
                        response_bytes=len(body))
            try:
                response = json.loads(body.decode("utf-8"))
                output = str(response.get("output", ""))
                meta.update(runtime_elapsed_seconds=(response.get("runtime") or {}).get("elapsed_seconds"),
                            output_characters=len(output), shot_count=count_output_shots(output))
            except (UnicodeDecodeError, json.JSONDecodeError):
                meta["parse_error"] = "response was not UTF-8 JSON"
        except (TimeoutError, URLError, OSError) as exc:
            elapsed = time.monotonic() - started
            meta.update(state="timeout_or_error", http_elapsed_seconds=round(elapsed, 3), error=str(exc))
        stem.with_suffix(".meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps(meta, ensure_ascii=False), flush=True)
        if meta["state"] != "completed" or meta.get("http_status") != 200:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
