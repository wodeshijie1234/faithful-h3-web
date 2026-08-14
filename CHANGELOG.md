# Changelog

All notable changes to liuliu Faithful H3 are documented here.

## 1.3.2 - 2026-08-14

### Fixed

- Added an optional, Git-ignored `local-settings.bat` startup override so local deployments can reuse an existing GGUF model and runtime without relying on temporary terminal environment variables.

## 1.3.1 - 2026-08-14

### Fixed

- Prevented corrupted GGUF Chinese previews from being shown as literal question marks. When the source prompt is Chinese, the tool now returns the original source text in the matching H3 template so the visual facts remain editable and unchanged.
- Reject unreadable previews for non-Chinese source prompts instead of returning corrupted text.

## 1.3.0 - 2026-08-13

### Added

- Added selectable Qwen3.5 4B and 9B model profiles.
- Added the official `llama.cpp` GGUF backend with automatic server startup, health checks, model residency, clean shutdown, and no-thinking chat requests.
- Added automatic NVIDIA/CUDA detection with a Vulkan compatibility fallback in the one-click installer.
- Added the active model, backend, and measured request duration to operation feedback.

### Changed

- Clean installations now use the lightweight GGUF runtime and no longer install PyTorch, Transformers, Quanto, Triton, or FLA by default.
- The 4B model is recommended below 16 GiB VRAM; the 9B model is recommended at 16 GiB VRAM or above. Users can still download and switch either model from the interface.
- Literal conversion and its visual review now explicitly reject unsupported indoor/outdoor settings, appearance, clothing, lighting, mood, relationships, intentions, and camera details.
- Audio inference remains isolated and may only fill soundscape and music fields from supported actions and dialogue.

### Compatibility

- Existing Quanto installations remain supported as a manual fallback through `requirements-quanto.txt`.
- Failed or unreadable GGUF output is rejected instead of being written into an H3 prompt.

## 1.2.0 - 2026-08-13

### Added

- Added a modular H3 editor for scene continuity, shots, overall soundscape, non-diegetic music, and the additional Ref2VA sections.
- Added semantic import from both the original prompt and enriched result without translation, rewriting, or creative expansion.
- Added dynamic shot counts based on explicit shot numbering or semantic cuts in the imported prompt.
- Added per-shot duration controls from 0.5 to 30 seconds in 0.5-second steps, automatic cumulative cut timestamps, and a live total duration.
- Added default three-shot editing for a blank workspace with compact add and remove controls.

### Changed

- Replaced the separate micro-edit workflow with one shared module editor used before and after H3 conversion.
- Literal visual translation now passes a strict no-invention review before any H3 result is returned.
- Audio inference runs separately and can only fill the soundscape and music fields.
- Reorganized the interface into prompt sources, a modular editing workspace, and a single H3 result area.

## 1.1.3 - 2026-08-13

### Fixed

- Constructed the Quanto model skeleton in BF16 before materializing the BF16 checkpoint scales and non-quantized weights, preventing a Float/BFloat16 mismatch during real inference.

## 1.1.2 - 2026-08-13

### Fixed

- Made the Windows launcher read a configured model directory from the current user environment when it was not inherited by the launcher process, preserving an isolated runtime without embedding machine-specific paths in the project.

## 1.1.1 - 2026-08-13

### Added

- Added a compact down-arrow action that copies the enriched prompt directly into the H3 conversion input, scrolls to it, and focuses the field.
- Added localized labels and empty-output feedback for the transfer action.

### Fixed

- Isolated the launcher from user and system site packages with `PYTHONNOUSERSITE=1`.
- Added a PyTorch and CUDA startup self-check so a broken runtime is reported before the user starts prompt processing.
- Updated `huggingface-hub` to `1.3.7` to satisfy the declared Transformers 5.2 dependency and make clean installation reproducible with current pip.
- Corrected the mobile header layout so the download and memory-release controls remain readable at 390 px width.
- Replaced the remaining legacy brand labels with the public `liuliu` brand across the UI, launchers, API metadata, and license.

## 1.1.0 - 2026-08-13

### Added

- Added a one-click **Release memory** control with English, Simplified Chinese, and Traditional Chinese labels.
- Added a local API that unloads the text model and tokenizer, runs Python garbage collection, and clears the CUDA allocator and IPC caches.
- Added clear status feedback for released and already-free states.

### Safety

- The action only releases resources owned by this tool. It does not stop other applications or clear memory allocated by other processes.
- The release action waits for an active generation request to finish and is disabled in the page while a request is running.

### Deployment

- Added a G-drive deployment that reuses the verified local checkpoint without duplicating the model file.

## 1.0.0 - 2026-08-12

### Added

- Initial standalone release with FL2VA and Ref2VA formatting.
- Prompt enrichment with adjustable creative strength.
- Structure-preserving H3 micro editing.
- English, Simplified Chinese, and Traditional Chinese interfaces.
- One-click Windows setup and verified local model download.
