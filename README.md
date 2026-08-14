# liuliu Faithful H3

`liuliu Faithful H3` is a standalone local Web tool with separate H3 conversion, prompt-enrichment, and image-to-prompt workspaces.

## Features

- Faithful FL2VA and Ref2VA text conversion on the default H3 page
- Independent image-to-prompt page with accelerated local preview, factual captioning, and one-click copy
- Top-level prompt-enrichment page with an independent creative-strength control
- Enrichment preserves the original prompt as an unchanged prefix; strength 0 is conservative and higher levels append bounded creative detail without altering the faithful-conversion workflow
- Direct conversion from the original prompt, with an optional arrow to move enriched text into the source field
- Literal English visual translation with a fail-closed no-invention review
- Separate audio inference that cannot modify visual descriptions
- English default interface with Simplified Chinese and Traditional Chinese
- Contextual `?` help for the model, mode, and every editing workflow
- Selectable Qwen3.5 4B and 9B local models
- Official `llama.cpp` GGUF runtime with automatic startup and model residency
- Live elapsed time and `token/s`, plus the final backend and measured request duration
- One-click release of this tool's loaded model, Python memory, and CUDA cache
- No API key, cloud inference, or host application required

> [!IMPORTANT]
> Image to prompt uses a compact 2B vision model to keep local deployment lightweight. Its recognition ability is limited: it may miss small details, confuse subject relationships, or simplify complex scenes. Treat its output as a draft reference, verify it against the source image, and revise it before using it for generation.

## What's new in v1.5.5 (2026-08-14)

- Added a full-width live resource strip above the existing header for CPU, RAM, SSD read/write throughput, GPU utilization, and VRAM usage.
- Resource sampling runs in a lightweight backend cache and refreshes in the browser every two seconds without shifting the existing workspaces.
- Unnumbered explicit time cues such as `2秒`, `3秒时`, and `At the 5.5-second mark` now create separate shots with standard H3 timestamps such as `At 00:02.000`.
- Explicit source timing retains millisecond precision, while prompts without timing continue to use natural semantic duration inference.
- Clarified that the optional compact vision model is intended for reference-assisted drafting rather than authoritative image understanding.

## What's new in v1.5.4 (2026-08-14)

- Closing the Windows launcher now terminates the complete local server process tree instead of leaving the port occupied.
- The shared model status now refreshes after every completed or failed request and no longer remains on `Loading model...`.

## What's new in v1.5.3 (2026-08-14)

- Every FL2VA and Ref2VA shot now carries an explicit timeline timestamp, beginning at `00:00.000`.
- Numbered shots and explicit source timing are preserved first; prompts without timing use semantic action-duration inference.

## What's new in v1.5.2 (2026-08-14)

- The Image to prompt input and output headings now share the same grid row, aligning both titles and content top edges.
- Stylesheets now use versioned URLs so an update cannot leave the previous layout in the browser cache.

## What's new in v1.5.1 (2026-08-14)

- Release memory now reports released and current/total VRAM and RAM in a localized Toast.
- First use and post-release model starts show an explicit loading state before elapsed time and `token/s` generation progress.
- Text and vision model readiness share the top status area, and paired input/output labels are aligned.
- FL2VA conversion no longer adds a picture reference when the source prompt does not contain one; explicit Chinese dialogue remains unchanged inside H3 dialogue tags.

## What's new in v1.5.0 (2026-08-14)

- Navigation is now ordered H3, Prompt enrichment, and Image to prompt, with prompt enrichment promoted to an independent page.
- The top Download models action lets users choose 4B, 9B, and the optional vision pair independently; only checked items download in the background and progress remains visible in the startup console.
- Vision inference enables Flash Attention and uses a bounded 256-512 image-token budget with a 4096-token context.
- Local generation now reports live elapsed time and `token/s` while work is in progress.
- Release memory now also terminates matching inherited local model servers, preventing text and vision models from remaining in VRAM together.
- RTX 4070 Ti verification completed a 141 KB PNG in `15.750s` from a cold start at a final `210.29 token/s`; a repeated cached request completed in `0.313s`.

## What's new in v1.4.0 (2026-08-14)

- Added a separate image-to-prompt page powered by the uncensored `Qwen2-VL-2B-Abliterated-Caption-it` vision model.
- Added top-level H3 and image-to-prompt navigation. H3 remains the default page, while image analysis has its own independent workflow and output.
- Added local PNG, JPEG, and WebP selection with a stable preview, optional focus instruction, same-language output, and one-click copy.
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
- Convert an original prompt directly to faithful H3.
- Remove any individual shot and drag shots into a new order; timestamps update automatically.
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

The top Download models action offers 4B, 9B, and the vision pair as independent choices. The vision pair consists of `Q4_K_S` plus the `Q8_0` multimodal projector, needs about 1.65 GB of additional disk space, and uses an isolated 4096-token context with a bounded 256-512 image-token budget. Images remain local and are sent only to the local `llama.cpp` process.

The optional vision model is deliberately small. It is suitable for quickly drafting visible subjects, positions, and camera cues, but it is not a high-accuracy vision system. Small objects, fine appearance details, spatial relationships, text, and complex multi-subject scenes may be incomplete or incorrect. Always compare the result with the image and use it as editable reference material.

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

Version `1.5.5`<br>
Copyright `@liuliu`<br>
Contact: `1661204908@qq.com`
