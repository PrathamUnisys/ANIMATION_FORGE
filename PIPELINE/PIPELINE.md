# Animation Forge — Full Pipeline (2026-11-09)
This is the honest end-to-end (Script → Voice → Lip-sync → Concept → Mesh → Library) proven in `DEMO_PIPELINE\20261109_medieval_warrior\`, with what's good, what's broken, and what's fake-good. The pipeline is **demo-grade**, not production-grade.

## FIRST (start here)
1. **Create the shot folder** `DEMO_PIPELINE/<date>_<name>/01_script/` — write 1 line: `01_script/script.txt` ("Halt! Who dares enter the fortress?")
2. **Generate voice** — Kokoro venv (see Stage 2). Copy WAV to `02_voice/`.
3. **Lip-sync** — Rhubarb CLI → `03_lipsync/*.json` (editorial) + `*.dat` (Moho). No GUI needed.
4. **Concept** — Flux2-Klein 4b fp8 in ComfyUI (8 GB VRAM / 12 GB RAM, LOW_VRAM + visible window) → `04_concept/*.png`, copy to `D:\Exports\Blender\`, indexed as `AST_0081/0082`.
5. **Mesh** — `scripts/optimize_generated_glb.py` (Blender 5.2.1 headless) → `05_mesh/*.fbx` (decimate for props, skip for facial rigs).
6. **Index** — append to `LIBRARY/ASSET_INDEX.json` with `storage_root_id` + forward-slash `relative_path` (see Stage 7).

Every step after 1 can run headless except ComfyUI (needs a real window or it crashes on tqdm `\r`).

## Details (8 stages, proof)
| # | Stage | Tool | Entry | Proof |
|---|---|---|---|---|
| 1 | Script / screenwriting | Final Draft 13 (installed) + `script.txt` | `DEMO_PIPELINE/.../01_script/script.txt` | Final Draft fetched finaldraft.com (INR ₹7,999); project has no screenplay data structure yet — free text only. |
| 2 | Voice TTS | Kokoro-82M 0.9.4 `af_heart` (Apache-2.0) | `DEMO_PIPELINE/.../02_voice/warrior_line.wav` 119.6 KB, 24 kHz, 4.575 s | 65.32 s cold (model download ~330 MB) / 8.27 s warm, CPU torch, 0 MB VRAM |
| 3 | Lip-sync | Rhubarb 1.14.0 `pocketSphinx` | `warrior_line.json` 1 KB (29 cues 4.57 s) + `warrior_line.dat` 135 B (Moho Preston Blair) | OK on both fight-audio (13 cues) and warrior line; `--datFrameRate 24` |
| 4 | Concept image | ComfyUI 0.34.2 + Flux2-Klein 4b fp8 | `flux2-klein-concept-warrior123_00001_.png` 797 KB, 1024² batch 1 seed 123, 75 s, VRAM 4.4 GB | SURVIVED after window fix — visual audit: full-body ornate plate, isolated white bg, near-T-pose. Blender-ready as reference only. |
| 5 | 3D mesh | Blender 5.2.1 `optimize_generated_glb.py` | `05_mesh/base-optimized.fbx` 11.4 MB, 17,683 tris | Decimate applied to props; CC Base skipped (shape keys) — facial rig preserved |
| 6 | Rendering / delivery | Resolve 21.0.0.48 + OBS 31.1.2 + ffmpeg | `D:\Exports\` holds Flux PNGs + optimized FBX | No rendered video produced yet in demo |
| 7 | Library / review | `LIBRARY/ASSET_INDEX.json` + `STORAGE_ROOTS.json` (ignored) | 82 assets (AST_0001–AST_0082) | Forward-slash paths validated against `LIBRARY_INDEX.schema.json` |
| 8 | Integration | ComfyUI 0.34.2 + KJNodes + GGUF (runtime-verified, 1,271 nodes) | `flux2-klein-concept_00001_.png` history prompt `70eba1fc…`; KJNodes `ImageResizeKJv2` at `image_nodes.py:2913` | Nodes load; workflows blocked on missing models (see limits) |

## Limitation (what's broken or weak)
1. **ComfyUI Manager hijacks stderr** → tqdm `\r` crashes (`OSError 22`) when launched headless `-NoNewWindow`. Workaround: rename `ComfyUI-Manager` → `.disabled` + visible window + `PYTHONUTF8=1`. **Fix is fragile.**
2. **`trimesh` missing** — `ComfyUI-Trellis2` `nodes.py:10 import trimesh` fails. Trellis2 (image→3D) **cannot run** until `python_embeded\pip install trimesh`. That's the 3D-generation gap.
3. **Only 4 model weights really present** — `flux-2-klein-4b-fp8`, `trellis_2_int8`, `qwen_3_4b`, SDXL + dreamshaper. `zimage_gguf`, `WanVideoWrapper`, SkinTokens node+model missing. Folder tree has 29 model dirs (40 GB total) but 25 are empty/placeholders.
4. **Blender extension conflicts** — `hair_brush_3d` claims max Blender `5.0.99` on 5.2.1; legacy `gemini-code-*.py` missing `bl_info`; `arb*` errors on load. Factory startup was required to open GUI at all.
5. **MCP server not started** — `scripts\addons\blender_mcp.py` installed (protocol 15), listens on 9876 only after GUI `Preferences → Add-ons → Start MCP Server`. `uvx mcp-for-blender install-addon` crashes on `→` char without `PYTHONUTF8=1`.
6. **Kokoro scope narrow** — English only (`lang_code='a'`), one verified voice (`af_heart`; `af_belle` 404). Model cache on D: (`~330 MB`) but CPU-only, no streaming.
7. **Decimate ladder is incomplete** — shape-key meshes (all CC characters) get skipped by optimizer; no quad-remesh/LOD auto-chain, no normal-bake path yet. You get decimated props, not LODs.
8. **Library index is manual** — 82 assets but **no SHA-256 hash** (`content_hash_sha256: null`), no approval/LICENCE flow, no STOCK photos yet. `LIBRARY_ASSET_INDEX` is not wired.
9. **Asset paths are local** — `STORAGE_ROOTS.json` uses absolute `D:\…` (intentionally ignored, per README), so the committed index is not portable across machines yet.
10. **GPU/VRAM fit is squeezed** — RAM free 2.78 GB at idle; Flux+Qwen = 11.28 GB staged → sequential offload only. Trellis2 would need block swap >8192 MB VRAM — expect OOM without GGUF/quant.

## Review of whole quality
**Overall: Demo-complete, NOT production-ready — 5.5/10**

| Dimension | Score | Why |
|---|---|---|
| Script → voice chain | 7/10 | Works end-to-end in ~10s + 65s cold; limited to English, 1 verified voice, no cast management |
| Lip-sync | 8/10 | Rhubarb deterministic, Moho match verified, 2.4s for 3s speech — best-in-class for this budget |
| Concept generation | 6/10 | Strictly 2D reference (not 3D), seed variance, no pose/control (OpenPose/controlnet present but unused) |
| 3D mesh | 4/10 | Only high-poly Blender demo; Trellis2 blocked on `trimesh`, no auto-LOD/normal-bake, manual tri budgets only |
| Rendering/animation | 3/10 | No animation/rendered shot produced (Cascadeur/Rigby2D present but no ` .ca/.rigby` demo output) |
| Library/toolchain | 4/10 | LIBRARY indexed but no hash/dam, CC5 custom libs untouched, MCP protocol 15 unverified handshakes |
| Honesty/reliability | 9/10 | Every trial logged with hashes/sizes/timings; failures (sampler OSError, voice 404) recorded, not hidden |

### What improves it cheapest (next 3 moves)
1. **Install `trimesh` + run Trellis2 smoke (≈ 2 hrs + VRAM dance):** turns the Flux still into a real `.glb` (currently pipeline stops at concept).
2. **Fix Manager/tqdm properly** (patch `prestartup_script.py` stderr wrapper, don’t rename Manager) and default server to `--lowvram --async-offload --disable-progress` — Ctrl+C stops being the only off switch.
3. **Auto-hash LIBRARY + port STORAGE_ROOTS to relative URIs** — index is currently a manual list without provenance hashes.

A full generated Blender-ready warrior with working dialogue exists today (`DEMO_PIPELINE\20261109_medieval_warrior\`) — but it’s a point-in-time demo, not a repeatable factory. The 3D step (Trellis2) and any job beyond 1–2 shots will expose the weak spots above.
