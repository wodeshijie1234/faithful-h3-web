"""Small lifecycle wrapper around the official llama.cpp server binary."""

from __future__ import annotations

import json
import os
import subprocess
import threading
import time
import ctypes
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
        self._progress_lock = threading.Lock()
        self._progress = {
            "active": False,
            "generated_tokens": 0,
            "tokens_per_second": 0.0,
            "elapsed_seconds": 0.0,
        }

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def loaded(self) -> bool:
        return self._healthy()

    @property
    def progress(self) -> dict:
        with self._progress_lock:
            snapshot = dict(self._progress)
        if snapshot["active"] and self.started_at is not None:
            snapshot["elapsed_seconds"] = round(time.monotonic() - self.started_at, 3)
        return snapshot

    def _set_progress(self, *, active: bool, generated_tokens: int = 0,
                      tokens_per_second: float = 0.0) -> None:
        elapsed = max(0.0, time.monotonic() - self.started_at) if self.started_at is not None else 0.0
        with self._progress_lock:
            self._progress = {
                "active": active,
                "generated_tokens": int(generated_tokens),
                "tokens_per_second": round(float(tokens_per_second), 2),
                "elapsed_seconds": round(elapsed, 3),
            }

    def _healthy(self) -> bool:
        try:
            with urlopen(Request(self.base_url + "/props"), timeout=1.5) as response:
                props = json.loads(response.read().decode("utf-8"))
            loaded = Path(str(props.get("model_path", ""))).resolve()
            return loaded == self.model_path.resolve()
        except (OSError, URLError, json.JSONDecodeError, RuntimeError):
            return False

    def _listening_pid(self) -> int | None:
        if os.name != "nt":
            return None
        try:
            output = subprocess.check_output(
                ["netstat", "-ano", "-p", "tcp"],
                text=True,
                errors="ignore",
                timeout=5,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        for line in output.splitlines():
            parts = line.split()
            if len(parts) < 5 or parts[0].upper() != "TCP" or parts[3].upper() != "LISTENING":
                continue
            if parts[1].rsplit(":", 1)[-1] == str(self.port):
                try:
                    return int(parts[4])
                except ValueError:
                    return None
        return None

    @staticmethod
    def _pid_executable(pid: int) -> Path | None:
        if os.name != "nt":
            return None
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, int(pid))
        if not handle:
            return None
        try:
            size = ctypes.c_ulong(32768)
            buffer = ctypes.create_unicode_buffer(size.value)
            if not kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
                return None
            return Path(buffer.value)
        finally:
            kernel32.CloseHandle(handle)

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
            "--port", str(self.port), "--flash-attn", "on", "--log-disable",
        ]
        if self.mmproj_path:
            command.extend((
                "--mmproj", str(self.mmproj_path),
                "--image-min-tokens", os.environ.get("FAITHFUL_H3_VISION_MIN_TOKENS", "256"),
                "--image-max-tokens", os.environ.get("FAITHFUL_H3_VISION_MAX_TOKENS", "512"),
            ))
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
        self.started_at = time.monotonic()
        self._set_progress(active=True)
        self.ensure_started()
        payload = {
            "model": "local",
            "messages": messages,
            "temperature": max(0.01, float(temperature)), "top_p": float(top_p),
            "max_tokens": int(max_new_tokens), "stream": True,
            "stream_options": {"include_usage": True},
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
                if not hasattr(response, "__iter__"):
                    result = json.loads(response.read().decode("utf-8"))
                    choices = result.get("choices") or []
                    if not choices:
                        raise RuntimeError("GGUF runtime returned no choices.")
                    message = choices[0].get("message") or {}
                    content = message.get("content") or message.get("reasoning_content") or ""
                    usage = result.get("usage") or {}
                    tokens = int(usage.get("completion_tokens") or max(1, len(str(content).split())))
                    elapsed = max(time.monotonic() - self.started_at, 0.001)
                    self._set_progress(active=False, generated_tokens=tokens, tokens_per_second=tokens / elapsed)
                    return str(content).strip()

                chunks = []
                generated_tokens = 0
                exact_tokens = None
                exact_rate = None
                for raw_line in response:
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    event = json.loads(data)
                    choices = event.get("choices") or []
                    if choices:
                        delta = choices[0].get("delta") or {}
                        content = delta.get("content") or ""
                        if content:
                            chunks.append(str(content))
                            generated_tokens += 1
                    usage = event.get("usage") or {}
                    if usage.get("completion_tokens") is not None:
                        exact_tokens = int(usage["completion_tokens"])
                    timings = event.get("timings") or {}
                    if timings.get("predicted_per_second") is not None:
                        exact_rate = float(timings["predicted_per_second"])
                    elapsed = max(time.monotonic() - self.started_at, 0.001)
                    visible_tokens = exact_tokens if exact_tokens is not None else generated_tokens
                    self._set_progress(
                        active=True,
                        generated_tokens=visible_tokens,
                        tokens_per_second=exact_rate if exact_rate is not None else visible_tokens / elapsed,
                    )
                content = "".join(chunks).strip()
                final_tokens = exact_tokens if exact_tokens is not None else generated_tokens
                elapsed = max(time.monotonic() - self.started_at, 0.001)
                self._set_progress(
                    active=False,
                    generated_tokens=final_tokens,
                    tokens_per_second=exact_rate if exact_rate is not None else final_tokens / elapsed,
                )
                return content
        except (OSError, URLError, json.JSONDecodeError) as exc:
            self._set_progress(active=False)
            raise RuntimeError(f"GGUF generation failed: {exc}") from exc

    def stop(self) -> None:
        process, self.process = self.process, None
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
            return
        if os.name != "nt" or not self._healthy():
            return
        pid = self._listening_pid()
        executable = self._pid_executable(pid) if pid else None
        if executable and executable.resolve() == self.binary.resolve():
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
