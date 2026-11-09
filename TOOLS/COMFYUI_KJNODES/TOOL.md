---
prompt_id: TOOL_COMFYUI_KJNODES
version: 1.0.0
modified_date: 2026-11-09
description: Operational guide for ComfyUI-KJNodes in Animation Forge
dependencies: ["TOOLS_INDEX"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Runtime-verified with PixelArtistry_Mesh_Processing path
---
# Tool Manual — ComfyUI-KJNodes (kijai)

## Identity and purpose

KJNodes adds batch image utilities (resize, grid, pad, etc.) required by PixelArtistry mesh/pixel workflows.

- **Tool ID:** `COMFYUI_KJNODES`
- **Official:** https://github.com/kijai/ComfyUI-KJNodes
- **Local status:** `INSTALLED` — `RUNTIME_VERIFIED` 2026-11-09 in ComfyUI 0.34.2

## Installation and location

- Clone → `ComfyUI\custom_nodes\ComfyUI-KJNodes` (backup `custom_nodes.bak-20261109` first)
- Deps: `pillow, color-matcher, matplotlib, mss, opencv-python-headless` → `python_embeded\python.exe -m pip install`

## Connection and configuration

- No config. Appears in object_info: `ImageResizeKJv2` @ `nodes\image_nodes.py:2913`, 45+ KJ nodes.

## How to use

- In `PixelArtistry_Mesh_Processing.json`: use `ImageResizeKJv2`, `ImageScaleToTotalPixels`, `GetImageSize`.
- For Blender: pre-process textures (resize/pad) before sending to Blender.

## Debugging

| Symptom | Diagnostic | Fix |
|---|---|---|
| Missing PatchTritonVAE warning | triton not installed | Non-critical; only triton-VAE unavailable |
| `nodes` not a package / import fail | wrong python | Use `python_embeded\` + check class exists (`ImageResizeKJv2`) |

## Resource profile

CPU nodes ~0 MB VRAM. Downstream Flux/Trellis models need offload (see COMFYUI).

## Verification history

| Date | Machine / OS | Version | Test | Result |
|---|---|---|---|---|
| 2026-11-09 | sb291 / Win11 | ComfyUI 0.34.2 | `/object_info` → 1,271 nodes, KJ present | RUNTIME_VERIFIED ✓ |
| 2026-11-09 | sb291 / Win11 | same | `ImageResizeKJv2` code present | RUNTIME_VERIFIED ✓ |

## Removal / rollback
Delete `ComfyUI-KJNodes` or restore `custom_nodes.bak-20261109`.
