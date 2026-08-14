# Changelog

All notable changes to liuliu Faithful H3 are documented here.

## 1.4.0 - 2026-08-14

### Added

- Added an independent image-to-prompt page using `Qwen2-VL-2B-Abliterated-Caption-it` with local image preview, optional focus instructions, localized output, and copy.
- Added on-demand, resumable download and SHA256 verification for the 940,312,704-byte `Q4_K_S` model and 712,895,168-byte `Q8_0` vision projector.
- Added PNG, JPEG, and WebP validation with a 12 MB request limit.
- Added standalone vision download and real-inference self-check scripts.

### Changed

- Text and vision inference now release each other before loading so they do not compete for VRAM.
- Added top-level H3 and image-to-prompt navigation. H3 is the default page, and image analysis no longer shares the H3 editing workflow.
- Removed the redundant H3 module editor and its import/decompose API; H3 conversion now runs directly from the source prompt.
- The release-memory endpoint now stops both runtimes.
- Vision inference uses an isolated 8192-token context with at least 1024 image tokens.

### Verification

- Real CUDA inference on a 496 KB JPEG completed in `7.641s`, including cold model startup, and returned a coherent Simplified Chinese description of the visible subjects, positions, clothing, beach, waves, and warm sky.

## 1.3.9 - 2026-08-14

### Fixed

- Prompt enrichment now preserves reference metadata written as `图片1/图片2`, including explicit identity assignments and phrases such as `视频开始于图片2的场景`, even at creative strength `100`.

## 1.3.8 - 2026-08-14

### Reverted

- Reverted the fixed high-strength scene filters and deterministic scene fallbacks from `1.3.7` after they made prompt enrichment too restrictive.
- Restored the previous model-driven prompt-enrichment workflow. Faithful conversion and Ref2VA timeline behavior are unchanged.

## 1.3.7 - 2026-08-14

### Fixed

- Prompt enrichment now returns one cohesive, same-language prompt with additions integrated beside the source action they support; it no longer appends a disconnected afterword to unchanged source text.
- Added an enrichment review and one repair pass that reject new characters, props, locations, dialogue, plot events, unsupported actions, and unsupported camera cuts before returning an enriched prompt.
- Explicit Chinese picture identities and video starting-reference facts are restored deterministically when an enrichment model omits them.

## 1.3.6 - 2026-08-14

### Fixed

- Ref2VA faithful conversion now turns explicit close-ups, camera cuts, and shot changes into sequential H3 timeline shots with cumulative timestamps instead of placing the whole translation in one paragraph.
- Ref2VA now derives explicit picture identity, starting-reference, and retention fields from the source prompt without adding visual details.
- The readable Chinese-preview fallback preserves the same Ref2VA shot boundaries when an inference backend returns corrupt preview text.
- Ref2VA starts its first shot at `00:00.000` and derives later cut times from explicit action density rather than assigning every shot a fixed three-second duration.

## 1.3.5 - 2026-08-14

### Fixed

- Recovered from stale browser language values instead of allowing a client-side initialization failure.
- Added a versioned application script URL and no-cache page entry response so refreshed deployments consistently load matching UI assets.

## 1.3.4 - 2026-08-14

### Fixed

- Canonicalized Chinese picture references for Ref2VA and preserved explicit picture identity and starting-reference facts in the generated H3 fields.
- Added an additional correction gate for unsupported English vocalizations such as `moans`; these are rejected unless explicitly present in the source.

### Changed

- Prompt enrichment is now independent from faithful conversion: the original prompt is always retained as an unchanged prefix, while strengths 30/50/80/100 append separately generated detail within their own token budgets; strength 0 stays conservative and returns the source unchanged.

## 1.3.3 - 2026-08-14

### Added

- Added direct faithful H3 conversion from the source prompt without requiring module import first.
- Added per-shot removal controls and drag-to-reorder support. Start timestamps are recalculated after every change and the first shot starts at `00:00.000`.

### Fixed

- Recover fenced module JSON, object wrappers, and trailing commas locally; retry one malformed or unterminated model JSON response before reporting a concise recovery failure.
- Retry a failed strict visual review once using a deletion-only correction pass. The no-invention guard remains enforced after the retry.

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
