import hashlib
from dataclasses import dataclass
from pathlib import Path

from huggingface_hub import snapshot_download


@dataclass(frozen=True)
class ModelSpec:
    id: str
    label: str
    repo: str
    filename: str
    directory: str
    size: int
    sha256: str
    ssm_a_is_log: bool
    required_files: tuple[str, ...]
    gguf_filename: str = ""
    gguf_size: int = 0
    gguf_sha256: str = ""
    gguf_repo: str = ""


_SHARED_FILES = ("config.json", "tokenizer.json", "tokenizer_config.json", "chat_template.jinja", "vocab.json")
MODEL_SPECS = {
    "4b": ModelSpec(
        id="4b",
        label="Qwen3.5 4B Abliterated",
        repo="byliuliu/faithful-h3-qwen3.5-4b-abliterated",
        filename="Qwen3.5-4B-Abliterated_quanto_bf16_int8.safetensors",
        directory="qwen35-4b-abliterated",
        size=4_844_829_456,
        sha256="3563d71540c755b3004dd4d514a2478c96d5f5e7ff29b4162a391b2d79a0071a",
        ssm_a_is_log=False,
        required_files=("Qwen3.5-4B-Abliterated_quanto_bf16_int8.safetensors", *_SHARED_FILES, "generation_config.json", "merges.txt"),
        gguf_filename="Qwen3.5-4B-Abliterated-Q4_K_M.gguf",
        gguf_size=2_707_513_696,
        gguf_sha256="143686101ab8e540a8a255fa40a4cb9e1bb490f212c75ad220d7600c095b9177",
        gguf_repo="byliuliu/faithful-h3-qwen3.5-4b-abliterated",
    ),
    "9b": ModelSpec(
        id="9b",
        label="Qwen3.5 9B Abliterated v2",
        repo="byliuliu/faithful-h3-qwen3.5-9b-abliterated-v2",
        filename="Qwen3.5-9B-Abliterated_v2_quanto_bf16_int8.safetensors",
        directory="qwen35-9b-abliterated-v2",
        size=8_957_488_932,
        sha256="eb03df5ccba4536eb64cf096c08b068eb84cfd2d2aa798cd45f31a0f67e339e6",
        ssm_a_is_log=True,
        required_files=("Qwen3.5-9B-Abliterated_v2_quanto_bf16_int8.safetensors", *_SHARED_FILES),
        gguf_filename="Qwen3.5-9B-Abliterated-text-Q4_K_M_bis.gguf",
        gguf_size=5_627_044_704,
        gguf_sha256="dba64d0e5cce0739e27535ee0a6b75249eb8006ce8b2d6c060e20750035c4695",
        gguf_repo="byliuliu/faithful-h3-qwen3.5-9b-abliterated-v2",
    ),
}

MODEL_REPO = MODEL_SPECS["9b"].repo
MODEL_FILE = MODEL_SPECS["9b"].filename
MODEL_SIZE = MODEL_SPECS["9b"].size
MODEL_SHA256 = MODEL_SPECS["9b"].sha256
REQUIRED_FILES = list(MODEL_SPECS["9b"].required_files)


def missing_files(model_dir: Path, spec: ModelSpec = MODEL_SPECS["9b"]) -> list[str]:
    missing = [name for name in spec.required_files if not (model_dir / name).is_file()]
    checkpoint = model_dir / spec.filename
    if checkpoint.is_file() and checkpoint.stat().st_size != spec.size:
        missing.append(f"{spec.filename} (invalid size)")
    return missing


def verify_model_file(checkpoint: Path, spec: ModelSpec = MODEL_SPECS["9b"]) -> None:
    checkpoint = Path(checkpoint)
    actual_size = checkpoint.stat().st_size
    if actual_size != spec.size:
        raise RuntimeError(f"Model file has the wrong size: expected {spec.size}, got {actual_size}.")
    digest = hashlib.sha256()
    with checkpoint.open("rb") as handle:
        for chunk in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    actual_hash = digest.hexdigest()
    if actual_hash != spec.sha256:
        raise RuntimeError(f"Model SHA256 mismatch: expected {spec.sha256}, got {actual_hash}.")


def download_model(model_dir: Path, spec: ModelSpec = MODEL_SPECS["9b"], repo_id: str | None = None) -> Path:
    model_dir.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=repo_id or spec.repo, local_dir=model_dir, allow_patterns=spec.required_files)
    missing = missing_files(model_dir, spec)
    if missing:
        raise RuntimeError(f"Model download incomplete: {', '.join(missing)}")
    verify_model_file(model_dir / spec.filename, spec)
    return model_dir


def verify_gguf_file(checkpoint: Path, spec: ModelSpec) -> None:
    checkpoint = Path(checkpoint)
    if spec.gguf_size and checkpoint.stat().st_size != spec.gguf_size:
        raise RuntimeError(f"GGUF has the wrong size: expected {spec.gguf_size}, got {checkpoint.stat().st_size}.")
    if spec.gguf_sha256:
        digest = hashlib.sha256()
        with checkpoint.open("rb") as handle:
            for chunk in iter(lambda: handle.read(16 * 1024 * 1024), b""):
                digest.update(chunk)
        if digest.hexdigest() != spec.gguf_sha256:
            raise RuntimeError("GGUF SHA256 mismatch.")


def download_gguf(model_root: Path, spec: ModelSpec) -> Path:
    model_root.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=spec.gguf_repo, local_dir=model_root, allow_patterns=(spec.gguf_filename,))
    checkpoint = model_root / spec.gguf_filename
    if not checkpoint.is_file():
        raise RuntimeError(f"GGUF download incomplete: {spec.gguf_filename}")
    verify_gguf_file(checkpoint, spec)
    return checkpoint
