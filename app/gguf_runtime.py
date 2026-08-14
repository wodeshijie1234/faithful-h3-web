"""Small lifecycle wrapper around the official llama.cpp server binary."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


class GgufRuntime:
    def __init__(self, model_path: Path, *, binary: Path | None = None, port: int = 0,
                 mmproj_path: Path | None = None, context_size: int | None = None):
        self.model_path = Path(model_path)
        self.mmproj_path = Path(mmproj_path) if mmproj_path else None
        self.binary = Path(binary or os.environ.get("FAITHFUL_H3_LLAMA_BIN", "llama-server.exe"))
        self.port = int(port or os.environ.get("FAITHFUL_H3_LLAMA_PORT", "18765"))
        self.host = os.environ.get("FAITHFUL_H3_LLAMA_HOST", "127.0.0.1")
        self.context_size = int(context_size or os.environ.get("FAITHFUL_H3_LLAMA_CONTEXT", "4096"))
        self.process: subprocess.Popen | None = None
        self.started_at: float | None = None

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def loaded(self) -> bool:
        return self._healthy()

    def _healthy(self) -> bool:
        try:
            with urlopen(Request(self.base_url + "/props"), timeout=1.5) as response:
                props = json.loads(response.read().decode("utf-8"))
            loaded = Path(str(props.get("model_path", ""))).resolve()
            return loaded == self.model_path.resolve()
        except (OSError, URLError, json.JSONDecodeError, RuntimeError):
            return False

    def ensure_started(self) -> None:
        if self._healthy():
            return
        try:
            with urlopen(Request(self.base_url + "/health"), timeout=1.5) as response:
                if response.status == 200:
                    raise RuntimeError(f"Port {self.port} is already serving a different model.")
        except (URLError, TimeoutError, OSError):
            pass
        if not self.binary.is_file():
            raise RuntimeError(f"llama-server.exe was not found: {self.binary}")
        if not self.model_path.is_file():
            raise RuntimeError(f"GGUF model was not found: {self.model_path}")
        if self.mmproj_path and not self.mmproj_path.is_file():
            raise RuntimeError(f"Vision projector was not found: {self.mmproj_path}")
        if self.process and self.process.poll() is not None:
            self.process = None
        command = [
            str(self.binary), "-m", str(self.model_path), "-ngl", os.environ.get("FAITHFUL_H3_LLAMA_GPU_LAYERS", "99"),
            "-c", str(self.context_size), "--host", self.host,
            "--port", str(self.port), "--log-disable",
        ]
        if self.mmproj_path:
            command.extend(("--mmproj", str(self.mmproj_path), "--image-min-tokens", "1024"))
        self.process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.started_at = time.monotonic()
        deadline = time.monotonic() + float(os.environ.get("FAITHFUL_H3_LLAMA_START_TIMEOUT", "90"))
        while time.monotonic() < deadline:
            if self._healthy():
                return
            if self.process.poll() is not None:
                raise RuntimeError(f"llama-server exited with code {self.process.returncode}")
            time.sleep(0.25)
        self.stop()
        raise RuntimeError("Timed out while starting the GGUF runtime.")

    def generate(self, user_text: str, system_text: str, *, temperature: float, top_p: float,
                 max_new_tokens: int = 1400, stop_on_json: bool = False) -> str:
        messages = [{"role": "system", "content": system_text}, {"role": "user", "content": user_text}]
        return self._chat_completion(
            messages,
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=max_new_tokens,
            stop_on_json=stop_on_json,
        )

    def generate_with_image(self, image_data_url: str, instruction: str, system_text: str, *,
                            max_new_tokens: int = 900) -> str:
        messages = []
        if system_text:
            messages.append({"role": "system", "content": system_text})
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                    {"type": "text", "text": instruction},
                ],
            }
        )
        return self._chat_completion(
            messages,
            temperature=0.1,
            top_p=0.8,
            max_new_tokens=max_new_tokens,
        )

    def _chat_completion(self, messages: list[dict], *, temperature: float, top_p: float,
                         max_new_tokens: int, stop_on_json: bool = False) -> str:
        self.ensure_started()
        payload = {
            "model": "local",
            "messages": messages,
            "temperature": max(0.01, float(temperature)), "top_p": float(top_p),
            "max_tokens": int(max_new_tokens), "stream": False,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        if stop_on_json:
            payload["response_format"] = {"type": "json_object"}
        request = Request(
            self.base_url + "/v1/chat/completions", data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
            with urlopen(request, timeout=float(os.environ.get("FAITHFUL_H3_LLAMA_REQUEST_TIMEOUT", "180"))) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (OSError, URLError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"GGUF generation failed: {exc}") from exc
        choices = result.get("choices") or []
        if not choices:
            raise RuntimeError("GGUF runtime returned no choices.")
        message = choices[0].get("message") or {}
        content = message.get("content") or ""
        if not content and message.get("reasoning_content"):
            content = message["reasoning_content"]
        return str(content).strip()

    def stop(self) -> None:
        process, self.process = self.process, None
        if not process:
            return
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
