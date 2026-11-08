---
prompt_id: TOOL_COMFYUI
version: 1.0.0
modified_date: 2026-11-09
description: Operational guide for locating, connecting, running and debugging ComfyUI workflows in Animation Forge
dependencies: ["TOOLS_INDEX", "SCHEMAS/TOOL_PROFILE.schema.json"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Add ComfyUI operational manual with explicit connection and execution verification boundaries
---
# Tool Manual — ComfyUI

## Identity and purpose

ComfyUI is a node-based interface and local server for model workflows such as image generation, image transformation and supported video/audio pipelines.

- **Tool ID:** `COMFYUI`
- **Primary task tags:** `image_generation`, `image_to_image`, `character_consistency`, `background_generation`, `storyboard_images`, `video_generation`
- **Official repository:** https://github.com/Comfy-Org/ComfyUI
- **Server API contract:** https://github.com/Comfy-Org/ComfyUI/blob/master/openapi.yaml
- **Common local UI endpoint:** `http://127.0.0.1:8188` (documented convention, not proof it is running)
- **Local status in this repository:** `NOT_VERIFIED`

## Installation and location

Use the official project installation instructions and choose the environment deliberately. Record the actual ComfyUI root, Python environment, launch script, model directories, custom-node directories and version in local configuration. Do not assume the common `ComfyUI_windows_portable` folder exists.

## Connection and configuration

ComfyUI exposes HTTP and WebSocket interfaces. The exact endpoint contract should be discovered from the OpenAPI specification shipped with the installed version, rather than copied permanently from an old adapter.

The commonly used workflow is:
1. Check a live endpoint and capture version/system information.
2. Query live node definitions and model availability rather than relying on a hardcoded node list.
3. Submit a workflow using the installed server's documented prompt/job endpoint.
4. Track progress and completion using the server's WebSocket and/or job/history endpoints.
5. Retrieve the actual output file(s), then verify file type, dimensions/duration and hashes.
6. Record workflow JSON, model/node versions, prompt, seed and output references.

A basic endpoint check after manually starting ComfyUI:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8188/system_stats" -Method Get
```

The endpoint and route names can evolve. Use the installed version's OpenAPI contract as the authority; do not assume the example endpoint exists in every build.

## How to use

1. Confirm the server is reachable and record its actual installed version.
2. Confirm workflow nodes, checkpoints, VAEs, LoRAs, custom nodes and model licences.
3. Start with a small low-resolution test and a fixed seed.
4. Inspect the output and only then increase resolution, batch size or frame count.
5. Save the workflow JSON next to the generated output and register the real file location and hash in the asset library.

## Debugging

| Symptom | Diagnostic | Likely action |
|---|---|---|
| Connection refused | Check process, endpoint and port | Start ComfyUI or correct configured host/port. |
| Missing node type | Query live node information and server logs | Install/update the compatible custom node, then restart. |
| Missing checkpoint/model | Inspect model search paths and filenames | Place the model in the configured directory and refresh/restart as required. |
| Out of VRAM | Inspect GPU memory, resolution, batch and model precision | Reduce workload or choose a compatible model/workflow. |
| Prompt stays queued | Inspect job/history state and console logs | Check worker state, node execution error and dependencies. |
| Output not found | Inspect completed-job output metadata | Retrieve the real output path/file and validate it before indexing. |

## Known limitations

The current Animation Forge `ComfyUIAdapter` validates against a hardcoded node/model list and records caller-supplied output bytes. It does not currently submit a workflow to a live ComfyUI server and retrieve a generated result. Do not label a saved byte payload as ComfyUI generation without actual dispatch evidence.

## Verification record

No current machine endpoint, server version, model inventory or successful generation is recorded by this documentation change.
