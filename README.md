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
- Selectable Qwen3.5 4B and 9B local models
- Official `llama.cpp` GGUF runtime with automatic startup and model residency
- Active backend and measured request duration shown after each operation
- One-click release of this tool's loaded model, Python memory, and CUDA cache
- No API key, cloud inference, or host application required

## What's new in v1.3.0 (2026-08-13)

- Choose between Qwen3.5 4B and 9B local model profiles.
- Run GGUF models through the official `llama.cpp` backend with automatic startup, health checks, model residency, clean shutdown, and no-thinking requests.
- Automatically select an NVIDIA CUDA runtime when supported, with Vulkan as a compatibility fallback.
- See the active model, backend, and measured request duration after each operation.
- Install a lightweight GGUF runtime without PyTorch, Transformers, Quanto, Triton, or FLA dependencies by default.
- Use the recommended 4B model below 16 GiB VRAM or the 9B model at 16 GiB VRAM and above, while retaining manual model selection.
- Reject invented visual details during literal conversion, including unsupported settings, appearance, clothing, lighting, mood, relationships, intentions, and camera details.
- Keep inferred audio isolated to the soundscape and music fields.
- Continue using an existing Quanto installation through the optional `requirements-quanto.txt` compatibility path.
- Reject failed or unreadable GGUF output instead of writing it into an H3 prompt.

Full version history remains available in [CHANGELOG.md](CHANGELOG.md).

## One-click Windows setup

1. Install 64-bit Python 3.10 or 3.11 and the current graphics driver.
2. Keep at least 12 GiB of free disk space for the runtime, download cache, and models.
3. Double-click `install-and-run.bat`.
4. The script creates `.venv`, detects the GPU, installs the official CUDA or Vulkan `llama.cpp` runtime, recommends 4B or 9B from available VRAM, downloads that model with resume support, verifies it, and opens `http://127.0.0.1:7868/`.

For later launches, double-click `run.bat`.

## System requirements

- Windows 10 or Windows 11, 64-bit
- Python 3.10 or 3.11
- NVIDIA GPU recommended; Vulkan is used as a compatibility fallback when CUDA is unavailable
- 4B recommended below 16 GiB VRAM; 9B recommended at 16 GiB or above
- At least 12 GiB free disk space during installation
- Internet access for the first installation and model download

Both models remain selectable in the interface. The 4B profile prioritizes lower memory use; the 9B profile prioritizes translation and instruction quality. Request time depends on prompt length, output length, and GPU.

## Models and runtime

The default runtime is the official Windows build of `llama.cpp` release `b10375`. The installer downloads only the model selected for the current machine. The other model can be downloaded later from the interface.

- 4B model: <https://huggingface.co/byliuliu/faithful-h3-qwen3.5-4b-abliterated>
- 9B model: <https://huggingface.co/byliuliu/faithful-h3-qwen3.5-9b-abliterated-v2>

Existing Quanto checkpoints remain an optional compatibility path. Install `requirements-quanto.txt` only when that fallback is specifically required.

## Manual development setup

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts\install_runtime.py --runtime-dir runtime
.venv\Scripts\python.exe scripts\download_model.py 4b
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

Version `1.3.0`<br>
Copyright `@liuliu`<br>
Contact: `1661204908@qq.com`
