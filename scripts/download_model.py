from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.model_files import MODEL_FILE, download_model, verify_model_file


def main() -> None:
    destination = ROOT / "models" / "qwen35-9b-abliterated-v2"
    print(f"Downloading model to: {destination}", flush=True)
    download_model(destination)
    print(f"Verifying {MODEL_FILE}...", flush=True)
    verify_model_file(destination / MODEL_FILE)
    print("Model download and SHA256 verification completed.", flush=True)


if __name__ == "__main__":
    main()
