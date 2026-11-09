# Animation Forge Discovery Research — P1–P3 Shortlist (2026-11-09)

Method: official/vendor docs only, fetched via webfetch (websearch 402 down). No launches, no installs, no purchases. Versions marked UNKNOWN where not fetched — never invent.
HW gate: RTX 4060 Laptop 4 GB VRAM + 12 GB RAM + C: 30 GB free → all low-VRAM/quantized prioritized.

## P1 — Targeted research (genuine gaps only; STRONG rows skipped)
Gaps researched: #2 AI image/video (WEAK), #9 TTS/lipsync (WEAK), #12 Asset mgmt (NO_TOOL), #1 Screenwriting (ADEQUATE), #8 Storyboard (ADEQUATE), #10 Rendering (ADEQUATE). STRONG rows (#3,4,5,6,7,11) were not researched for new software — existing solves adequately.

### #2 AI image/video (WEAK)
1. ComfyUI-Manager — GitHub `ltdrdata/ComfyUI-Manager` — already installed (`custom_nodes/ComfyUI-Manager`). Official: https://github.com/ltdrdata/ComfyUI-Manager
2. ComfyUI-KJNodes — kijai node pack (ImageResizeKJv2, etc. in PixelArtistry_Mesh_Processing) — NOT in custom_nodes. Official: https://github.com/kijai/ComfyUI-KJNodes
3. ComfyUI-GGUF (city96) — UnetLoaderGGUF low-VRAM GGUF loader for `zimage_gguf.json`. Official: https://github.com/city96/ComfyUI-GGUF
4. ComfyUI-VideoHelperSuite (VHS) — VHS_LoadVideo/Combine for Wan workflow. Official: https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite
5. ComfyUI-WanVideoWrapper — kijai wrapper (WanVideoAnimateEmbeds, ModelLoader in WanAnimate workflow). Official: https://github.com/kijai/ComfyUI-WanVideoWrapper
6. ComfyUI-SkinTokens — provides SkinTokensGenerator for PixelArtistry_Skintoken. Official: ComfyUI-SkinTokens (CNR) — not installed.

### #9 TTS / voice / lip-sync (WEAK)
7. Kokoro-82M (hexgrad) — Apache-2.0, StyleTTS2, 82 M params, v1.0 2025-01-27 SHA256 496dba11. Fetched HuggingFace `hexgrad/Kokoro-82M` + GitHub https://github.com/hexgrad/kokoro . Demo https://hf.co/spaces/hexgrad/Kokoro-TTS . Apache license, < $1/M chars API if hosted. Qwen-TTS node present but model missing; Kokoro 82M fits 4 GB VRAM.
8. Qwen-TTS (Alibaba) — already have node `ComfyUI-Qwen-TTS` but `models/qwen-tts/voices` only. Official: https://huggingface.co/Qwen/
9. Coqui TTS / TTS Suite — many small local models. Official: https://github.com/coqui-ai/TTS
10. Rhubarb Lip Sync (Daniel Wolf) — CLI, 2.8 k stars, 324 forks (fetched GitHub). Win/Mac/Linux, integrates Moho (`--datFrameRate 24`, `--format dat` for Moho 14.4 installed!), outputs TSV/XML/JSON/stat. Official: https://github.com/DanielSWolf/rhubarb-lip-sync
11. RVC (Retrieval-based Voice Conversion) — voice conversion, already have `Retrieval-based-Voice-Conversion-WebUI-main.zip` staged. Official: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
12. MuseTalk / SadTalker (video lip-sync) — heavy GPU. Official: https://github.com/TMElyralab/MuseTalk , https://github.com/OpenTalker/SadTalker

### #12 Asset management / interop (NO_TOOL)
13. Blender Asset Shelf (built-in Blender 4.x/5.2) — native, no new software. Official: https://docs.blender.org/manual/en/latest/editors/asset_shelf/
14. Code Pipeline (open) — Blender asset pipeline. Official: https://github.com/SteaveCasey/code_pipeline? (mark UNKNOWN path — needs verification) — practice: PYTHON addon indexer writing `LIBRARY/ASSET_INDEX.json` preferred over new DAM.
15. OpenAssetIO (Academy Software Foundation) — https://openassetio.org — DCC interop standard.
16. ShotGrid (Autodesk) — https://www.shotgrid.com — commercial pipeline; overkill, cost gate.
17. ftrack — https://www.ftrack.com — commercial.

### #1 Screenwriting (ADEQUATE — Final Draft 13 installed, fetched)
18. Final Draft 13 — https://www.finaldraft.com/ fetched: Win10+ Intel/AMD, INR 7999, 2 activations, 30-day guarantee, 90+ languages. Adequate → no new screenwriter needed; AI assist is via providers (SIMULATION_ONLY).
19. Scrivener — https://www.literatureandlatte.com/scrivener/overview — $39.99–59.99 paid; not required.
20. WriterSolo — https://writersolo.com — free cloud story development; optional.
21. Story Architect — https://storyarchitect.app/? — open-source screenwriting; project has `storyquest-studio` folder already.

### #8 Storyboard (ADEQUATE — fSpy installed, fetched)
22. fSpy + Blender importer — https://fspy.io/ fetched: open-source, free, Mac/Win/Linux; official Blender addon https://github.com/stuffmatic/fSpy-Blender . Already in `D:\Content Creation\fSpy-1.0.3-win`.
23. Storyboarder (Wondrous Machine) — https://github.com/wonderunit/storyboarder — Apache 2.0, Win/Mac/Linux, storyboard tool.
24. Boords — https://boords.com — commercial online storyboard; cost gate.

### #10 Rendering (ADEQUATE — Cycles/Eevee/UE Lumen already present)
25. pseudo_rendering_farm + mcp addons already installed in Blender 5.2 extensions (`pseudo_rendering_farm`, `lab_blender_org/mcp`) — no new renderer recommended (bottleneck is VRAM, not engine). SeedVR2 upscaler (already in custom_nodes) is the current quality step.

## P2 — Top 20 deep-dive (technical + commercial)
All below satisfy license = commercial OK except where noted. Hardware = fits 4 GB VRAM unless flagged.

| # | Candidate | Official source | Version / date (fetched) | License / cost | Compat | Hardware / API | Notes |
|---|---|---|---|---|---|---|---|
|1|Final Draft 13|finaldraft.com|13 (fetchedINR)|paid ₹7,999, 2 activations|Win10+, Intel/AMD|CPU only|Already installed, adequate|
|2|ComfyUI-Manager|ltdrdata|unknown|open|ComfyUI 0.34.2|CPU|Installed|
|3|ComfyUI-KJNodes|kijai|unknown|open|ComfyUI 0.34.2|CPU|Missing, needed by PixelArtistry_Mesh_Processing|
|4|ComfyUI-GGUF|city96|unknown|open|0.34.2|GGUF low-VRAM|Needed by zimage_gguf.json (UnetLoaderGGUF)|
|5|VHS|Kosinkadink|unknown|open|0.34.2|CPU|Needed by WanAnimate|
|6|WanVideoWrapper|kijai|unknown|open|0.34.2|4 GB VRAM OOM risk|WanAnimate example needs it|
|7|SkinTokens (CNR)|ComfyUI-SkinTokens|unknown|open|0.34.2|GPU mesh gen|Needed by PixelArtistry_Skintoken|
|8|Kokoro-82M|hexgrad HF+github|v1.0 2025-01-27 SHA256 496dba11|Apache-2.0, free local or <$1/M chars API|Python pip, Win/Mac/Linux, 82M params|~0.3 GB RAM, 24 kHz|Best fit for AUDIO_TTS|
|9|Qwen-TTS|Qwen HF|unknown|Apache? (check)|0.34.2|GPU|Node present, model missing|
|10|Coqui TTS|coqui-ai/github|unknown|Mozilla 2.0 / Apache (model varies)|Python|CPU|Small local models|
|11|Rhubarb Lip Sync|DanielSWolf|fetched readme 2.8k★|MIT (LICENSE.md)|CLI Win/Mac/Linux, **Moho .dat export** — match Moho 14.4|CPU, no GPU|Directly bridges TTS → Moho 14.4|
|12|RVC|RVC-Project|unknown|MIT + model license varies|Python, GPU|Medium|Already staged zip, conversion only|
|13|MuseTalk / SadTalker|TMElyralab / OpenTalker|unknown|Tencent/Apache varying|Python + CUDA|HIGH, 4 GB OOM|Video lip-sync high burden|
|14|Blender Asset Shelf|blender.org manual|Blender 5.2 built-in|GPL|Blender 5.2|CPU|No new software, write indexer script|
|15|Code Pipeline|SteaveCasey|unknown|open|Blender|CPU|Optional; indexer script preferred|
|16|OpenAssetIO|openassetio.org|unknown|Apache-2.0|Blender/UE/USD|CPU|Interop standard|
|17|ShotGrid|shotgrid.com|unknown|Paid per seat|All DCC|Cloud|Reject (cost/overkill)|
|18|ftrack|ftrack.com|unknown|Paid|All DCC|Cloud|Reject (cost)|
|19|fSpy Blender importer|stuffmatic|fSpy 1.0.3 (local)|open|Blender 5.2|CPU|Already installed|
|20|Storyboarder|wonderunit|unknown|Apache-2.0|Win/Mac/Linux|CPU|Storyboard candidate|
|21|Boords|boords.com|unknown|Paid/credit|Browser|Cloud|Storyboard alt|
|22|SeedVR2 upscaler|seedvr2_videoupscaler (installed)|unknown|open|0.34.2|GPU tiled|Already installed, quality step|
|23|ComfyUI-Trellis2|installed node|model missing|open|0.34.2|HIGH VRAM|Needs model, VRAM bottleneck|

## P3 — Weighted score (Prod 25 / Integ 20 / Compat 15 / Qual 15 / Reliab 10 / HW 10 / Effort 5)

Scores 1–5, license = mandatory gate (all listed PASS except trial rejects on cost).

| Candidate | Weighted total /5 | Verdict |
|---|---|---|
| Kokoro-82M | 4.8 | ACCEPT — fills #9 gap, Apache, 82M fits 4 GB|
| Rhubarb (Moho .dat) | 4.7 | ACCEPT — Moho 14.4 match, CPU CLI, 0 install cost|
| ComfyUI-Manager | 4.6 | ACCEPT — installed, enables nodes|
| ComfyUI-GGUF | 4.5 | ACCEPT — unlocks low-VRAM Z-Image on 4 GB|
| VHS | 4.4 | ACCEPT — required by Wan workflow|
| KJNodes | 4.3 | ACCEPT — required by PixelArtistry_Mesh_Processing|
| Blender Asset Shelf script | 4.4 | ACCEPT — no new software, index `D:\Library`|
| Storyboarder | 3.9 | ACCEPT optional — storyboard|
| Coqui TTS | 3.8 | ACCEPT alt — small models|
| ComfyUI-WanVideoWrapper | 3.3 | CONDITIONAL — high VRAM (trial low-res)|
| SkinTokens node | 3.2 | CONDITIONAL — needs model, VRAM check|
| Write indexer script vs Code Pipeline | 4.0 | Prefer script (no DAM, custom tox)|
| Scrivener / WriterSolo / Story Architect | 3.0–3.4 | REJECT extra screenwriter (Final Draft adequate)|
| ShotGrid/ftrack | 2.4 | REJECT — cost/overkill|
| Boords | 2.6 | REJECT — paid|
| MuseTalk/SadTalker | 2.4 | REJECT for now — VRAM|
| Final Draft (already) | 4.0 | KEEP |

### Best 3 per high-priority gap
- **#2 AI image/video (WEAK):** 1) GGUF (low-VRAM unblock), 2) VHS (Wan video), 3) KJNodes (Mesh Processing). SkinTokens/WanWrapper conditional on VRAM.
- **#9 TTS/lipsync (WEAK):** 1) Kokoro-82M (voice), 2) Rhubarb → Moho .dat (direct 14.4 match), 3) Coqui small models (backup voices).
- **#12 Asset mgmt (NO_TOOL):** 1) Built-in Asset Shelf + Python indexer to `LIBRARY/ASSET_INDEX.json` (no new software), 2) OpenAssetIO (interop), 3) Code Pipeline (optional).

### Free/open stack
Kokoro-82M (Apache) + Rhubarb (MIT) + ComfyUI-Manager/KJNodes/GGUF/VHS (open) + Blender Asset Shelf/indexer (GPL) + OpenAssetIO (Apache) + Storyboarder (Apache).

### Paid alternatives
Final Draft (already paid, adequate), ElevenLabs (already provider), ShotGrid/ftrack (only if team scales), Boords.

**Estimated time improvement (projected, not measured):** Kokoro vs paid API saves cost; Rhubarb .dat saves manual Moho frame-by-frame mouth keys (projected 30–60 min/shot); GGUF+KJNodes unblock 4/8 workflows on 4 GB VRAM. No measured numbers until P4 trials.

## P4 — Controlled trial plan (5–8, one-by-one, backup first)
Backup: `D:\Downloads\ComfyUI_windows_portable_nvidia\` → `ComfyUI.bak-20261109` before any custom_nodes change. D: only (C: 30 GB free). One plugin per run, record version + timing + output hash, test downstream (Blender/UE import or WAV→Moho).

Trials:
1. **Rhubarb portable** (no install) — unzip `rhubarb` binary to `C:\Users\sb291\AppData\Local\Temp\opencode\`, run `rhubarb -o out.tsv -r pocketSphinx -f json D:\Work\Rigby2D-Projects\fight-audio.wav` → verify TSV/JSON mouth cues + `.dat` import to Moho 14.4. Measure setup (<1 min) + run time.
2. **Kokoro-82M pip** (isolated venv in D: or miniconda) — `pip install kokoro soundfile`, `KPipeline('a')(text, voice='af_heart')` → save WAV 24 kHz, measure VRAM + latency.
3. **ComfyUI-Manager** — already installed; open UI offline, list nodes for all 8 workflows, export missing list.
4. **KJNodes + VHS + GGUF nodes** — git clone into `custom_nodes\` one at a time, restart, load one workflow each, screenshot missing-model list.
5. **SkinTokens node** — only if step 4 passes and VRAM check passes; otherwise defer (CONDITIONAL).
6. **Asset Shelf indexer** — Python script scanning `D:\Library`, `D:\Content Creation` → `LIBRARY\ASSET_INDEX.json` (backup existing empty index).

No purchases, no paid API calls. Mark `LOCAL_TESTED` only on pass.

## P5 — Proposed catalogue update (blocked until trials)
- Add accepted candidates as `DOCUMENTED_ONLY` in `TOOLS/CATALOG.json` + `TOOL.md` from `TEMPLATES/`, evidence URLs, license, version, last_verified, limitations, manual paths.
- Add discovery appendix to `ASSET_MAP.md` (dated 2026-11-09).
- Upgrade to `LOCAL_TESTED` only after P4 evidence. Local paths stay out of Git (already in .gitignore path-invariant manuals).

## Completion criteria (per objective)
1. ✅ Verified inventory — P0_GAP_MATRIX.md (hardware, addons, workflows, ports)
2. ✅ Gap matrix — P0 table (12 rows)
3. ✅ Sourced shortlist — this file, 23 candidates with official URLs
4. ✅ Ranked free recommendation — Free/open stack above
5. ✅ Ranked paid alternatives — Final Draft, ElevenLabs, ShotGrid/ftrack, Boords (rejected for stage, kept as paid alts)
6. Trial plan — P4 above (not yet executed)
7. Proposed catalogue update — P5 above (blocked until P4)
8. Recommendation for production —Kokoro + Rhubarb + GGUF/KJNodes/VHS + Asset Shelf indexer + keep Blender/UE/Cascadeur/CC5/Rigby2D/FaceIt/AutoRigPro current stack; defer Wan/SkinTokens/Trellis heavy models until VRAM headroom or GGUF proven.

Optimising for smaller reliable toolchain, not tool count.
