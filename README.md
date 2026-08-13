# liuliu Faithful H3

`liuliu Faithful H3` is a standalone local Web tool for faithful `FL2VA` and `Ref2VA` prompt formatting, controlled prompt enrichment, and module-based H3 editing.

## Features

- Faithful FL2VA and Ref2VA conversion without image recognition
- Prompt enrichment with an independent creative-strength control
- Semantic import from either an original prompt or an enriched result into editable H3 modules
- Dynamic shot count based on explicit numbering or semantic cuts in the imported prompt
- Per-shot duration controls with 0.5-second steps, automatic cut timestamps, and a live total duration
- One shared module editor before and after conversion, so users can adjust individual fields and regenerate H3
- Literal English visual translation with a fail-closed no-invention review
- Separate audio inference that cannot modify visual modules
- English default interface with Simplified Chinese and Traditional Chinese
- Contextual `?` help for the model, mode, and every editing workflow
- Local inference with Qwen3.5 9B Abliterated v2
- One-click release of this tool's loaded model, Python memory, and CUDA cache
- No API key, cloud inference, or host application required

See [CHANGELOG.md](CHANGELOG.md) for release notes.

## One-click Windows setup

1. Install the current NVIDIA driver and 64-bit Python 3.10 or 3.11.
2. Keep at least 25 GiB of free disk space for the isolated environment, packages, download cache, and model.
3. Double-click `install-and-run.bat`.
4. The script creates `.venv`, installs CUDA PyTorch and the application, downloads the model with resume support, verifies its official v2 SHA256, and opens `http://127.0.0.1:7868/`.

For later launches, double-click `run.bat`.

## System requirements

- Windows 10 or Windows 11, 64-bit
- Python 3.10 or 3.11
- NVIDIA GPU with CUDA support
- Approximately 12 GiB VRAM recommended for this 9B INT8 runtime
- At least 25 GiB free disk space during installation
- Internet access for the first installation and model download

The application has been designed for a 12 GiB NVIDIA GPU, but actual peak VRAM can vary with the installed PyTorch/Quanto versions and generation length.

## Model

The expected checkpoint is:

`Qwen3.5-9B-Abliterated_v2_quanto_bf16_int8.safetensors`

- Size: `8,957,488,932` bytes
- SHA256: `eb03df5ccba4536eb64cf096c08b068eb84cfd2d2aa798cd45f31a0f67e339e6`
- Download source: <https://huggingface.co/byliuliu/faithful-h3-qwen3.5-9b-abliterated-v2>

The downloader uses this repository exclusively and never substitutes the older checkpoint with a renamed file.

## Manual development setup

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade torch --index-url https://download.pytorch.org/whl/cu128
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts\download_model.py
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 7868
```

Run the tests with:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Privacy

Prompts and generated text remain on the local computer. The application only contacts Hugging Face when model files are downloaded. It does not include analytics or telemetry.

## Model and license notice

The source code in this repository is licensed under the MIT License. The model is a separate third-party artifact. Its inclusion in, or download through, this project does not transfer ownership or grant additional rights. Review the Qwen and applicable base-model license terms before redistribution or commercial use. This project does not claim authorship of the model.

Version `1.2.0`<br>
Copyright `@liuliu`<br>
Contact: `1661204908@qq.com`
