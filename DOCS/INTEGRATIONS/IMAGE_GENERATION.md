---
prompt_id: INTEGRATION_IMAGE_GENERATION
version: 1.0.0
modified_date: 2026-11-09
description: Workflow guidance for evaluating image-generation capabilities.
dependencies: ["INTEGRATION_COMFYUI", "TOOL_INTEL_LICENSING", "TOOL_INTEL_POC"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial image generation guidance
---
# Image Generation

## Status
The application's image-generation profile is associated with ComfyUI. The adapter validates supplied graph fields and records supplied output bytes; it does not submit a generation request (`backend/integrations/comfyui_adapter.py`). Other production code draws static Pillow-based sample images, not model outputs (`backend/departments/production_studios.py`). Provider metadata/profile labels are not evidence of an invoked model. Use `INTEGRATIONS/COMFYUI.md` for current adapter limits.

## Workflow
Specify deliverable dimensions, format, visual references, consistency criteria, acceptable variation, and review owner before selection. Verify current model/checkpoint license, intended commercial use, source/provenance of inputs, custom-node code, GPU requirements, and actual local inventory. Classify integrations as official, community, or experimental.

If running a workflow, use an approved, versioned graph in draft storage; record exact model and node versions/hashes, prompt, negative prompt, seed, settings, input references, timestamp, output hash, and measured resource use. A seed is a reproducibility aid, not a guarantee of identical outputs. Obtain download/spend approvals first.

A qualified human must review identity, consistency, artifacts, rights, and suitability. Tool QA, metadata, or generated previews do not approve creative assets for release.
