# P0 — Capability Gap Matrix (2026-11-09)
Source: read-only disk audit. No apps launched. Ports all closed = nothing live.
Hardware (**re-verified 2026-11-09, see Corrections at bottom**): Windows 11 Home 10.0.26200, AMD Ryzen 7 7435HS 8C/16T, **11.7 GB RAM**, RTX 4060 Laptop **8188 MiB (8 GB) VRAM**, C: **24.7 GB** free, D: **104.9 GB** free.

## Blender 5.2 extensions (user_default + blender_org, verified `Test-Path`)
**user_default:** `auto_rig_pro`, `EasyEnv`, `faceit`, `gui_slider`, `hair_brush_3d`, `keentools`, `kekit` (KitOps), `mesh_data_transfer`, `meta_human_dna`, `truedepth`
**blender_org:** `amarillos_vrm_toolkit`, `frame_by_plane`, `model_decompressor`, `pseudo_rendering_farm`, `sapling_tree_gen`, `t3d_gn_presets`, `ucupaint`, `vrm`
**lab_blender_org:** `mcp`
Note: all `blender_manifest.toml` report `1.0.0` (placeholder — real versions not yet extracted).

## ComfyUI 0.34.2 (`comfyui_version.py`)
Path: `D:\Downloads\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\`
- `custom_nodes` (9): `ComfyUI-HY-Motion1`, `ComfyUI-Manager`, `ComfyUI-Qwen-TTS`, `ComfyUI-Trellis2`, `comfyui_essentials`, `debugpadawans-comfyui-essentials`, `one-node-flux-2-klein`, `seedvr2_videoupscaler`
- `models/` 29 dirs but **only 2 checkpoints**: `dreamshaper_8.safetensors`, `sd_xl_base_1.0.safetensors`; `loras/arcane_offset.safetensors`; `controlnet/control_v11p_sd15_canny` (partial name). `qwen-tts/voices` only.
- `input/` has prior runs (`Alley Fantasy.jpg`, `Body_Basecolor.png`, `MK2 30fps.mp4`, `Puck02.mp4`); `output/` has 41 `ComfyUI_*.png` + 13 `Flux2-Klein_*.png` + 76 `seedvr2_upscaled_test_*.png` + `3d/`, `mesh/`, `video/`, `2.5D_assets/`.
- Workflows (8): `D:\Comfyui Workflow\` = PixelArtistry_CharDesign (FluxKleinOneNode, LoRA, UNET), PixelArtistry_Mesh_Processing (KJNodes, RTX), PixelArtistry_Pixal3D_native (Trellis2/Pixal3D, ~47 nodes), PixelArtistry_Skintoken (SkinTokensGenerator — needs `ComfyUI-SkinTokens`, **not** in custom_nodes), PixelArtistry_Trellis2_native (Trellis2/Pixal3D); `D:\Work\Workflows\` = `zimage_gguf.json` (Z-Image Turbo GGUF, UnetLoaderGGUF), `wanvideo_WanAnimate_example_01.json` (WanVideoWrapper + SAM2 + controlnet_aux + VHS), `image_z_image_turbo.json` (AuraFlow).
- **Corrected 2026-11-09:** TRELLIS.2 **is** installed (`trellis_2_int8_convrot` 4.89 GB + shape/texture VAEs), as are `flux-2-klein-4b-fp8` 3.79 GB, `birefnet` 0.82 GB, `moge_2_vitl_normal_fp16` 0.62 GB, `seedvr2_ema_3b_fp8_e4m3fn` 3.16 GB, `flux2-vae`, `triposplat_vae_decoder`, clip_vision, controlnet — **19 weight files / 40.7 GB**. The "only 2 checkpoints" figure counted `checkpoints/` alone and is misleading. Still missing: Z-Image GGUF, WanVideo/Wan weights, SkinTokens, Hunyuan3D. VRAM is **8 GB**, not 4 GB, so SDXL up to ~1536–2048px is viable; video and heavy 3D still need quantised/offloaded paths.

## UE / CC5 / Connectivity
- UE Engine installs: 5.6/5.7/5.8 (`UnrealEditor.exe` FileVersion `++UE5+Release-5.x-CL-…`). `Engine/Plugins` tree ≈ 4014 dirs (default). User projects: `D:\Projects\` ×6.
- CC5 5.12.1927.1 `Bin64/CharacterCreator.exe`; Shared Plugins present; `D:\Work\Reallusion Custom\` libraries.
- Ports `8188, 9876, 8000, 11434` — all `TcpTestSucceeded=False`. All MCP/server states = NOT_VERIFIED (offline as user stated).

## Gap matrix (installed vs verified kept separate)

| # | Capability | Class | Evidence | Installed (on disk) | Verified (live) |
|---|---|---|---|---|---|
| 1 | Screenwriting / story mgmt | ADEQUATE | `C:\Program Files (x86)\Final Draft 13`, `D:\Work\storyquest-studio-windows-project`, `youtube_animated_storytelling_master_blueprint.md` | Final Draft 13 + storyquest folder | NOT_VERIFIED (no live LLM, providers SIMULATION_ONLY) |
| 2 | AI image / video gen | WEAK | ComfyUI 0.34.2 + 9 nodes + 2 checkpoints only; 8 workflows require missing models/nodes (SkinTokens, WanVideoWrapper, Z-Image GGUF) | ComfyUI portable | NOT_VERIFIED (8188 closed; historic outputs prove past use) |
| 3 | Character creation / consistency | STRONG | CC5 5.12, AutoRigPro addon, FaceIt, meta_human_dna, TrueDepth, Marvelous 2025.2.143, ZBrush folder, DAZ3DIM1, Faceform Wrap 2025.11.14 | Full | NOT_VERIFIED |
| 4 | 3D modelling / retopo / texturing | STRONG | Blender 5.2 + kekit (KitOps), mesh_data_transfer, sapling_tree_gen, ucupaint, mcp; ZBrush 2025 folder | Full | NOT_VERIFIED |
| 5 | Rigging / facial animation | STRONG | AutoRigPro, FaceIt, meta_human_dna, TrueDepth, keentools, Cascadeur 2026.1.2 (+rigging tool_*.dll), AccuRIG, CC5 ActorCore | Full | NOT_VERIFIED |
| 6 | Mocap / retarget / cleanup | STRONG | FreeMoCap data + Skelly*, Cascadeur (Manny/Maximo .casc), `output.bvh` staged, VRM toolkit (`amarillos_vrm_toolkit,vrm`) | Full | NOT_VERIFIED |
| 7 | Environment / world gen | STRONG | Gaea 2.0 + `Gaea\Project/Output`, EasyEnv, sapling_tree_gen, PlantFactory folder, iCity Cyberpunk 1.7.1, MedievalCityGenerator .blend | Full | NOT_VERIFIED |
| 8 | Storyboard / camera previs | ADEQUATE | fSpy 1.0.3 (`D:\Content Creation\fSpy-1.0.3-win`), frame_by_plane, UE Sequencer, ComfyUI storyboard tags | Present | NOT_VERIFIED (no previs render verified) |
| 9 | TTS / voice / lip-sync / audio | WEAK | Qwen-TTS node but `qwen-tts/voices` only (no model); Kokoro/ElevenLabs SIMULATION_ONLY; RVC zip staged not installed; VRM_Converter present; Audacity 3.7.7 | Node only | NOT_VERIFIED |
| 10 | Rendering / compositing | ADEQUATE | Blender Cycles, UE (Lumen), Resolve 21.0.0.48 Fusion, pseudo_rendering_farm addon — but 4 GB VRAM + 12 GB RAM bottleneck | Present | NOT_VERIFIED |
| 11 | Editing / delivery | STRONG | Resolve 21, Blender VSE, OBS 31.1.2, ffmpeg, Audacity | Full | NOT_VERIFIED |
| 12 | Asset mgmt / DCC interop | NO_TOOL | `LIBRARY/ASSET_INDEX.json` empty `[]`; `STORAGE_ROOTS.example.json` 4 roots UNCONFIGURED; `D:\Library`, `D:\Content Creation`, `D:\Exports` manual folders; `ASSET_MAP.md` new but not indexed | NO_TOOL (manual folders only) | NOT_VERIFIED |

Definitions per `TOOLS/README.md:48-56`: NO_TOOL = verified absent, WEAK = present but thin/bottlenecked, ADEQUATE = present functional, STRONG = full pipeline present, NOT_VERIFIED = no live check yet. All Installed rows are NOT_VERIFIED live (ports closed).

## Hardware constraints (re-measured 2026-11-09)
- **8 GB VRAM (RTX 4060 Laptop, 8188 MiB, driver 621.14):** SDXL viable to ~1536–2048px; Flux2-Klein-4B fp8 and TRELLIS.2 fit; 14 B+ video models (Wan 2.2 14B, HunyuanVideo 1.5 8.3B) do **not** fit at 12 GB RAM. Stay in the **4–6 B fp8/int8 class**.
- **11.7 GB RAM is the real bottleneck, not VRAM:** only ~0.8 GB free with `ollama app` resident at ~4.0 GB; commit 18.7/24.1 GB. Stopping Ollama before a render reclaims ~4 GB — the single cheapest optimisation available.
- **Disk: C: 24.7 GB free, D: 104.9 GB free.** C: is too tight for models; keep weights and HF cache on D:.

## P0 deliverable
This file. No changes to CATALOG yet (P5). Next: P1 targeted research 3–5 candidates per genuine gap (all except the 4 STRONG rows are targets; STRONG rows = verify only if newer maintained tool clearly beats installed).

---

## Corrections — re-verified 2026-11-09

Every row below was checked against the disk this session. Where P0 and disk disagreed, disk wins.

| P0 claim | Actual (verified) | Evidence |
|---|---|---|
12 GB RAM / **4 GB VRAM** / C: 30 GB / D: 115 GB | **11.7 GB RAM / 8188 MiB / C: 24.7 / D: 104.9** | `nvidia-smi`, `Win32_OperatingSystem`, `Win32_LogicalDisk` |
All Blender manifests "1.0.0 placeholder" | `vrm` **4.10.4** (VRM 1.0 support), `amarillos_vrm_toolkit` **1.0.19** | `blender_manifest.toml` |
ComfyUI `custom_nodes` "9" | **10** incl. `ComfyUI-GGUF`, `ComfyUI-KJNodes`, `ComfyUI-Manager.disabled` | dir listing |
"only 2 checkpoints" (implies near-empty) | **19 weight files / 40.7 GB** — TRELLIS.2, Flux2-Klein, SeedVR2, BiRefNet, MoGe-2 present | recursive size scan |
UE installs "5.6/5.7/5.8" | **5** builds: 5.4 `D:\Program Files\Epic\UE_5.4`, 5.5 `C:\Program Files\Epic Games\UE_5.5`, 5.6 `…\UE_5.6`, 5.7 `D:\Work\Epic\UE_5.7`, **5.8.4 `D:\Work\Epic\UE_5.8`** | `HKLM\SOFTWARE\EpicGames\Unreal Engine`, `Build.version` |
User projects "D:\Projects ×6" | **5** at `C:\Users\sb291\OneDrive\Documents\Unreal Projects` (FantasyHR, Again, AnimationProject, Good, Library) **plus 7** at `D:\Projects` (Stylized_*, SamuraiProject, …) | `.uproject` scan |
CC5 `5.12.1927.1` | **5.12.1928.1** (+ Headshot plugin 3.0) | uninstall registry |
Marvelous `2025.2.143` | **2025.2.81** | uninstall registry |
Row 6 Mocap = **STRONG** ("FreeMoCap data + Skelly*") | **No FreeMoCap install** (no uninstall entry, no executable). Data/artifacts only, if at all. **Downgrade to ADEQUATE / unverified.** Mocap is *not* an available lever; use Cascadeur AutoPhysics. | registry sweep, path scan |
Row 9 TTS "Kokoro/ElevenLabs SIMULATION_ONLY" | **Kokoro is INSTALLED and LOCAL_TESTED** — `.venv-kokoro-test` (Py 3.12.3, kokoro 0.9.4), model cached `D:\hf_cache`, 4.575 s WAV produced. **Rhubarb 1.14.0** installed and LOCAL_TESTED (29 cues + Moho `.dat`). | `TOOLS/KOKORO_TTS/TOOL.md:24`, `TOOLS/RHUBARB_LIP_SYNC/TOOL.md:24`, `--version` |
Row 8 fSpy "Present" | **Confirmed correct** — `fSpy.exe` 1.0.3 at `D:\Content Creation\fSpy-1.0.3-win\`, **and the Blender importer `fspy_blender` is installed** at `…\Blender\5.2\scripts\addons\fspy_blender` | `Test-Path`, addon scan |
ZBrush 2025 / Gaea 2.0 (rows 4, 7) | **Not found** at P0's claimed paths, and no uninstall entry. Treat as **UNVERIFIED, probably absent** until a real path is produced. | registry + path sweep |
Row 10/11 Resolve | **Correct** — DaVinci Resolve **21.0.00048** at `C:\Program Files\Blackmagic Design\DaVinci Resolve` | uninstall registry, `Test-Path` |
"no VRM stack" (implied) | **Blender `vrm` 4.10.4** (VRM 1.0 in+out), **VRM4U** for UE 5.8 (`…\Unreal Projects\Library\Plugins\VRM4U`, `EngineVersion 5.8.0`), **VRoid Studio 2.3.0**, **9 VRM assets** in `Documents\3D` | `blender_manifest.toml`, `VRM4U.uplugin`, registry, dir scan |
Workflows "8" | Plus **17** in `ComfyUI\user\default\workflows` — notably `3d_moge_perspective_to_mesh.json`, `Flux2 Image Edit.json`, `Upscale_and_background_FIXED.json`, `utility_birefnet_remove_background.json`, `utility_seedvr2_*` — and `D:\Work\Workflows\` holds `zimage_gguf.json`, `wanvideo_WanAnimate_example_01.json`, `image_z_image_turbo.json` | JSON node-graph scan |

**MetaHuman:** UE 5.8.4 ships the full MetaHuman suite including **MetaHuman Animator**, whose *Audio Driven Animation* workflow animates a face from a WAV with no video capture — relevant because the pipeline is TTS-driven. See `PIPELINE/PIPELINE_V2.md`.
