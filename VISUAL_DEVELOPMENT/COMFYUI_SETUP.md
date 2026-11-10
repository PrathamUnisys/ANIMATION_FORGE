# ComfyUI Setup

Everything below was verified against a **real local ComfyUI instance** on this machine,
not against documentation alone. Where a statement is an assumption rather than an
observation it is labelled.

## Verified environment

| Item | Value | How it was confirmed |
|---|---|---|
| ComfyUI version | `0.34.2` | `GET /system_stats` -> `system.comfyui_version` |
| Frontend package | `1.49.6` | `GET /system_stats` -> `comfy_package_versions` |
| Python | `3.13.9` | `GET /system_stats` -> `system.python_version` |
| PyTorch | `2.9.1+cu130` | `GET /system_stats` -> `system.pytorch_version` |
| OS | `win32` | `GET /system_stats` -> `system.os` |
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU | `GET /system_stats` -> `devices[0].name` |
| VRAM | 8 585 216 000 total, 7 411 204 096 free at idle | `GET /system_stats` -> `devices[0]` |
| RAM | 12 554 305 536 total, 1 798 213 632 free at idle | `GET /system_stats` -> `system` |
| Install path | `D:\Downloads\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\` | local disk inspection |

## Installation assumption

The module does **not** install, download or configure ComfyUI. It expects a ComfyUI
server that a human has already installed and can start. The verified instance here is
the Windows portable build.

## Starting the server

```powershell
cd D:\Downloads\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable
$env:PYTHONUTF8 = '1'
.\python_embeded\python.exe -s ComfyUI\main.py `
    --windows-standalone-build --fast fp16_accumulation --port 8188 --disable-auto-launch
```

Notes from the verified run:

- `PYTHONUTF8=1` avoids a Windows tqdm/logger crash in this portable build.
- `--fast fp16_accumulation` is what this GPU build accepted; the server reported
  "Enabled fp16 accumulation" and "Set vram state to: NORMAL_VRAM".
- `ComfyUI-Manager` was left disabled (the folder is `ComfyUI-Manager.disabled`) so the
  server starts without network calls.
- `ComfyUI-Trellis2` failed to import (`No module named 'trimesh'`) and
  `ComfyUI-KJNodes` skipped `PatchTritonVAE` (no `triton`). **Neither affects this
  module**: it only uses core nodes (`CheckpointLoaderSimple`, `CLIPTextEncode`,
  `EmptyLatentImage`, `KSampler`, `VAEDecode`, `SaveImage`, `LoadImage`, `Canny`,
  `ControlNetLoader`, `ControlNetApplyAdvanced`, `LoraLoader`).

## Connection configuration

The endpoint is a command-line option and defaults to `http://127.0.0.1:8188`.

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli comfy-check --comfy-url http://127.0.0.1:8188
```

There is no configuration file to edit; the URL is passed per command. The review UI
reads the same default and reports `CONNECTED` or `UNAVAILABLE` in its Generation
Monitor tab.

## Required models

Confirmed present via `GET /models/<folder>`:

| Folder | File | Size | Role |
|---|---|---|---|
| `checkpoints` | `dreamshaper_8.safetensors` | 2.0 GB | Default text-to-image model (SD 1.5) |
| `checkpoints` | `sd_xl_base_1.0.safetensors` | 6.6 GB | Available alternative, not used by the pilot |
| `loras` | `arcane_offset.safetensors` | 288 MB | Optional stylisation LoRA, strength 0.65 |
| `controlnet` | `control_v11p_sd15_canny.pth` | 1.4 GB | Canny ControlNet for blocking references |

`sd_xl_base_1.0.safetensors` was **not** used in the pilot: on an 8 GB card it is a
poor default next to the SD 1.5 checkpoint, and the bundled `sdxlturbo_example.json`
workflow references `sd_xl_turbo_1.0_fp16.safetensors`, which is **not** installed.

### What is NOT available here

- No IP-Adapter model and no IP-Adapter custom node. Reference conditioning is
  therefore limited to ControlNet Canny plus prompt text.
- No `comfyui_controlnet_aux`, so only the built-in `Canny` preprocessor is usable.
- No depth, pose or segmentation ControlNet models.
- No style-model, upscale-model or detection models.

The module validates every node class and required input against the live
`/object_info` **before** queueing, so a missing node or model is reported as a
validation error instead of a confusing runtime failure.

## Workflow setup

The module does not need a workflow file on disk. It builds **API-format** workflows in
code (`VISUAL_DEVELOPMENT/workflows.py`) and submits them to `POST /prompt`:

| Workflow id | Nodes | Used for |
|---|---|---|
| `txt2img_v1` | CheckpointLoaderSimple -> (LoraLoader) -> CLIPTextEncode x2 -> EmptyLatentImage -> KSampler -> VAEDecode -> SaveImage | Art-direction candidates, storyboard images |
| `txt2img_canny_v1` | the above plus LoadImage -> Canny -> ControlNetLoader -> ControlNetApplyAdvanced | Blocking references, conditioned on the deterministic layout PNG |

API-format node references use the ComfyUI convention `["node_id", output_index]`.

The bundled UI-format workflows in `ComfyUI\user\default\workflows\` are **not** used:
they carry UI node positions and widget metadata, and most reference models that are not
installed. The module's own templates are the supported path.

### Adding another workflow

1. Add a builder function in `VISUAL_DEVELOPMENT/workflows.py` returning an API-format
   dictionary.
2. Add a `workflow_id` constant and register it in the `workflow_id` argument passed to
   `generate_image()`.
3. Run `validate_workflow(client, workflow)` against the live server before queueing.

## Reproducibility

Every image records: prompt, negative prompt, checkpoint, LoRA and strength, seed,
width, height, steps, cfg, sampler, scheduler, ControlNet name, reference images,
workflow id and version, ComfyUI prompt id, Style Bible hash, source screenplay hash,
image SHA-256 and timestamp.

The art-direction comparison uses one shared seed for every candidate so that the
differences between candidates come from the style, not from noise. Storyboard shots use
a deterministic per-shot seed derived from the shot id and the Style Bible base seed.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ComfyUI unreachable at http://127.0.0.1:8188` | Server not running | Start it with the command above, then run `comfy-check` |
| `ComfyUI rejected the workflow` with `node_errors` | Node class or model missing | Run `comfy-check`; the JSON body names the missing class/model |
| `Validation failed: missing_nodes/missing_inputs` | Workflow template does not match the running build | Compare the template against `GET /object_info/<ClassType>` |
| HTTP 10013 on bind | Windows reserved/excluded port | Pick another port; 8765 was occupied on this machine, the review UI defaults to 8790 |
| CUDA out of memory | Model too large for the card | Use `dreamshaper_8.safetensors`, lower width/height and steps, or run with `--lowvram` |
| Images generated but wrong subject | SD 1.5 cannot compose complex multi-character scenes reliably | Reduce the prompt to one dominant subject per shot, or switch the Style Bible to a higher-capacity checkpoint |

## Replacing the model

1. Drop the new checkpoint into `ComfyUI\models\checkpoints\`.
2. Confirm it is listed: `GET /models/checkpoints`.
3. Point the module at it by editing `generation_settings.model` in the Style Bible
   (`VISUAL_DEVELOPMENT/style_bible.py`, `DEFAULT_GENERATION_SETTINGS`) or by passing a
   different model when building a workflow.

The model name is stored in every image manifest, so older images keep pointing at the
model that actually produced them.
