# Animation Forge — Pipeline V2 (2026-11-09)

The replacement for `PIPELINE.md`. That document described an **8-stage demo** that
produced 7 files (`DEMO_PIPELINE\20261109_medieval_warrior\`) and rendered no shot.
This document describes a **shot factory**: one that tracks shots, manages takes, locks
audio before animating, routes each shot to the method that suits it, and inspects real
media at the end.

> **Status discipline.** Every stage below is labelled with what is *verified*, not what is
> *hoped*. Vocabulary: **PROVEN** = run once on this machine with evidence ·
> **READY** = every tool present, not yet run in this pipeline · **TO_BUILD** = nothing
> exists yet · **UNDECIDED** = a bake-off chooses between two options.
> No stage is called working because a manual or a catalogue says so.

---

## 1. Why V1 failed

| | V1 (`PIPELINE.md`) | V2 |
|---|---|---|
Shape | 8 sequential steps, one pass | 9 phases with gates and a per-shot manifest |
Scope | 1 image, 1 audio line, 1 mesh | N shots, N takes each, resumable |
Audio | generated whenever | **locked and frozen before animation** |
Character | one concept PNG | **VRM or MetaHuman rig — same character every shot** |
Camera | none | 2.5D projection or engine camera |
Method choice | fixed | **routed per shot** (§5) |
QC | predetermined fake checks | real `ffprobe`/frame/level inspection |
Proof | 7 files, self-scored 5.5/10 | acceptance test per stage, scored in `BAKEOFF.md` |

The root cause was structural: V1 skipped workflow stages 6–9
(`ONLINE_TOOL_RESEARCH_AND_RND`, `TOOL_COMPARISON`, `PROOF_OF_CONCEPT`,
`HUMAN_TOOLCHAIN_APPROVAL`) and jumped from script to output. V2 reinstates them as
the bake-off gate.

---

## 2. Hardware reality (measured 2026-11-09)

| | Value | Consequence |
|---|---|---|
GPU | RTX 4060 Laptop **8188 MiB**, driver 621.14 | 4–6 B fp8/int8 class only |
CPU | Ryzen 7 7435HS 8C/16T | fine for CPU TTS/alignment |
RAM | **11.7 GB**, ~0.8 GB free with Ollama resident | **the real bottleneck** |
Ollama | `ollama app` = ~4.0 GB idle | stop it before renders → frees ~4 GB |
Commit | 18.7 / 24.1 GB | pagefile headroom is thin; keep batches small |
Disk | C: 24.7 GB · D: 104.9 GB | all weights and caches go to **D:** |

**Rule:** no 14 B+ model, no MetaHuman crowd, no ROOT-level video diffusion.
`scripts/pipeline/env_guard.ps1` enforces the RAM/VRAM floor before a batch starts.

---

## 3. Verified tool inventory

Only tools confirmed on disk are listed. Full evidence in `P0_GAP_MATRIX.md` §Corrections.

| Layer | Tool | Path | Status |
|---|---|---|---|
Image | ComfyUI **0.34.2** | `D:\Downloads\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable` | PROVEN (historic outputs) |
Image | Flux.2 Klein 4B fp8 + `Flux2 Image Edit.json` | `...\ComfyUI\user\default\workflows` | READY |
Depth→3D | `3d_moge_perspective_to_mesh.json` + MoGe-2 | same | READY |
Depth→3D | TRELLIS.2 (`trellis_2_int8_convrot`) | `...\models\diffusion_models` | READY |
Cutout | BiRefNet + `Upscale_and_background_FIXED.json` | same | READY (SeedVR2 half blocked, §3.1) |
Camera solve | **fSpy 1.0.3** | `D:\Content Creation\fSpy-1.0.3-win\fSpy.exe` | PROVEN (app) |
Camera solve | **fSpy-Blender importer** | `...\Blender\5.2\scripts\addons\fspy_blender` | READY |
Projection | Blender 5.2.1 `UV_PROJECT` modifier | `D:\Program Files\BlenderFoudation` | PROVEN (built-in) |
Character | VRM add-on **4.10.4** (VRM 1.0) | `...\extensions\blender_org\vrm` | READY |
Character | VRoid Studio **2.3.0** + 9 VRM assets | `C:\Users\sb291\OneDrive\Documents\3D` | PROVEN (assets exist) |
Character | CC5 **5.12.1928.1** + Headshot 3.0 | `C:\Program Files\Reallusion\Character Creator 5` | READY |
Character | MetaHuman suite incl. **Animator** | `D:\Work\Epic\UE_5.8\Engine\Plugins\MetaHuman` | READY |
Character | VRM4U (`EngineVersion 5.8.0`) | `...\Unreal Projects\Library\Plugins\VRM4U` | READY |
Rig/animation | AutoRigPro, FaceIt, AccuRIG 2.1, Cascadeur | Blender ext / registry | READY |
Animation | Unreal 5.8.4 + IKRig | `D:\Work\Epic\UE_5.8` | READY |
Render | Blender EEVEE / Cycles | Blender 5.2.1 | PROVEN |
Render | Unreal MRQ + OCIO + AccumulationDOF + mask passes | UE 5.8.4, template: `FantasyHR` | READY |
TTS | **Kokoro 0.9.4** | `.venv-kokoro-test\` | **PROVEN** (4.575 s WAV) |
TTS | ElevenLabs (later) | cloud, `wav_48000`, Pro tier | UNDECIDED (not wired) |
Lip-sync | **Rhubarb 1.14.0** | `...\Temp\opencode\p4\rhubarb\...\rhubarb.exe` | **PROVEN** (29 cues) |
Lip-sync | VRM expressions / MetaHuman Animator | Blender / UE 5.8 | UNDECIDED |
2D | Moho 14.4, Rigby2D | `C:\Program Files\Moho 14` | READY |
Finish | DaVinci Resolve **21.0.00048**, ffmpeg | `C:\Program Files\Blackmagic Design\...`, `C:\Program Files\ffmpeg\bin` | PROVEN (present) |

### 3.1 The only real gap
`Upscale_and_background_FIXED.json` requests `diffusion_models/seedvr2_3b_int8_convrot.safetensors`
(~3 GB). Installed is `SEEDVR2/seedvr2_ema_3b_fp8_e4m3fn.safetensors` — different quantisation
and folder. **Download the int8 file**; do not repoint the loader. Everything else the graph
needs (`birefnet.safetensors`, `vae/seedvr2_ema_vae_fp16.safetensors`) is present.

---

## 4. Architecture

```
A  SCRIPT + APPROVAL            existing app stages 1–4          (human gate, unchanged)
B  LOOK DEVELOPMENT
   B1 characters     VRM (VRoid/CC5)  |  MetaHuman                UNDECIDED
   B2 environments   Flux2 Image Edit → master plates             READY
C  ENVIRONMENT DEPTH                                             (CPU-cheap)
   C1 outpaint 2–3× for camera room                               TO_BUILD
   C2 3d_moge_perspective_to_mesh → GLB                           READY
   C3 fSpy camera solve                                           PROVEN app / READY chain
   C4 Blender UV_PROJECT + bake → parallax                        READY
   C5 BiRefNet cutouts / foreground layers                        READY (needs §3.1)
   C6 vtracer — flat-style plates ONLY                            TO_BUILD (optional)
D  AUDIO LOCK — run once, then freeze
   D1 line list → D2 Kokoro now / ElevenLabs later
   D3 cache WAV + alignment.json + metadata (immutable)
   D4 timing table: seconds → frames @ 24 fps
   D5 sound pass (SFX/music) — later
E  SHOT ROUTING (§5) → production
F  LIP-SYNC   phoneme→VRM expressions  |  MetaHuman Animator audio-driven   UNDECIDED
G  RENDER     Blender EEVEE/Cycles  |  Unreal MRQ       UNDECIDED (bake-off T22b)
H  FINISH     SeedVR2 upscale → Resolve 21 grade → OTIO          READY
I  QC         ffprobe / frame sampling / LUFS                    TO_BUILD
```

---

## 5. Shot routing rule

The single most important decision in this document. Encode it as code, not judgement:

| Shot characteristic | Route | Why |
|---|---|---|
Camera moves **through** an environment | **2.5D projection** (C2→C4) | geometry stays rigid; AI video bends walls |
Character **performs**, camera near-static | **rig** (VRM / MetaHuman) | consistency; a rig never re-invents a face |
Both | rig on a projected plate, composited | mask passes (§7) |
Prop insert / turnaround | **TRELLIS.2 → engine** | one asset, reused |
Atmosphere only (smoke, rain, embers, crowd) | deferred AI video, **optional** | where diffusion genuinely wins |
**Any** shot needing straight architecture | **never** AI video | hard rule |

---

## 6. Stage acceptance criteria

A stage is done only when its check passes and the evidence is recorded.

| Stage | Acceptance |
|---|---|
B1 | character imports with humanoid bones mapped, expression set present (`aa/ih/ou/ee/oh` + blink), SpringBone/LookAt active — printed by a headless script |
B2 | plate generated at target aspect; no text artefacts; human-approved |
C1 | outpainted plate ≥ 2× width with no visible seam |
C2 | GLB imports to Blender; non-degenerate geometry; vertex count recorded |
C3 | `.fspy` solves without error; Blender camera intrinsics match the plate |
C4 | rendered camera move shows **true parallax** — if the plate slides as one layer, the bake failed |
C5 | RGBA cutout with clean alpha edge, checked at 400 % zoom |
D | WAV ≥ target duration, `ffprobe` valid; alignment JSON validates; **timing table frame count = `round(duration × 24)`** |
F | mouth visibly follows audio; recorded as scored row in `BAKEOFF.md` |
G | identical shot rendered in both engines; scored row in `BAKEOFF.md` |
H | graded clip exported; OTIO parses |
I | `qc.py` flags a deliberately broken file and passes a good one |

---

## 7. Audio lock (Phase D) — the contract

Because TTS is non-deterministic and (later) paid, audio is generated **once** and frozen.

```
line  ──► WAV  +  alignment.json  +  metadata.json          (immutable)
              │
              ├─ duration, words[], phonemes[], visemes[]
              └─ provider, model, voice, seed, settings, request_id, cost
```

Implementation: `scripts/pipeline/audio_provider.py` — one interface, two backends.
Downstream stages **never** know which backend ran.

| Backend | Output | Alignment source | Status |
|---|---|---|---|
`local-kokoro` | 24 kHz PCM16 WAV | Rhubarb 1.14.0 → phonemes/visemes | **PROVEN** |
`elevenlabs` | `wav_48000`, mono, dry | API `with-timestamps` character times | not wired |

Rules:
1. `wav_48000` for ElevenLabs — **48 kHz, not 44.1**, because the deliverable is 24 fps video.
2. Mono and **dry** — pan/reverb/distance are mix decisions, applied in post, never baked in.
3. Fixed `seed`; `previous_request_ids` chained per scene for performance continuity.
4. A render never calls the network. Cached files are the artifact of record.
5. Rhubarb's 9 mouth shapes are **not** 1:1 with VRM's 5 vowels — map via phonemes, not by
   name. Naïve mapping looks wrong and is the most common mistake in this area.

---

## 8. Bake-off gate (replaces the old "skip stages 6–9")

Two control shots, scored in `PIPELINE/BAKEOFF.md`. No pipeline method is chosen by
preference; the scorecard decides.

- **Shot 1 — performance:** one line delivered **plus a head turn and a hand action**, then the
  same character from a second angle. Exposes identity drift, cutout tearing, rig quality.
- **Shot 2 — architecture:** a camera push through an interior. Exposes AI-video wall bending.

Tracks: **1a** VRM+Blender · **1b** MetaHuman+Unreal · **2** 2D Moho · **3** AI video baseline
(deferred) · **E** engine comparison (Blender vs Unreal, identical shot).

Weighted rubric: character consistency 30 · motion believability 20 · cinematic look 15 ·
lip-sync 10 · prop/texture fidelity 10 · cost (min/finished second, peak RAM/VRAM, re-roll rate) 15.

---

## 9. Honest limits (do not paper over)

1. **No native 4K.** AI plates are ~720p-class; resolution comes from SeedVR2 upscale.
2. **Wall clock.** Real AI-video shots run 15–40 min per finished 5 s. Rigged shots cost
   hours of animation up front and are then cheap to re-render. Plan around this.
3. **12 GB RAM** caps model size and makes Unreal + MetaHuman a measured risk, not an
   assumption.
4. **MetaHuman Animator drives MetaHuman only** — it cannot drive a VRM. Character choice and
   facial-method choice are therefore partly the same decision.
5. **Nothing here is proven in combination yet.** Individual tools are proven; the chain is not.
   Section 6 exists precisely so that gap is closed by evidence, stage by stage.

---

## 10. Mapping to the app's workflow stages

`backend/main.py:171-189` defines 17 stages. V2 fills them like this:

| App stage | V2 phase |
|---|---|
1 `USER_STORY_IDEA` … 4 `SCREENPLAY_APPROVAL` | A (existing, unchanged) |
5 `PRODUCTION_REQUIREMENT_ANALYSIS` | A |
6 `ONLINE_TOOL_RESEARCH_AND_RND` | §3 inventory |
7 `TOOL_COMPARISON` | **§8 bake-off** |
8 `PROOF_OF_CONCEPT` | **§8 bake-off** |
9 `HUMAN_TOOLCHAIN_APPROVAL` | human sign-off on the scorecard |
10 `PRODUCTION_PLANNING` | shot manifest (`shot_manifest.py`) |
11 `AUDIO_AND_VISUAL_PRODUCTION` | B, C, D |
12 `STORYBOARD_AND_ANIMATIC` | C4 projection renders double as animatic |
13 `ANIMATION` | E, F |
14 `POST_PRODUCTION` | H |
15 `QUALITY_CONTROL` | I |
16 `HUMAN_FINAL_APPROVAL` | human |
17 delivery | H |

Note stage 12: 2.5D projection makes the **animatic reusable** — the same render becomes the
final background, instead of being thrown away as in V1.

---

## 11. Verification

```powershell
# repo baseline (must stay green)
.\.venv\Scripts\python -m pytest -q TESTS/test_animation_forge_suite.py TESTS/test_instruction_repository.py
.\.venv\Scripts\python scripts\validate_instruction_repository.py

# the app suite rewrites tracked files under PROJECTS/ — always restore
git checkout -- PROJECTS/ CORE/GLOBAL_WORKFLOW.md
git status
```

Pipeline checks are per-stage (§6) and recorded in `BAKEOFF.md`. No stage is marked PROVEN
without a recorded result.

## 12. Rollback

- New files only (`PIPELINE/PIPELINE_V2.md`, `PIPELINE/BAKEOFF.md`, `scripts/pipeline/*`).
  Deleting them restores the previous state exactly; nothing existing is modified.
- The one download (§3.1) is a single file in `models/diffusion_models/` — delete to revert.
- No app code, no schema, no DB change is made by V2.

## 13. Change log

| Date | Change |
|---|---|
| 2026-11-09 | Created. Replaces `PIPELINE.md` (demo-grade) with a gated shot factory. Records verified tool inventory, the C2→C4 projection chain, the shot routing rule, the frozen-audio contract, and the bake-off that decides engine and facial method. |
