---
prompt_id: TOOL_COMFYUI
version: 1.1.0
modified_date: 2026-11-09
description: Operational guide for ComfyUI workflows in Animation Forge (verified 2026-11-09)
dependencies: ["TOOLS_INDEX", "SCHEMAS/TOOL_PROFILE.schema.json"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Verified 0.34.2, 8 GB VRAM/12 GB RAM, KJNodes+GGUF runtime, Flux2-Klein Blender-ready run, tqdm/Manager workarounds
  - version: 1.0.0
    date: 2026-11-09
    summary: Add ComfyUI operational manual with explicit connection and execution verification boundaries
---
# Tool Manual — ComfyUI

## Identity and purpose

ComfyUI is a node-based interface and local server for image/video generation, 3D-from-image (Trellis2), and mesh/texture processing.

- **Tool ID:** `COMFYUI`
- **Official repository:** https://github.com/Comfy-Org/ComfyUI
- **Local status:** `INSTALLED` — `RUNTIME_VERIFIED` 2026-11-09 (Flux2-Klein concept produced)
- **Server API:** `http://127.0.0.1:8188` (`/system_stats`, `/object_info`, `/prompt`, `/history/<id>`)

## Installation and location (verified)

- Root: `D:\Downloads\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\ComfyUI\`
- Version: **0.34.2** (`comfyui_version.py`), frontend 1.49.6, python_embeded 3.13.9, torch 2.9.1+cu130
- custom_nodes (11): ComfyUI-HY-Motion1, Manager, Qwen-TTS, Trellis2, essentials×2, one-node-flux-2-klein, seedvr2, **ComfyUI-KJNodes** (new), **ComfyUI-GGUF** (new)
- Models (~40 GB): checkpoints dreamshaper_8 1.99 GiB, sd_xl_base 6.46 GiB; diffusion flux-2-klein-4b-fp8 3.79 GB, trellis_2_int8 4.89 GB; text_encoders qwen_3_4b 7.49 GB; clip_vision g/dino ~6.1 GB; vae ~3.2 GB; SEEDVR2 3.63 GB
- custom_nodes backup: `custom_nodes.bak-20261109` (9 dirs) before edits

## Connection and configuration

```powershell
$env:PYTHONIOENCODING='utf-8'; $env:PYTHONUTF8='1'; $env:TQDM_DISABLE='1'
Start-Process -FilePath '.\python_embeded\python.exe' `
  -ArgumentList '-s ComfyUI\main.py --windows-standalone-build --fast fp16_accumulation --lowvram --async-offload --port 8188 --disable-auto-launch' `
  -WorkingDirectory 'D:\Downloads\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable'
# NOTE: launch WITH a visible window (not -NoNewWindow) so tqdm works; -NoNewWindow crashes sampler (OSError 22) — tried 3×.
```

- **Hardware gate (verified via nvidia-smi):** RTX 4060 Laptop 8,188 MiB VRAM, 12,554 MB RAM. Default launch uses LOW_VRAM + async offload (2 streams, pinned memory 4,789 MB). Never use plain `--highvram` on this laptop.
- System stats: `Invoke-RestMethod http://127.0.0.1:8188/system_stats` → `ram_free`, `vram_total/free` (idle 769 MiB VRAM, gen ~5.2 GB).
- Node check: `/object_info` → 1,271 nodes after KJNodes+GGUF (was 9 custom packs).

## How to use — Flux2-Klein Blender-ready concept (verified)

1. Ensure models in place (`flux-2-klein-4b-fp8`, `qwen_3_4b`, `flux2-vae`).
2. Use `custom_nodes\one-node-flux-2-klein\workflows\t2i_workflow.json` (API format). Adapt filenames:
   - `FK:155 CLIPLoader → qwen_3_4b.safetensors, type=flux2`
   - `FK:165 UNETLoader → flux-2-klein-4b-fp8.safetensors`
   - `FK:166 CLIPTextEncode → prompt, FK:170 EmptyFlux2LatentImage 1024×1024 batch 1, FK:171 KSampler steps 4 cfg 1 er_sde/simple seed {42}, FK:86 SaveImage prefix blender-ready/flux2-klein-concept`
3. Submit:
   ```powershell
   Invoke-RestMethod -Uri 'http://127.0.0.1:8188/prompt' -Method Post -ContentType 'application/json' -Body (ConvertTo-Json @{prompt=$wf} -Depth 8)
   ```
4. Poll: `history/<prompt_id>` until `status_str=success`, then read `outputs.FK:86.images[0].filename`; copy from `output\blender-ready\` to `D:\Exports\Blender\`.
5. Verified output: `flux2-klein-concept_00001_.png` 805 KB, 1024², medieval warrior, isolated white bg, Blender-ready.

## Keep in mind (hard-won lessons)

- **Current custom_nodes state (2026-11-09):** `ComfyUI-Manager.disabled` (renamed from `ComfyUI-Manager`) to avoid the stderr hijack tqdm crash. Flux workflow runs with Manager disabled. Re-enable only when upstream fixes tqdm/logger.
- **8 GB VRAM ≠ 4 GB.** Earlier WMI read was wrong. Budget: Flux+Qwen = 11 GB staged → sequential offload + GGUF preferred. RAM free was 2.78 GB at idle — close Chrome/VS Code during heavy runs.
- **1024px batch 1 is the safe ceiling** for Flux/Trellis on this laptop. Larger/batch >1 needs `--lowvram` + patience.
- **Models stay on D:** (40 GB). Do not fill C: (30 GB free).
- **Manager hijack bug:** `ComfyUI-Manager\prestartup_script.py` wraps stderr and crashes tqdm `\r` → `OSError [Errno 22] Invalid argument` in KSampler. Fix: rename `ComfyUI-Manager` → `ComfyUI-Manager.disabled` for Flux runs, set `TQDM_DISABLE=1`, and launch **with a window**.
- **Unicode crash:** Qwen-TTS ❌✅/emoji under cp1252 → `UnicodeEncodeError`. Fix: `PYTHONIOENCODING=utf-8 PYTHONUTF8=1`.
- **Missing triton/trimesh:** `PatchTritonVAE` (KJNodes) + `ComfyUI-Trellis2` (`trimesh`) fail import — non-critical for Flux (Trellis2 nodes will error until `trimesh` installed, keep separate trial).
- **No server auto-launch** (`--disable-auto-launch`) + manual `/system_stats` check every time.

## Debugging

| Symptom | Diagnostic | Fix |
|---|---|---|
| `Connection refused :8188` | Port closed (expected idle state) | Start with resource-safe command above (visible window) |
| `OSError [Errno 22]` in KSampler | tqdm + logger/Manager | window launch, Manager.disabled, TQDM_DISABLE + PYTHONUTF8 |
| `ModuleNotFoundError: trimesh` (Trellis2) | node import fail | install `trimesh` into python_embeded or disable node (Flux unaffected) |
| OOM (VRAM/RAM) | `nvidia-smi` + `system_stats` ram_free <2 GB | `--lowvram --async-offload`, 1024px batch 1, close apps, GGUF |
| Workflow missing model | `/object_info` + `models\` listing | use exact filename (e.g. `flux-2-klein-4b-fp8.safetensors`), Gen via GGUF loader if fp8 ooms |

## Verification history

| Date | Machine / OS | Version | Test | Result |
|---|---|---|---|---|
| 2026-11-09 | sb291 / Win11, 8 GB VRAM, 12 GB RAM | ComfyUI 0.34.2 | `/system_stats` + `/object_info` 1,271 nodes (KJNodes + GGUF loaded) | RUNTIME_VERIFIED ✓ |
| 2026-11-09 | sb291 / Win11 | same | Flux2-Klein 1024² batch 1 seed 42, LOW_VRAM async offload → `flux2-klein-concept_00001_.png` 805 KB | LOCAL_TESTED ✓ |

## Removal / rollback
Kill python (free 8188), delete `ComfyUI-KJNodes` / `ComfyUI-GGUF` or restore `custom_nodes.bak-20261109`; re-enable Manager by renaming `.disabled` → `ComfyUI-Manager`. Outputs stay in `output\blender-ready\`.
