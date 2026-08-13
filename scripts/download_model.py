from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.model_files import MODEL_SPECS, download_gguf


def main() -> None:
    model_id = sys.argv[1].lower() if len(sys.argv) > 1 else "4b"
    if model_id not in MODEL_SPECS:
        raise SystemExit("Model must be 4b or 9b.")
    destination = ROOT / "models"
    print(f"Downloading {model_id.upper()} GGUF to: {destination}", flush=True)
    checkpoint = download_gguf(destination, MODEL_SPECS[model_id])
    print(f"Model download and verification completed: {checkpoint.name}", flush=True)


if __name__ == "__main__":
    main()
