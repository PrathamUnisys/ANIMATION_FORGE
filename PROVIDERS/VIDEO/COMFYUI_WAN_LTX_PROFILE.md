---
prompt_id: PROVIDER_VIDEO_COMFYUI
version: 1.1.0
modified_date: 2026-11-09
description: ComfyUI video model candidates with explicit implementation and verification requirements.
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial provider profile
  - version: 1.1.0
    date: 2026-11-09
    summary: Distinguished listed candidate from actual generation and corrected status
---
# PROVIDER PROFILE: PROVIDER_VIDEO_COMFYUI

## Capability status
`COMFYUI_LOCAL_GRAPH` provider metadata lists Flux and Wan model identifiers. The ComfyUI adapter has a hard-coded Wan entry and node names but does not connect to ComfyUI or run video inference (`backend/providers/manager.py`, `backend/integrations/comfyui_adapter.py`). LTX-Video and AnimateDiff are profile candidates, not registered model integrations in the inspected manager. Do not claim these workflows are implemented or locally installed.

## Verification before selection
For each exact model/checkpoint and workflow verify the current official source, license/commercial terms, supported resolution/duration/frame rate, required nodes, dependencies, download size, host GPU/VRAM/storage, and known constraints. Mark community workflow nodes and experimental features. Do not transfer still-image metadata to video models or assume equal requirements.

Get human authorization before downloads, network transfer, or paid inference. Run an approved minimal clip on the actual host and capture graph, exact versions/hashes, input, seed/settings, logs, output integrity, measured runtime and memory. Human-review motion, identity, quality, rights, and release suitability.
