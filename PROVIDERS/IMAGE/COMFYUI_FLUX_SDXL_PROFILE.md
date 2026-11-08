---
prompt_id: PROVIDER_IMAGE_COMFYUI
version: 1.1.0
modified_date: 2026-11-09
description: ComfyUI image candidate profile; records adapter limits and required local verification.
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial provider profile
  - version: 1.1.0
    date: 2026-11-09
    summary: Clarified adapter limits, candidate models, and review gates
---
# PROVIDER PROFILE: PROVIDER_IMAGE_COMFYUI

## Capability status
`COMFYUI_LOCAL_GRAPH` is registered as provider metadata in `backend/providers/manager.py`; that manager does not execute an image-generation request. `backend/integrations/comfyui_adapter.py` checks supplied graph names against hard-coded node/model lists and records supplied bytes; it does not connect to ComfyUI or generate images.

Flux/SDXL, ControlNet, and IP-Adapter are candidate workflow/model names only. Their presence here is not evidence that the files, nodes, licenses, or live workflow are installed or tested. Confirm exact checkpoint, VAE, auxiliary weights, custom nodes, versions and hashes at the target host.

Other production code draws static Pillow-based sample character/environment images; these are not model-generated assets (`backend/departments/production_studios.py`).

## Required checks
Verify current official model/software licenses and commercial conditions per artifact; separate software, extension, model, input-image and output rights. Test actual resolution, output quality, consistency, VRAM and runtime on the production workstation. Record the graph, model/node versions, prompt, seed, inputs, date, logs and output hash. A seed/reference lock does not guarantee identity.

Get human approval before model/node downloads, paid/network operations or toolchain selection. Keep generations in draft state and obtain human creative approval before use or release. See `DOCS/INTEGRATIONS/IMAGE_GENERATION.md` and `DOCS/INTEGRATIONS/COMFYUI.md`.
