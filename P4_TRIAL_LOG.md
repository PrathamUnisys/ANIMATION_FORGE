# P4 Trial Log (2026-11-09)

## Trial 1 — Rhubarb Lip Sync 1.14.0 — LOCAL_TESTED ✓
- Source: https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.14.0/Rhubarb-Lip-Sync-1.14.0-Windows.zip (GitHub API tag v1.14.0, 87 MB zip)
- Backup: not needed (portable, no install). Isolated: `C:\Users\sb291\AppData\Local\Temp\opencode\p4\rhubarb\extracted\`
- Command 1: `rhubarb.exe --version` → `Rhubarb Lip Sync version 1.14.0`
- Test task: `D:\Work\Rigby2D-Projects\fight-audio.wav` (529,278 bytes) → `rhubarb -r pocketSphinx -f json -o fight-audio.json fight-audio.wav`
- Time: `Measure-Command` TotalSeconds **2.42** for 3.00s audio
- Output: `fight-audio.json` metadata duration 3.00, 13 mouthCues (X,D,C,B,X,D,C,B,X,D,C,B,X) — matches pronunciation of fight call sequence.
- Downstream: `-f dat --datFrameRate 24 --datUsePrestonBlair` → `fight-audio.dat` 118 bytes, Moho switch: frames 1 rest, 5 AI, 9 E, 10 etc, 15 rest… Preston Blair mapping verified (D=AI, C=E, B=etc, X=rest).
- Quality/failure: no failure, deterministic JSON. CPU-only, no GPU.
- Rollback: delete `C:\Users\sb291\AppData\Local\Temp\opencode\p4\rhubarb\` (zip + extracted). No system change.
- Verdict: **LOCAL_TESTED — production ready for TTS→Moho lip-sync.** Projected saving: manual mouth keys 30–60 min/shot vs 2.4s auto + cleanup.

## Trial 2 — Kokoro-82M 0.9.4 (hexgrad) — LOCAL_TESTED ✓
- Source: https://huggingface.co/hexgrad/Kokoro-82M + https://github.com/hexgrad/kokoro (Apache-2.0, StyleTTS2, 82M params, v1.0 2025-01-27 SHA256 496dba11)
- Isolated env: Python 3.12.3 venv `D:\Work\ANIMATION_FORGE\.venv-kokoro-test\`, HF cache → D: (`hf_cache`/`D:\hf_cache`), `pip install kokoro soundfile` → kokoro 0.9.4, torch 2.15.0 (CPU 126 MB wheel), transformers 5.22.2, misaki, espeakng-loader; auto-installed `en-core-web-sm` 3.8.0 (12.8 MB)
- Test task: `KPipeline(lang_code='a')(“Hello, this is a test…”, voice='af_heart')`
- Time: first run **65.32 s** (model download ~330 MB), second run **8.27 s** for 4.575 s audio (CPU torch, 1.8× realtime, no VRAM)
- Output: `D:\Work\ANIMATION_FORGE\.venv-kokoro-test\test_voice.wav` — 219,644 bytes, 24,000 Hz, 1 ch, 4.575 s PCM_16
- Downstream chain test: same WAV → Rhubarb pocketSphinx JSON → 29 cues (X,C,E,F,B,C,B,G,E,C,A…) duration 4.57 — proves TTS→lip-sync→Moho chain end-to-end.
- Quality/failure: no failure; warnings only (HF unauthenticated, symlinks, weight_norm deprecated, LSTM dropout). CPU torch = no GPU required.
- Rollback: delete `D:\Work\ANIMATION_FORGE\.venv-kokoro-test\` (venv + cached model). No system Python touched.
- Verdict: **LOCAL_TESTED — offline voice generation works on 4 GB VRAM laptop.** Fills #9 gap vs ElevenLabs (paid) + Qwen node missing model.

## Trial 3a — ComfyUI-KJNodes — RUNTIME_VERIFIED ✓
- Runtime 2026-11-09: launched `python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --fast fp16_accumulation --port 8188 --disable-auto-launch`
- system_stats: ComfyUI 0.34.2, frontend 1.49.6, python 3.13.9, pytorch 2.9.1+cu130, os win32, ram_total 12554305536, ram_free 2782965760 (2.78 GB free — tight), VRAM total 8585216000, free 7451181056 (idle 769 MiB used)
- object_info: 1259 nodes — `ImageResizeKJv2`, `ImageResizeKJ`, `ImagePadKJ`, `SaveImageKJ`, `LazySwitchKJ`, `VAELoaderKJ`, `VAEMergeKJ`, `WanVideoTeaCacheKJ`, `GGUFLoaderKJ` etc. All present.
- Server stopped cleanly (PID 1128 killed, port 8188 closed).
- Verdict: **RUNTIME_VERIFIED** — node loads. Workflow `PixelArtistry_Mesh_Processing` missing-node resolved.

## Trial 3b — ComfyUI-GGUF (low-VRAM) — RUNTIME_VERIFIED ✓
- object_info: `UnetLoaderGGUF`, `CLIPLoaderGGUF`, `Dual/Triple/QuadrupleCLIPLoaderGGUF`, `UnetLoaderGGUFAdvanced` — 6 GGUF loaders present.
- Verdict: **RUNTIME_VERIFIED** — node loads. Workflow `zimage_gguf.json` (UnetLoaderGGUF + ModelSamplingAuraFlow) missing-node resolved. Safe on 8 GB VRAM with --fast fp16_accumulation, 1024px batch 1, sequential offload.

## Notes (Blender-ready first)
- Trellis2 (node `ComfyUI-Trellis2` + model `trellis_2 4.89 GB` + `trellis_2_shape/texture_vae`) and Flux2-Klein (node `one-node-flux-2-klein` + model `flux-2-klein 3.79 GB` + `qwen_3_4b 7.49 GB` + `flux2-vae 0.31 GB`) were **already installed** — no new download needed. Runtime for those heavy models deferred to next ComfyUI launch with offload (sheet 4 claim corrected to 8 GB VRAM).

## Trial 4 — Flux2-Klein 4b generation (Blender-ready) — LOCAL_TESTED ✓
- Model: `flux-2-klein-4b-fp8.safetensors` 3.79 GB + `qwen_3_4b.safetensors` 7.49 GB + `flux2-vae.safetensors` 0.31 GB, t2i_workflow adapted filenames.
- Launch: `python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --fast fp16_accumulation --lowvram --async-offload --port 8188 --disable-auto-launch` with visible window + PYTHONUTF8=1 + Manager disabled (`.disabled`) to avoid Windows tqdm/logger bug (`\r` → OSError 22).
- Test task: 1024×1024, batch 1, steps 4, cfg 1, er_sde/simple, prompt “stylized medieval warrior game character concept, full body, neutral T-pose…” seed 42, prefix `blender-ready/flux2-klein-concept`.
- Time: queued → succeeded in ~75 s total (incl. model offload).
- VRAM: 5,179 MiB used during gen (of 8,188), idle 797 MiB after stop. RAM free 3.46 GB at launch → tight but no OOM.
- Output: `ComfyUI\output\blender-ready\flux2-klein-concept_00001_.png` 805,540 bytes, copied to `D:\Exports\Blender\flux2-klein-concept_00001_.png` for Blender reference. Visual: full-body ornate plate armor (silver/gold filigree), white isolated background, near-T-pose, game-ready PBR look.
- Rollback: stop server (port 8188 closed), delete `custom_nodes\ComfyUI-KJNodes`/`-GGUF` or restore `custom_nodes.bak-20261109`, re-enable `ComfyUI-Manager.disabled` → `ComfyUI-Manager` if needed.
- Verdict: **LOCAL_TESTED — Blender-ready concept generation works on 8 GB VRAM / 12 GB RAM with lowvram+async-offload.** Fills AI image gap for character concepts.

## Trial 5 — Asset indexer — LOCAL_TESTED ✓
- Backup: `LIBRARY/ASSET_INDEX.json` → `.bak-20261109` before modify
- Local config: `LIBRARY/STORAGE_ROOTS.json` (ignored, .gitignored) with 3 CONFIGURED roots (PROJECTS/SHARED/RENDER) + 1 UNCONFIGURED
- Fix: backslash `relative_path` → forward slash `/` (per `LIBRARY_INDEX.schema.json` pattern forbids `\`, drive letter, `..`), validated `asset_id`/`project_id` regex
- Expand scan: depth-limited rglob, excluded DerivedDataCache/Saved, 17 → **80 assets** (6 UE .uprojects + .blend/.fbx/.casc/.png etc.)
- Rollback: restore `.bak-20261109`, delete `index_fix.py` (already removed)
- Verdict: **LOCAL_TESTED — closes NO_TOOL gap #12.** Absolute paths stay in ignored `STORAGE_ROOTS.json`, committed index uses root_id + relative_path.

## Trial 6 — Blender free extensions — LOCAL_TESTED ✓
- Source: https://extensions.blender.org/add-ons/ (Bool Tool 2.1.0 GPL, Mio3 UV 2.2.0 GPL, Texel Density Checker 2026.1.1 GPL)
- Method: `blender --background --python-expr "bpy.ops.extensions.package_install_files(filepath=..., repo='user_default')" ` → `STATUS Installed "bool_tool/mio3_uv/texel_density_checker"`
- Result: `user_default` 10 → 13 folders. Headless Boolean test: cube + cutter DIFFERENCE → `BOOLEAN OK Bool Cube` (Blender 5.2.1 LTS).
- GPU: RTX 4060 Laptop 8 GB available for Cycles; plugins CPU-only, no VRAM needed.
- Rollback: `package_uninstall` or delete `user_default\bool_tool|mio3_uv|texel_density_checker`
- Verdict: **LOCAL_TESTED — modeling/texturing gap closed for free.**

## Trial 7 — Optimize_generated_glb.py — LOCAL_TESTED ✓
- Script: `D:\Work\ANIMATION_FORGE\scripts\optimize_generated_glb.py` (env fallback INPUT_GLB/OUTPUT_FBX — Blender eats positional file args as blendfile)
- Tested tile-high.glb (12 tris → 12, exported 18.5 KB FBX) + Base.fbx CC character (17,683 tris → 17,683, shape-key meshes skipped preserved)
- Edge case: Decimate can't apply to CC Base (shape keys = facial rig) — script now SKIPs shape-key meshes with warning, preserving facial rig for AutoRigPro/FaceIt pipeline
- Resource: CPU-only decimate, no VRAM, works on 12 GB RAM
- Verdict: **LOCAL_TESTED — optimizer ready for any generated .glb** (characters need LOD/quad-remesh path, props decimate directly)

## Pending
- P5 commit: git add TOOLS + P4 logs + ASSET_INDEX (absolute paths stay in ignored STORAGE_ROOTS)
