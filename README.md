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
- Automatic IndexedDB drafts, sortable per-workspace queues, and up to 20 restorable history records across H3, prompt enrichment, and image to prompt
- Live CPU, RAM, SSD, GPU, and VRAM monitoring in a separate top resource strip
- No API key, cloud inference, or host application required

> [!IMPORTANT]
> Image to prompt uses a compact 2B vision model to keep local deployment lightweight. Its recognition ability is limited: it may miss small details, confuse subject relationships, or simplify complex scenes. Treat its output as a draft reference, verify it against the source image, and revise it before using it for generation.

## What's new in v1.6.0 - Time to Have Fun Again! (2026-08-14)

- Three independent top-level workspaces now cover H3, prompt enrichment, and image to prompt.
- The optional compact 2B image-to-prompt workflow includes local preview, focus instructions, same-language output, and copy; its limited output is intended as editable reference material.
- Model downloads are selectable and run in the background for Qwen3.5 4B, Qwen3.5 9B, and the optional image-to-prompt model.
- H3, prompt enrichment, and image to prompt now preserve independent drafts in IndexedDB, including selected image data and requirements.
- Every workspace now has its own sortable processing queue and restorable history, with single-item, multi-select, and select-all deletion.
- Queue and history panels show five records at once and scroll internally; successful history is capped at the newest 20 records.
- Live elapsed time, `token/s`, memory-release usage summaries, and the top CPU, RAM, SSD read/write, GPU, and VRAM strip provide continuous runtime feedback.

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

Version `1.6.0`<br>
Copyright `@liuliu`<br>
Contact: `1661204908@qq.com`
