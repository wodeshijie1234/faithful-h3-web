# Changelog

All notable changes to liuliu Faithful H3 are documented here.

## 1.7.0 - 2026-08-15 - Today We Can Have Fun Again!

### Added

- Added a fourth top-level Storyboard workspace with a dedicated source, sortable shot timeline, story inspector, structured JSON output, drafts, queues, and history.
- Added local comic-panel detection with numbered overlays, editable panel assignments, per-shot durations, automatic cumulative start times, and drag-and-drop shot ordering.
- Added comic-panel and viral-video storyboard modes with editable shot size, camera movement, visual action, dialogue, sound, transition, hook, and ending fields.
- Added selectable Fast 2B and Accurate 8B vision models for both image-to-prompt and storyboard generation, with independent on-demand downloads.
- Added English, Simplified Chinese, and Traditional Chinese storyboard output, including local Traditional Chinese normalization.

## 1.6.0 - 2026-08-14 - Time to Have Fun Again!

### Added

- Added three independent top-level workspaces for H3, prompt enrichment, and image to prompt.
- Added an optional compact 2B image-to-prompt workflow with local preview, focus instructions, same-language output, and copy; its limited recognition output is presented as editable reference material.
- Added on-demand model selection and background downloads for Qwen3.5 4B, Qwen3.5 9B, and the optional image-to-prompt model.
- Added independent IndexedDB draft recovery to H3, prompt enrichment, and image to prompt, including image data, image filenames, instructions, settings, and outputs.
- Added per-workspace processing queues with sequential execution, drag-and-drop ordering, retryable failed items, item deletion, and multi-select deletion.
- Added restorable per-workspace history capped at the newest 20 successful results, with five visible rows, internal scrolling, item deletion, and multi-select deletion.
- Added live elapsed time and `token/s`, a memory-release usage summary, and a top resource strip for CPU, RAM, SSD read/write, GPU, and VRAM.

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
