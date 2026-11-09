# P0 — Capability Gap Matrix (2026-11-09)
Source: read-only disk audit. No apps launched. Ports all closed = nothing live.
Hardware: Windows 11 Home 10.0.26200, AMD Ryzen 7 7435HS 8C/16T, 12 GB RAM, RTX 4060 Laptop 4 GB VRAM, C: 30 GB free, D: 115 GB free.

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
- Missing deps pattern: Z-Image GGUF, WanVideo, SkinTokens, Trellis2/Pixal3D model files not present despite nodes existing. Only SDXL/dreamshaper available. VRAM 4 GB will OOM >1536px SDXL and all video/3D nodes.

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

## Hardware constraints (why P1 must respect)
- **4 GB VRAM (RTX 4060 Laptop):** limits SDXL to ≤1280px safe, Flux/Wan/Trellis2/HY-Motion likely OOM or CPU-offload. Research must filter for GGUF / quantized / low-VRAM workflows.
- **12 GB RAM:** limits large .blend/.uproject and ComfyUI batch size.
- **C: 30 GB free:** can’t hold large model downloads on C — use D: (115 GB).

## P0 deliverable
This file. No changes to CATALOG yet (P5). Next: P1 targeted research 3–5 candidates per genuine gap (all except the 4 STRONG rows are targets; STRONG rows = verify only if newer maintained tool clearly beats installed).
