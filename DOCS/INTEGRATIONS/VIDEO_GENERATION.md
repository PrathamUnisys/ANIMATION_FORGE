---
prompt_id: INTEGRATION_VIDEO_GENERATION
version: 1.0.0
modified_date: 2026-11-09
description: Guidance for evaluating generative video tools and workflows.
dependencies: ["INTEGRATION_COMFYUI", "TOOL_INTEL_HARDWARE", "TOOL_INTEL_LICENSING"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial video generation guidance
---
# Video Generation

## Status
ComfyUI adapter metadata lists example image-to-video capability and a Wan model entry, but the inspected adapter does not submit a graph to ComfyUI or run a video model. Treat video generation as **planned/unverified at application integration level**, not an implemented live generator (`backend/integrations/comfyui_adapter.py`).

## Evaluation and test
Define duration, resolution, frame rate, aspect ratio, input conditioning, temporal consistency, audio requirements, and acceptable defects. Verify exact model/version, license, workflow nodes, required custom extensions, disk/VRAM, runtime and current source documentation. Distinguish official vendor integration from community workflow/nodes and experimental features.

Before any download, paid service call, or remote transfer, obtain explicit human approval for version, data, and cost cap. Test a minimal approved clip on the target host; measure actual runtime/resource use and validate container, frame rate, duration, playback, and output integrity. Preserve workflow/configuration and hashes, but do not claim a test without a generated artifact and logs.

A human reviews motion, identity, artifacts, rights, and story fit. Technical validation does not approve the final creative deliverable.
