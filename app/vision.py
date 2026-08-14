"""Verified local vision-caption model files and runtime helpers."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from huggingface_hub import snapshot_download
from opencc import OpenCC

from .gguf_runtime import GgufRuntime


_SIMPLIFIED_TO_TRADITIONAL = OpenCC("s2twp")


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

VISION_MODELS = {
    "fast": VISION_MODEL,
    "accurate": VisionModelSpec(
        label="Qwen3-VL-8B Abliterated Caption-it",
        repo="mradermacher/Qwen3-VL-8B-Abliterated-Caption-it-GGUF",
        model_filename="Qwen3-VL-8B-Abliterated-Caption-it.Q4_K_M.gguf",
        model_size=5_027_785_888,
        model_sha256="3ffdeb8d9765fb9d415df7b134a713a930b5144fad0fe6370054fa7cc4bdd588",
        mmproj_filename="Qwen3-VL-8B-Abliterated-Caption-it.mmproj-Q8_0.gguf",
        mmproj_size=752_290_336,
        mmproj_sha256="c0e36e3ffa229f67f95a662c7c680c07bcfb58f6b95854b22ef04d9f1f0e36cc",
    ),
}


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


def _matches_requested_caption_language(text: str, language: str) -> bool:
    if language == "en":
        return not re.search(r"[\u3400-\u9fff]", text)
    return len(re.findall(r"[\u3400-\u9fff]", text)) >= 2


def _convert_output_language(value, language: str):
    if language != "zh-TW":
        return value
    if isinstance(value, str):
        return _SIMPLIFIED_TO_TRADITIONAL.convert(value)
    if isinstance(value, list):
        return [_convert_output_language(item, language) for item in value]
    if isinstance(value, dict):
        return {key: _convert_output_language(item, language) for key, item in value.items()}
    return value


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
        language_rule = {
            "en": "Output only English.",
            "zh-CN": "只用简体中文回答，禁止使用英文。",
            "zh-TW": "只用繁體中文回答，禁止使用英文。",
        }[language]
        user_instruction = f"""Describe the image as one detailed, cohesive visual-generation prompt in {language_name}. {language_rule} Include all clearly visible subjects, objects, positions, poses, expressions, clothing, environment, lighting, composition, and camera viewpoint. Describe sensitive or explicit visible content neutrally without refusing. Do not invent events outside the image, hidden details, dialogue, sound, or camera changes. State each visible fact only once and stop immediately when the paragraph is complete. Do not use headings or bullet points."""
        if focus:
            user_instruction += f" Pay particular attention to this user request: {focus}"
        result = self._runtime.generate_with_image(
            image_data_url,
            user_instruction,
            f"You are a precise image captioning assistant. {language_rule}",
            max_new_tokens=384,
        )
        if not result:
            raise RuntimeError("The vision model returned an empty description.")
        if not _matches_requested_caption_language(result, language):
            result = self._runtime.generate_with_image(
                image_data_url,
                user_instruction + f" Your previous answer used the wrong language. {language_rule} Repeat the complete description now.",
                f"You are a precise image captioning assistant. {language_rule}",
                max_new_tokens=384,
            )
            if not result:
                raise RuntimeError("The vision model returned an empty description.")
        return _convert_output_language(_deduplicate_caption(result), language)

    def storyboard(self, image_data_url: str, *, task_type: str, goal: str, language: str,
                   panel_boxes: list[dict] | None = None) -> dict:
        validate_image_data_url(image_data_url)
        language_name = {
            "en": "English",
            "zh-CN": "Simplified Chinese",
            "zh-TW": "Traditional Chinese",
        }.get(language)
        if not language_name:
            raise ValueError("Unsupported output language.")
        if task_type not in {"comic_panels", "viral_video"}:
            raise ValueError("Unsupported storyboard task type.")
        boxes = panel_boxes or []
        if len(boxes) > 40:
            raise ValueError("No more than 40 panel candidates are supported.")
        box_lines = []
        for index, box in enumerate(boxes, 1):
            try:
                values = [max(0.0, min(1.0, float(box[key]))) for key in ("x", "y", "width", "height")]
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("Panel candidates must use normalized x, y, width, and height values.") from exc
            box_lines.append(f"{index}: x={values[0]:.4f}, y={values[1]:.4f}, w={values[2]:.4f}, h={values[3]:.4f}")
        panel_context = "\n".join(box_lines) if box_lines else "No reliable panel candidates were detected; infer panels from visible gutters and layout."
        panel_example = "1" if boxes else "null"
        task_rule = (
            "Treat each visible comic panel as source evidence. Preserve reading order, visible identities, actions, dialogue, and scene continuity. Do not invent unseen panels or events."
            if task_type == "comic_panels" else
            "Use the source image as the visual identity and opening-state anchor. Create an engaging short-form video storyboard while keeping visible identity-defining facts consistent."
        )
        language_rule = {
            "en": "Output only English.",
            "zh-CN": "只用简体中文回答，禁止使用英文。",
            "zh-TW": "只用繁體中文回答，禁止使用英文。",
        }[language]
        analysis_instruction = f"""Analyze the visible image accurately in {language_name}. {language_rule}
Identify visible people, objects, text, spatial relationships, actions, and composition. If the image contains comic panels or distinct regions, enumerate them in reading order. Do not create events beyond the image. This analysis will be used to write a storyboard."""
        visual_analysis = self._runtime.generate_with_image(
            image_data_url,
            analysis_instruction,
            f"You are a precise visual analyst. State concrete image facts only. {language_rule}",
            max_new_tokens=650,
            temperature=0.1,
            top_p=0.8,
            repeat_penalty=1.15,
        )
        if not visual_analysis:
            raise RuntimeError("The storyboard model returned an empty visual analysis.")
        instruction = f"""Based only on the visual analysis below, create a production-ready storyboard in {language_name}. {language_rule} {task_rule}
User goal: {goal.strip() or 'Create a clear visual story with strong continuity.'}
Panel candidates (normalized coordinates, proposals rather than ground truth):
{panel_context}

Visual analysis:
{visual_analysis}

Return one JSON object only with this exact shape:
{{"title":"specific title","synopsis":"specific synopsis","characters":["specific character"],"shots":[{{"panel_index":{panel_example},"duration_seconds":2.5,"shot_size":"specific shot size","camera_movement":"specific movement","visual_action":"specific action","dialogue":"","sound":"specific sound","transition":"specific transition"}}],"sound_design":"specific overall audio plan","viral_hook":"specific hook","ending":"specific ending"}}
Populate every field with concrete content supported by the visual analysis and task rule; dialogue alone may be empty. Use 1 to 20 shots, each with one clear visual beat. Durations must be realistic values from 0.5 to 15 seconds. Do not output start times because they are calculated locally. Do not include Markdown."""
        raw = self._runtime.generate(
            instruction,
            "You are a precise storyboard writer. Fill every requested JSON field with concrete production content.",
            max_new_tokens=1800,
            temperature=0.25 if task_type == "comic_panels" else 0.55,
            top_p=0.85,
            stop_on_json=True,
        )
        try:
            normalized = _normalize_storyboard(raw, max_panel_index=len(boxes))
        except RuntimeError as exc:
            if "invalid structured data" not in str(exc):
                raise
            repaired = self._runtime.generate(
                "Repair the JSON syntax below without adding, deleting, translating, or rewriting content. Preserve every field and array item. Return one valid JSON object only.\n\nBROKEN JSON:\n" + raw,
                "You are a JSON syntax repair tool. Preserve content exactly and return valid JSON only.",
                max_new_tokens=1800,
                temperature=0.01,
                top_p=0.1,
                stop_on_json=True,
            )
            normalized = _normalize_storyboard(repaired, max_panel_index=len(boxes))
        return _convert_output_language(normalized, language)

    def stop(self) -> bool:
        released = self._runtime.process is not None or self._runtime.loaded
        self._runtime.stop()
        return released


def _normalize_storyboard(raw: str, *, max_panel_index: int | None = None) -> dict:
    text = str(raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    try:
        data, _ = json.JSONDecoder().raw_decode(text[text.find("{"):])
    except (ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError("The storyboard model returned invalid structured data.") from exc
    if not isinstance(data, dict) or not isinstance(data.get("shots"), list) or not data["shots"]:
        raise RuntimeError("The storyboard model returned no usable shots.")
    if len(data["shots"]) > 20:
        raise RuntimeError("The storyboard model returned more than 20 shots.")
    normalized_shots = []
    start = 0.0
    for index, shot in enumerate(data["shots"], 1):
        if not isinstance(shot, dict):
            raise RuntimeError("The storyboard model returned an invalid shot.")
        try:
            duration = round(max(0.5, min(15.0, float(shot.get("duration_seconds", 3.0)))) * 2) / 2
        except (TypeError, ValueError):
            duration = 3.0
        panel_index = shot.get("panel_index")
        if panel_index is not None:
            try:
                panel_index = max(1, int(panel_index))
            except (TypeError, ValueError):
                panel_index = None
        if panel_index is not None and (not max_panel_index or panel_index > max_panel_index):
            panel_index = None
        normalized_shots.append({
            "number": index,
            "start_seconds": round(start, 1),
            "duration_seconds": duration,
            "panel_index": panel_index,
            "shot_size": str(shot.get("shot_size") or "Medium shot").strip(),
            "camera_movement": str(shot.get("camera_movement") or "Static").strip(),
            "visual_action": str(shot.get("visual_action") or "").strip(),
            "dialogue": str(shot.get("dialogue") or "").strip(),
            "sound": str(shot.get("sound") or "").strip(),
            "transition": str(shot.get("transition") or "Cut").strip(),
        })
        start += duration
    title = str(data.get("title") or "").strip()
    synopsis = str(data.get("synopsis") or "").strip()
    sound_design = str(data.get("sound_design") or "").strip()
    if not title or not synopsis or not sound_design or not any(shot["visual_action"] for shot in normalized_shots):
        raise RuntimeError("The storyboard model returned incomplete structured data.")

    def character_text(item) -> str:
        if isinstance(item, dict):
            name = str(item.get("name") or "").strip()
            description = str(item.get("description") or "").strip()
            return " - ".join(part for part in (name, description) if part)
        return str(item).strip()

    return {
        "title": title,
        "synopsis": synopsis,
        "characters": [text for item in data.get("characters", []) if (text := character_text(item))],
        "shots": normalized_shots,
        "sound_design": sound_design,
        "viral_hook": str(data.get("viral_hook") or "").strip(),
        "ending": str(data.get("ending") or "").strip(),
        "total_duration_seconds": round(start, 1),
    }
