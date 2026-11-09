---
prompt_id: TOOL_COMFYUI_GGUF
version: 1.0.0
modified_date: 2026-11-09
description: Operational guide for ComfyUI-GGUF (low-VRAM) in Animation Forge
dependencies: ["TOOLS_INDEX"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Runtime-verified for zimage_gguf.json path
---
# Tool Manual — ComfyUI-GGUF (city96)

## Identity and purpose

GGUF loaders enable quantized low-VRAM diffusion/text-encoders for 8 GB VRAM workflows.

- **Tool ID:** `COMFYUI_GGUF`
- **Official:** https://github.com/city96/ComfyUI-GGUF
- **Local status:** `INSTALLED` — `RUNTIME_VERIFIED` 2026-11-09

## Installation and location

- Clone → `ComfyUI\custom_nodes\ComfyUI-GGUF`
- Deps: `gguf>=0.13.0, sentencepiece, protobuf` → `python_embeded\pip install gguf`

## Connection and configuration

- object_info adds: `UnetLoaderGGUF`, `CLIPLoaderGGUF`, `Dual/Triple/QuadrupleCLIPLoaderGGUF`, `UnetLoaderGGUFAdvanced`.
- Required by `zimage_gguf.json` (`UnetLoaderGGUF` + `ModelSamplingAuraFlow`).

## How to use

- Download GGUF weights (place in `models\diffusion_models\`), load via `UnetLoaderGGUF`, same prompt path.
- For 8 GB VRAM: prefer GGUF for Flux/Qwen (3.79 GB + 7.49 GB) over full fp32; keep 1024px batch 1 + async offload.

## Debugging

| Symptom | Diagnostic | Fix |
|---|---|---|
| `import gguf` OK but loader missing | node not in object_info | restart ComfyUI, check `custom_nodes\ComfyUI-GGUF` |
| Still OOM | Full fp model | switch to GGUF weights + `--lowvram --async-offload` |

## Resource profile

Quantized weights fit 8 GB VRAM with offload; RAM offload still needed (pinned memory 4,789 MB).

## Verification history

| Date | Machine / OS | Version | Test | Result |
|---|---|---|---|---|
| 2026-11-09 | sb291 / Win11 | ComfyUI 0.34.2 | `/object_info` → 6 GGUF loaders present | RUNTIME_VERIFIED ✓ |
| 2026-11-09 | sb291 / Win11 | same | `import gguf` in verbatim python | RUNTIME_VERIFIED ✓ |

## Removal / rollback
Delete `ComfyUI-GGUF` or restore `custom_nodes.bak-20261109`.
