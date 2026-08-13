# Changelog

All notable changes to liuliu Faithful H3 are documented here.

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
