# Changelog

All notable changes to liuliu Faithful H3 are documented here.

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
