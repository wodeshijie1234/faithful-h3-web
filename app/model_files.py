import hashlib
from pathlib import Path

from huggingface_hub import snapshot_download


MODEL_REPO = "byliuliu/faithful-h3-qwen3.5-9b-abliterated-v2"
MODEL_FILE = "Qwen3.5-9B-Abliterated_v2_quanto_bf16_int8.safetensors"
MODEL_SIZE = 8_957_488_932
MODEL_SHA256 = "eb03df5ccba4536eb64cf096c08b068eb84cfd2d2aa798cd45f31a0f67e339e6"
REQUIRED_FILES = [MODEL_FILE, "config.json", "tokenizer.json", "tokenizer_config.json", "chat_template.jinja", "vocab.json"]


def missing_files(model_dir: Path) -> list[str]:
    missing = [name for name in REQUIRED_FILES if not (model_dir / name).is_file()]
    checkpoint = model_dir / MODEL_FILE
    if checkpoint.is_file() and checkpoint.stat().st_size != MODEL_SIZE:
        missing.append(f"{MODEL_FILE} (invalid size)")
    return missing


def verify_model_file(checkpoint: Path) -> None:
    checkpoint = Path(checkpoint)
    actual_size = checkpoint.stat().st_size
    if actual_size != MODEL_SIZE:
        raise RuntimeError(f"Model file has the wrong size: expected {MODEL_SIZE}, got {actual_size}.")
    digest = hashlib.sha256()
    with checkpoint.open("rb") as handle:
        for chunk in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    actual_hash = digest.hexdigest()
    if actual_hash != MODEL_SHA256:
        raise RuntimeError(f"Model SHA256 mismatch: expected {MODEL_SHA256}, got {actual_hash}.")


def download_model(model_dir: Path, repo_id: str = MODEL_REPO) -> Path:
    model_dir.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=repo_id, local_dir=model_dir, allow_patterns=REQUIRED_FILES)
    missing = missing_files(model_dir)
    if missing:
        raise RuntimeError(f"Model download incomplete: {', '.join(missing)}")
    verify_model_file(model_dir / MODEL_FILE)
    return model_dir
