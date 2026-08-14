# liuliu Faithful H3

`liuliu Faithful H3` is a standalone local Web tool for faithful `FL2VA` and `Ref2VA` prompt formatting, controlled prompt enrichment, and module-based H3 editing.

## Features

- Faithful FL2VA and Ref2VA text conversion, isolated from optional image analysis
- Independent image-to-prompt reconstruction with local preview, factual captioning, copy, and one-click transfer to the source prompt
- Prompt enrichment with an independent creative-strength control
- Enrichment preserves the original prompt as an unchanged prefix; strength 0 is conservative and higher levels append bounded creative detail without altering the faithful-conversion workflow
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

## What's new in v1.4.0 (2026-08-14)

- Added a separate image-to-prompt module powered by the uncensored `Qwen2-VL-2B-Abliterated-Caption-it` vision model.
- Added local PNG, JPEG, and WebP selection with a stable preview, optional focus instruction, same-language output, copy, and one-click transfer to the source prompt.
- Added on-demand download and SHA256 verification for a `Q4_K_S` model plus `Q8_0` vision projector, totaling about 1.65 GB.
- Text and vision runtimes now release each other before inference so the optional vision model cannot silently compete with the 4B or 9B text model for VRAM.
- The existing release-memory action now unloads either runtime.
- A real NVIDIA CUDA test described a 496 KB reference image in Simplified Chinese in `7.641s`, including cold model startup.

## What's new in v1.3.9 (2026-08-14)

- Prompt enrichment now protects Chinese reference metadata written with either `图` or `图片`, including identity assignments and the explicit starting-scene reference.

## v1.3.8 (2026-08-14)

- Restored the previous model-driven prompt-enrichment behavior after feedback that the fixed high-strength scene restrictions were too rigid.
- The rollback affects prompt enrichment only; faithful conversion, Ref2VA timeline handling, model selection, and local runtime behavior are unchanged.

## v1.3.7 (2026-08-14)

- Prompt enrichment now produces one cohesive prompt and automatically removes disconnected source-plus-afterword output or unsupported new plot elements.
- Explicit Chinese picture identities and starting-reference facts remain protected during prompt enrichment.
- Ref2VA faithful conversion now turns explicit close-ups and cuts into timestamped H3 timeline shots rather than one translated paragraph.
- Ref2VA starts from the implicit `00:00.000` first shot and estimates later cut times from the number and type of explicit actions instead of using fixed three-second slots.
- Preserve explicit picture identities, the starting reference, and retention fields without creating new visual details.
- Keep Ref2VA timeline structure in the local Chinese-preview fallback when model output is unreadable.
- v1.3.5 recovers from stale browser state and refreshes the application script after updates.
- Preserve explicit Chinese picture identities and starting-reference facts in Ref2VA output.
- Remove unsupported vocalizations from faithful H3 conversion through an additional correction gate.
- Convert an original prompt directly to faithful H3 without first importing it into modules.
- Remove any individual shot and drag shots into a new order; timestamps update automatically.
- Recover common malformed module JSON and retry one strict no-invention correction before showing a failure.
- Support an optional local startup configuration for reusing an existing GGUF model and runtime.
- Prevent corrupt Chinese GGUF previews from being displayed as question marks; Chinese source prompts fall back to the original source text in the matching H3 template.
- Reject unreadable previews for non-Chinese source prompts instead of returning corrupted text.
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

To reuse a model or runtime already stored elsewhere, copy `local-settings.example.bat` to `local-settings.bat` and set the applicable local paths. This file is ignored by Git and stays on the local machine.

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
- Optional vision model: <https://huggingface.co/mradermacher/Qwen2-VL-2B-Abliterated-Caption-it-GGUF>

The optional vision module downloads `Q4_K_S` plus the `Q8_0` multimodal projector on demand. It needs about 1.65 GB of additional disk space and uses an isolated 8192-token context. Images remain local and are sent only to the local `llama.cpp` process.

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

Version `1.3.7`<br>
Copyright `@liuliu`<br>
Contact: `1661204908@qq.com`
