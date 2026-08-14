"""Verified local vision-caption model files and runtime helpers."""

from __future__ import annotations

import base64
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from huggingface_hub import snapshot_download

from .gguf_runtime import GgufRuntime


@dataclass(frozen=True)
class VisionModelSpec:
    label: str
    repo: str
    model_filename: str
    model_size: int
    model_sha256: str
    mmproj_filename: str
    mmproj_size: int
    mmproj_sha256: str


VISION_MODEL = VisionModelSpec(
    label="Qwen2-VL-2B Abliterated Caption-it",
    repo="mradermacher/Qwen2-VL-2B-Abliterated-Caption-it-GGUF",
    model_filename="Qwen2-VL-2B-Abliterated-Caption-it.Q4_K_S.gguf",
    model_size=940_312_704,
    model_sha256="1fffe7ef7b2f44c6323e158aa10348991b15fd47d9b3982a9910bf75e616842f",
    mmproj_filename="Qwen2-VL-2B-Abliterated-Caption-it.mmproj-Q8_0.gguf",
    mmproj_size=712_895_168,
    mmproj_sha256="21356973f9f9d8ba131d83b21e2798df5b1bbcd125761a68ae8e14b5f41f4062",
)


def _verify_file(path: Path, expected_size: int, expected_sha256: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"Vision model file was not found: {path.name}")
    actual_size = path.stat().st_size
    if actual_size != expected_size:
        raise RuntimeError(
            f"Vision model file has the wrong size: {path.name}; "
            f"expected {expected_size}, got {actual_size}."
        )
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != expected_sha256:
        raise RuntimeError(f"Vision model SHA256 mismatch: {path.name}")


def vision_paths(model_root: Path, spec: VisionModelSpec = VISION_MODEL) -> tuple[Path, Path]:
    root = Path(model_root)
    return root / spec.model_filename, root / spec.mmproj_filename


def vision_ready(model_root: Path, spec: VisionModelSpec = VISION_MODEL) -> bool:
    return all(path.is_file() for path in vision_paths(model_root, spec))


def verify_vision_model(model_root: Path, spec: VisionModelSpec = VISION_MODEL) -> tuple[Path, Path]:
    model_path, mmproj_path = vision_paths(model_root, spec)
    _verify_file(model_path, spec.model_size, spec.model_sha256)
    _verify_file(mmproj_path, spec.mmproj_size, spec.mmproj_sha256)
    return model_path, mmproj_path


def download_vision_model(model_root: Path, spec: VisionModelSpec = VISION_MODEL) -> tuple[Path, Path]:
    root = Path(model_root)
    root.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=spec.repo,
        local_dir=root,
        allow_patterns=(spec.model_filename, spec.mmproj_filename),
    )
    return verify_vision_model(root, spec)


_DATA_URL = re.compile(r"^data:(image/(?:png|jpeg|webp));base64,([A-Za-z0-9+/=\r\n]+)$")
_MAX_IMAGE_BYTES = 12 * 1024 * 1024
_IMAGE_SIGNATURES = {
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/webp": (b"RIFF",),
}


def _deduplicate_caption(text: str) -> str:
    segments = re.findall(r"[^。！？!?]+[。！？!?]+|[^。！？!?]+$", text.strip())
    kept: list[str] = []
    seen: list[str] = []
    for segment in segments:
        clean = segment.strip()
        if not clean:
            continue
        key = re.sub(r"\s+", "", clean).rstrip("。！？!?").casefold()
        if not key or key in seen:
            continue
        is_truncated = clean[-1] not in "。！？!?"
        if is_truncated and len(key) >= 4 and any(previous.startswith(key) for previous in seen):
            continue
        kept.append(clean)
        seen.append(key)
    return "".join(kept).strip()


def validate_image_data_url(image_data_url: str) -> None:
    match = _DATA_URL.fullmatch(image_data_url.strip())
    if not match:
        raise ValueError("Use a PNG, JPEG, or WebP image.")
    mime_type, encoded = match.groups()
    try:
        raw = base64.b64decode(encoded, validate=True)
    except ValueError as exc:
        raise ValueError("The selected image is not valid base64 data.") from exc
    if not raw or len(raw) > _MAX_IMAGE_BYTES:
        raise ValueError("The image must be between 1 byte and 12 MB.")
    signatures = _IMAGE_SIGNATURES[mime_type]
    if not any(raw.startswith(signature) for signature in signatures):
        raise ValueError("The selected file content does not match its image type.")
    if mime_type == "image/webp" and raw[8:12] != b"WEBP":
        raise ValueError("The selected file content does not match its image type.")


class VisionCaptionRuntime:
    def __init__(self, model_root: Path, *, binary: Path | None = None, port: int = 18766,
                 spec: VisionModelSpec = VISION_MODEL):
        self.model_root = Path(model_root)
        self.spec = spec
        model_path, mmproj_path = vision_paths(self.model_root, spec)
        self._runtime = GgufRuntime(
            model_path,
            binary=binary,
            port=port,
            mmproj_path=mmproj_path,
            context_size=4096,
        )

    @property
    def ready(self) -> bool:
        return vision_ready(self.model_root, self.spec)

    @property
    def loaded(self) -> bool:
        return self._runtime.loaded

    @property
    def progress(self) -> dict:
        return self._runtime.progress

    def caption(self, image_data_url: str, instruction: str, language: str) -> str:
        validate_image_data_url(image_data_url)
        language_name = {
            "en": "English",
            "zh-CN": "Simplified Chinese",
            "zh-TW": "Traditional Chinese",
        }.get(language)
        if not language_name:
            raise ValueError("Unsupported output language.")
        focus = instruction.strip()
        user_instruction = f"""Describe the image as one detailed, cohesive visual-generation prompt in {language_name}. Include all clearly visible subjects, objects, positions, poses, expressions, clothing, environment, lighting, composition, and camera viewpoint. Describe sensitive or explicit visible content neutrally without refusing. Do not invent events outside the image, hidden details, dialogue, sound, or camera changes. State each visible fact only once and stop immediately when the paragraph is complete. Do not use headings or bullet points."""
        if focus:
            user_instruction += f" Pay particular attention to this user request: {focus}"
        result = self._runtime.generate_with_image(
            image_data_url,
            user_instruction,
            "",
            max_new_tokens=384,
        )
        if not result:
            raise RuntimeError("The vision model returned an empty description.")
        return _deduplicate_caption(result)

    def stop(self) -> bool:
        released = self._runtime.process is not None or self._runtime.loaded
        self._runtime.stop()
        return released
