# ANIMATION FORGE — AI CONTEXT & WORKING RULES

> **Read this file first. Do not re-explore the whole repository.**
> This is the single fast-context map for AI agents. It is also the project rule file:
> **update it in the same change as any work you do** (see §8).

---

## 0. Snapshot (verify before trusting)

- **Last source review:** 2026-11-09. Reviewed main base: 0dcebb3e4b999c30cae96b210cc186c38edc5feb. This update adds the CR_006 proposal and reconciles the story/screenplay capability map; it does not implement runtime features. Verify resulting HEAD with git rev-parse HEAD.
- **Git:** default branch is main. Source was read through GitHub; local working-tree cleanliness was not verified.
- **Local environment:** Python, Node, installed dependencies, sidecar binaries and workstation paths are not verified by this source-only review. Follow DOCS/DEVELOPER_GUIDE.md.
- **Tests:** not run during this GitHub source review. Historical test counts in older reports are not current pass claims.
- **Instruction validator:** not run during this review. Re-run scripts/validate_instruction_repository.py locally before relying on a zero-finding result.
- **DB:** animation_forge.db remains tracked in Git; contents and history were not inspected. Do not delete or rewrite it without a separately reviewed data-preservation and exposure plan.
- **Audience Experience:** merged through PR #3. Hook library, screenplay templates, playbooks and JSON contracts are documentation/design artifacts only; there is no runtime persistence, API or UI integration yet.
- **CR_006:** a draft proposal for Story Bible/context, real provider integration, staged screenplay generation and script QC is documented under DOCS/CHANGE_REQUESTS. It is not submitted to GovernanceEngine or approved; no protected schemas, CORE rules, agent instructions, DB migrations or runtime code are changed by that proposal.
- **Pipeline V2 (outside the app):** PIPELINE/PIPELINE_V2.md, PIPELINE/BAKEOFF.md, PIPELINE/BAKEOFF/scorecard.json, scripts/pipeline/env_guard.ps1, scripts/pipeline/shot_manifest.py. See section 3.

If any line above is stale, fix it before doing anything else.

---

## 1. What this project is (30 seconds)

A **local-first, human-directed animation production OS**. Four things in one repo:

1. **Governed Markdown instructions** — constitution, modes, 16 agent roles, departments, genres, channel styles, tool manuals, provider profiles.
2. **FastAPI + SQLite backend** — approvals, governance, R&D/toolchain records, QC, and read-only project inspection.
3. **React/TypeScript UI** — 17-stage workflow stepper with per-stage viewers.
4. **Tauri 2 / Rust shell** — launches the Python backend as a sidecar with a per-launch IPC token.

Core principle: **agents propose, humans approve**. Never mark creative work approved, never overwrite an approved revision, never claim an integration works because a doc or catalog says so.

---

## 2. Where to look (minimum reading)

| Concern | File |
|---|---|
| HTTP routes (19, all IPC-token protected) | `backend/main.py` |
| DB schema (38 tables, migrations) | `backend/database.py` |
| Stage list + honest capability labels | `backend/main.py:171-210` |
| Governance / rule loading | `backend/governance/rule_loader.py` |
| Approval state machine | `backend/governance/approval_engine.py` |
| Human confirmation (Windows) | `backend/governance/windows_reviewer.py` |
| IPC token check (no fallback) | `backend/governance/local_ipc.py:25-27` |
| Demo data seeding | `backend/demo_project_runner.py:42` |
| UI (single 742-line file) | `frontend/src/App.tsx` |
| Desktop sidecar lifecycle | `src-tauri/src/main.rs` |
| Route/MCP truth | `DOCS/CAPABILITY_REGISTRY.md` |
| Story/screenplay implementation plan | `DOCS/CHANGE_REQUESTS/CR_006_STORY_CONTEXT_SCREENPLAY_QC.md` |
| Known gaps | `DOCS/INSTRUCTION_REPOSITORY_AUDIT.md` |
| Real-tool trials (outside app) | `PIPELINE/PIPELINE.md` (V1, demo), `PIPELINE/PIPELINE_V2.md` (V2, current), `P4_TRIAL_LOG.md`, `RESEARCH_P1_P3.md` |
| Bake-off spec + machine scorecard | `PIPELINE/BAKEOFF.md`, `PIPELINE/BAKEOFF/scorecard.json` |
| Pipeline scaffolding (shot manifest, env gate) | `scripts/pipeline/shot_manifest.py`, `scripts/pipeline/env_guard.ps1` |
| Verified capability matrix (disk truth) | `P0_GAP_MATRIX.md` (+ Corrections table) |

Do **not** read the full repo by default. Read this file, then only the rows above that match the task.

---

## 3. Reality matrix (most important section)

| Capability | Status | Evidence / boundary |
|---|---|---|
| Project creation | IMPLEMENTED | `POST /api/projects` |
| 17-stage workflow derivation | IMPLEMENTED (read-only) | `backend/main.py:322-402`; derives from DB/files, never backfills DONE |
| Approval engine + Windows confirm | PARTIAL / WINDOWS-ONLY | `approval_engine.py` and `windows_reviewer.py` derive the signed-in Windows account and require a native confirmation dialog. Non-Windows approval fails closed; this is not password/MFA re-authentication. |
| Project file explorer / media serving | IMPLEMENTED | `backend/main.py:284-303`; traversal + symlink containment |
| Story Bible / episode brief | PARTIAL FOUNDATION | `series.bible_json` and `episodes` exist in SQLite, but there is no versioned Story Bible / Episode Brief service, API or UI; project genre/style IDs are not wired end-to-end. See draft CR_006. |
| Screenplay context assembly | CONTRACT ONLY | `DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md` defines the target; runtime profile/canon assembly is not implemented. |
| Screenplay workflow | SCAFFOLD ONLY | `story_pipeline.py` creates a premise-specific editable scaffold. It does not call an LLM, generate scene prose, complete passes, assign scores or pass automated QC. Manual inspection is required. |
| Creative script critique | INSTRUCTION ONLY | `AGENTS/SCRIPT_CRITIC/INSTRUCTION.md` defines the review role; no independent evidence-backed critique service is wired. |
| Production breakdown | UNAVAILABLE | `generate_production_breakdown()` fails explicitly until a real approved-script-to-scene parser exists; it creates no scene rows. |
| LLM providers | SIMULATED / NOT CONNECTED | `providers/manager.py` makes no live request and does not persist estimated tokens/cost as actual usage. The credential vault is an in-memory test stub. |
| TTS | SIMULATED | `production_studios.py:176` writes sine-tone WAVs |
| Character/environment/storyboard images | SIMULATED demo files | generated by `demo_project_runner.py` |
| Animation execution | UNAVAILABLE | no capability |
| Post-production | SIMULATED | OTIO/SRT demo files only |
| Technical QC | SIMULATED | `quality_controller.py` uses predetermined demo checks and does not inspect the submitted screenplay/media. Script-specific deterministic checks and independent creative critique are not implemented. |
| ComfyUI / Blender / Unreal adapters | SIMULATION_ONLY / DOCUMENTED_ONLY | validate/record only; do not launch apps or dispatch jobs |
| MCP gateway | CATALOG ONLY | names registered, no real dispatch (`mcp_gateway.py`) |
| Asset library | INDEX ONLY | Check current asset hashes and machine-specific roots before reuse; local storage-root configuration is separate. |
| Story acquisition | DOCUMENTATION ONLY | STORY_ACQUISITION contains source/rights templates and workflow guidance; no automated rights clearance engine |
| Audience Experience | DOCUMENTATION / CONTRACTS ONLY | AUDIENCE_EXPERIENCE has hook patterns, screenplay templates, playbooks and draft JSON contracts; no persistence/API/UI or agent integration |
| Real Kokoro / Rhubarb / ComfyUI Flux / Blender demos | VERIFIED OUTSIDE THE APP | `DEMO_PIPELINE/`, `PIPELINE/PIPELINE.md` |
| Pipeline V2 spec + bake-off gate | PARTIALLY EXECUTED | `PIPELINE/PIPELINE_V2.md`, `PIPELINE/BAKEOFF.md`; scorecard has **12 rows** (T1A proof, T1B env-only, measured rows, Shot 1 clip, Shot 2 push, composites, final lit+idle, MH attempt) |
| Shot 1 VRM clip (track 1a) | RENDERED, UNSCORED | `PIPELINE/BAKEOFF/T20_shot1_angleA.mp4` + angleB: 120 frames, 640×480, 5.0 s @ 24 fps; head turn 40° + arm gesture + mouth from audio; identity perfect across angles (rig) |
| Shot 2 projection push | RENDERED, UNSCORED | `PIPELINE/BAKEOFF/T21_shot2_projection.mp4`: 120f 640×480 5.0 s; UV_PROJECT alley plate, dolly push; rigid (no bend). AI-video baseline deferred (no WAN weights) |
| Composite (character + plate) | RENDERED, UNSCORED | `PIPELINE/BAKEOFF/T22_composite.mp4`: VRM on upscaled alley, one scene; 120f 640×480 5.0 s; mouth+turn+gesture on plate |
| Lit composite (lighting pass) | RENDERED, UNSCORED | `PIPELINE/BAKEOFF/T23_v2.mp4`: 3-point + world lighting applied (dark edges fixed); idle keyframes NOT yet rendering (Blender 5 slot/eval mismatch, gesture still works) |
| Final lit+idle composite | RENDERED, UNSCORED | `PIPELINE/BAKEOFF/T26_frame2.mp4`: lit + arms-down idle (frame-2 keys — frame-1 keys dropped headless); character natural on alley |
| MetaHuman (track 1b) | GUI-BOUND, NOT CREATED | UE 5.8.4 MH suite + 311 Python classes present; `MetaHumanPerformanceFactoryNew` exists, Creator has no Python API — human 5-min step. Audio staged. See `PIPELINE/BAKEOFF/T14_metahuman_attempt.md` |
| Environment (MoGe/fSpy/projection) | MECHANICS PROVEN, CHAIN PARTIAL | C2 MoGe GLB imports (3.1M verts — needs decimation; SaveGLB writes no file in fresh runs); C4 UV_PROJECT via `mod.projectors[0].object`, 2 frames differ; fSpy solve is human GUI — see `PIPELINE/BAKEOFF/T16_T18_environment.md` |
| Shot/take bookkeeping + env gate | IMPLEMENTED (outside app) | `scripts/pipeline/shot_manifest.py` (lifecycle + approve guard verified), `scripts/pipeline/env_guard.ps1` (PASS: RAM 3.89 GB, VRAM 7209 MB) |
| Local TTS (Kokoro) / forced alignment (Rhubarb) | LOCAL_TESTED | `.venv-kokoro-test` kokoro 0.9.4 → 4.575 s WAV; rhubarb 1.14.0 → 29 cues + Moho `.dat` |
| VRM character import (Blender) | PROVEN (import + proof render) | `vrm` add-on 4.10.4, `RedHairGirl.vrm` → 225 bones, Fcl_MTH_A/I/U/E/O, 4 EEVEE frames with mouth driven from audio (T15) |
| MetaHuman + Animator pipeline | READY, NOT RUN | UE 5.8.4 `MetaHuman` suite incl. Animator (audio-driven), VRM4U present; no MH asset created yet — see `PIPELINE/BAKEOFF/T14_metahuman_measurement.md` |
| Audio provider + viseme map | PROVEN | `scripts/pipeline/audio_provider.py` (Kokoro 2.35 s WAV + contract JSON; ElevenLabs dry-run `wav_48000` seed 42), `align_to_visemes.py` (13 keyframes, 56 frames) |
| Engine comparison Blender vs Unreal | UNDECIDED | decided only by `BAKEOFF.md` track E — not yet run |

**Rule:** distinguish app capability from manual trial evidence, and both from "spec written". The app cannot run the demo pipeline today, and the V2 pipeline has not yet produced a shot.

---

## 4. Last recorded local data snapshot (2026-11-09; not verified in this source review)

- Projects: `PROJECT_001` "The Forgotten Kingdom" (`COMPLETED_PRODUCTION_PACKAGE`), `PROJECT_002` "The Dragon-Slaying Refund" (`STORY_ANALYSIS`).
- Records: 1 script, 2 scenes, 4 shots, 4 assets / 4 revisions, 4 audio lines, 15 approvals (all `APPROVED`), 5 QC reports, 0 agent executions.
- Library: 82 assets (`AST_0001`–`AST_0082`); `LIBRARY/STORAGE_ROOTS.json` is gitignored, absolute `D:\` paths; no `content_hash_sha256`.
- Tool catalog: v1.2.0, 11 task groups, 20 tools, 5 providers.
- Genres: Fantasy, Comedy. Channel styles: registry intentionally empty.

---

## 5. Verification baseline (run these, record real output)

```powershell
.\.venv\Scripts\python -m pytest -q TESTS/test_animation_forge_suite.py TESTS/test_instruction_repository.py
.\.venv\Scripts\python scripts\validate_instruction_repository.py
```

Current verification: not run by this GitHub source-edit operation. Previously recorded `31 passed` / `0 findings` are historical only. Run the commands above locally and record the exact current output.
Never report a test as passing unless you ran it in this workspace.

**Side effect:** the app suite runs the demo runner against the repo root and rewrites
tracked files under `PROJECTS/` **and `CORE/GLOBAL_WORKFLOW.md`** (timestamps, research dates,
manifests). After testing, check `git status` and restore test noise with
`git checkout -- PROJECTS/ CORE/GLOBAL_WORKFLOW.md`.

**Pipeline checks (V2, not part of pytest):**

```powershell
.\scripts\pipeline\env_guard.ps1 -StopOllama      # 0 = safe to render, 1 = insufficient headroom
.\.venv\Scripts\python scripts\pipeline\shot_manifest.py validate
```

---

## 6. Verification status and known gaps

No fresh test suite or instruction-validator run was performed during this GitHub
source review. The old 31 passed / 0 findings values are historical and must
not be treated as the current main baseline. Re-run the commands in section 5
and record observed output.

Previously resolved instruction issues included the AGENT_SCREENWRITER /
DOCS_SCREENPLAY_CONTEXT_ASSEMBLY dependency cycle, the invalid
3D_MODELING_RIGGING task ID (now MODELING_RIGGING), and missing tool-manual
audit inventory entries.

If validation goes red, record the exact finding here before working around it.

**Pipeline red (not a test failure — a capability gap).** As of 2026-11-09 the V2 pipeline has
proof renders (T13/T15) but **no scored Shot 1/Shot 2 clip**: `PIPELINE/BAKEOFF/scorecard.json`
has 2 rows, both with `total: null`. Individual tools are proven (Kokoro, Rhubarb, fSpy, Blender,
ComfyUI), the **full chain** (character turn + gesture, two angles) is not. Do not describe the
pipeline as working until a scored row exists. Remaining known blockers: MetaHuman asset (T14),
procedural blink/LookAt/micro-motion (T15 remainder), `diffusion_models/seedvr2_3b_int8_convrot.safetensors`
(~3 GB) not downloaded so `Upscale_and_background_FIXED.json` cannot run as written.

---

## 7. Known traps (code-level)

- **Rules-of-Hooks regression guard:** the previous conditional-hook defect was corrected by extracting StoryboardAndAnimaticStage. Keep hooks inside React components/custom hooks; stageViewer must remain a hook-free selector.
- **DB in git:** `animation_forge.db` is tracked (contains demo state). Treat schema changes as migrations, not file replacements.
- **Docs drift:** `README.md` and the audit still mention a "fixed token fallback"; the code has none (`local_ipc.py`). Audit's "96 files, 0 findings" is stale.
- **Tauri readiness:** the Host header now uses the selected dynamic backend port; keep it aligned with the actual sidecar port if lifecycle code changes.
- **Two realities:** README/status describe the *app* (simulated); `PIPELINE/PIPELINE.md` describes *manual trials* (real tools). Never merge these claims.
- **Tests dirty tracked files:** `TESTS/test_animation_forge_suite.py` runs the demo runner against the repo root, rewriting `PROJECTS/` manifests and reports. Revert with `git checkout -- PROJECTS/` after a test run.

---

## 8. Mandatory update rule (every change)

After **any** change to code, schema, catalog, registry, tool manual, doc, project data, or scripts, in the **same change**:

1. Update this `AGENTS.md`:
   - §0 snapshot: date, commit/working-tree state, test + validator results.
   - §3 Reality matrix: only if behaviour/capability changed.
   - §4 data state: only if counts/records/roots changed.
   - §6 known red baseline: remove fixed findings, add new ones.
   - §9 change log: add one row.
2. Run the verification commands in §5 and record the **actual** output.
3. Do not create a second project map; extend this file instead.

If you cannot update this file, stop and say why.

---

## 9. Change log (newest first)

| Date | Change | Files | Verification |
|---|---|---|---|
| 2026-11-09 | **CR_006 draft proposal**: scope Story Bible/context, live LLM provider, staged screenplay generation and evidence-based script QC; no runtime or protected schema changes | `DOCS/CHANGE_REQUESTS/CR_006_STORY_CONTEXT_SCREENPLAY_QC.md`, `DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md`, `DOCS/CAPABILITY_REGISTRY.md`, `DOCS/DEVELOPER_GUIDE.md`, `AGENTS.md` | Source-readback only; proposal not submitted to GovernanceEngine; tests/build not run; no runtime capability added |
| 2026-11-09 | **T14 MetaHuman headless attempt**: 311 classes, factory exists, Creator GUI-bound | `PIPELINE/BAKEOFF/T14_metahuman_attempt.md`, `scorecard.json` (12 rows), `AGENTS.md`, Library.uproject (Python plugin, backup kept) | UnrealEditor-Cmd + PythonScript runs; audio staged; asset creation needs human 5-min GUI step |
| 2026-11-09 | **VRM RIG POC M2/M4a**: FBX→UE 5.8 import (skeleton OK, morphs lost) | `PIPELINE/VRM_RIG_POC/{scripts/vrm_export_fbx.py,ue_import_fbx.py,ue_probe*.py,IMPORT_REPORT.md,README.md,outputs/M2*.fbx,ue_import*.log}`, `AGENTS.md` | UE Python import Success 0 errors; 225 bones; `get_all_morph_target_names()==[]` (full + Face-only); validator `0 findings`; pytest `31 passed` |
| 2026-11-09 | **VRM RIG POC M1**: folder + headless import (Blender 5.2.1), maps + import report | `PIPELINE/VRM_RIG_POC/{README.md,IMPORT_REPORT.md,maps/bone_map.csv,maps/face_map.csv,outputs/M1_redhairgirl.json,.blend}`, `AGENTS.md` | M1 fresh run: 225 bones, 57 shape keys, aa/ih/ou/ee/oh+blink true, import FINISHED; validator `0 findings`; pytest `31 passed` |
| 2026-11-09 | **VRM→Unreal env correction**: UE 5.8 `D:\Work\Epic\UE_5.8` (not missing), Faceit 2.3.65 in Blender 5.2 | `PIPELINE/VRM_UNREAL_RESEARCH.md`, `AGENTS.md` | Verified `UE_5.8\.egstore`; Faceit manifest 2.3.65 GPL; vrm manifest 4.10.4 Blender 4.2–5.3 |
| 2026-11-09 | **VRM→Unreal research (no code)**: feasibility, A/B/C comparison, repo audit, Sequencer Option 1 recommendation, POC plan | `PIPELINE/VRM_UNREAL_RESEARCH.md`, `AGENTS.md` | Evidence: docs.blender.org 5.2 LTS; extensions VRM 4.10.4; GitHub API saturday06/ruyo; reallusion.com v2.03 (UE 5.6–5.8) |
| 2026-11-09 | **Final lit+idle composite (T26)**: frame-2 idle keys fix | `scripts/pipeline/final_composite.py`, `PIPELINE/BAKEOFF/T26_frame2.mp4`, `scorecard.json` (11 rows), `AGENTS.md` | 120f 640x480 24fps 5.0s; arms hang naturally at 2s. Root cause: frame-1 keyframes dropped in headless render; frame-2 keys render |
| 2026-11-09 | **Lighting pass (T23)**: 3-point + world, idle investigation | `scripts/pipeline/lighting_idle.py`, `scripts/pipeline/composite_shot.py`, `PIPELINE/BAKEOFF/T23_v2.mp4`, `T23_lit.blend`, `scorecard.json` (10 rows), `AGENTS.md` | Lighting fixed; idle investigated (root cause found later: frame-1 keys) |
| 2026-11-09 | **Composite (T22)**: character on plate, one scene | `scripts/pipeline/composite_shot.py`, `PIPELINE/BAKEOFF/T22_composite.mp4`, `T22_composite/*.png` (120), `scorecard.json` (9 rows), `AGENTS.md` | 120f 640×480 24 fps 5.0 s (ffprobe); check frames show character standing in alley with turn+gesture; dark plate edges noted |
| 2026-11-09 | **Pipeline V2 T21 Shot 2**: projection push clip | `scripts/pipeline/shot2_projection.py`, `PIPELINE/BAKEOFF/T21_shot2_projection.mp4`, `T21_shot2/*.png` (120), `scorecard.json` (8 rows), `AGENTS.md` | 120f 640×480 24 fps 5.0 s (ffprobe); start/end check frames show dolly push, alley rigid (no bend); flat plane (not true depth); AI-video baseline deferred |
| 2026-11-09 | **Pipeline V2 T19 complete + T20 Shot 1 (1a)**: BiRefNet cutout + VRM performance clip | `PIPELINE/BAKEOFF/alley_birefnet_cutout.png`, `scripts/pipeline/shot1_vrm.py`, `PIPELINE/BAKEOFF/T20_shot1_angleA.mp4`, `T20_shot1_angleB.mp4`, `T20_shot1/*.png` (240), `scorecard.json` (7 rows), `AGENTS.md` | BiRefNet 545×360 RGBA alpha 0-255 (4.5%/88.9%); Shot 1: 240 PNGs in ~3.3 min, 2× mp4 640×480 24 fps 5.0 s (ffprobe); head-turn + gesture visually confirmed in check frames; identity identical across angles |
| 2026-11-09 | **Pipeline V2 T19**: SeedVR2 int8 download + live upscale | `models/diffusion_models/seedvr2_3b_int8_convrot.safetensors` (3,298 MB, outside repo), `PIPELINE/BAKEOFF/alley_seedvr2_upscaled.png`, `scorecard.json` (5 rows), `AGENTS.md` | All 3 graph models + all graph nodes validated; live upscale 545×360 → 2192×1440 (4×) ~20 s; substituted `ImageScaleBy` for `ResizeImageMaskNode` DynamicCombo; BiRefNet cutout not run (open) |
| 2026-11-09 | **Pipeline V2 Gate 2b**: blink/micro-motion, score.py, environment chain (MoGe GLB + UV_PROJECT parallax) | `scripts/pipeline/mouth_drive.py`, `scripts/pipeline/score.py`, `scripts/pipeline/parallax_test.py`, `PIPELINE/BAKEOFF/T16_T18_environment.md`, `PIPELINE/BAKEOFF/T18_frames/*`, `PIPELINE/BAKEOFF/plate_alley.jpg`, `moge_alley.glb`, `scorecard.json` (4 rows), `AGENTS.md` | T15 re-render with blink + head micro-motion; score.py appends ffprobe row (640×480 PNG); C2: MoGe GLB = 3.1M verts (SaveGLB writes no file in fresh runs — recorded); C4: 2 frames differ via `mod.projectors[0].object`; env_guard PASS; ComfyUI stopped after test |
| 2026-11-09 | **Pipeline V2 Gate 2 (partial)**: VRM import + mouth-drive proof, audio provider + viseme mapper, MetaHuman env measurement | `scripts/pipeline/vrm_inspect.py`, `scripts/pipeline/mouth_drive.py`, `scripts/pipeline/audio_provider.py`, `scripts/pipeline/align_to_visemes.py`, `PIPELINE/audio/*`, `PIPELINE/BAKEOFF/T13_*`, `PIPELINE/BAKEOFF/T14_*`, `PIPELINE/BAKEOFF/T15_frames/*`, `PIPELINE/BAKEOFF/scorecard.json` (2 rows), `AGENTS.md` | T13 JSON: 225 bones, Fcl_MTH_A/I/U/E/O + blink present; T15: 4 EEVEE frames, mouth open/closed differs per audio frame; T07: Kokoro 2.35 s WAV + contract JSON, ElevenLabs dry-run OK; T08: 13 keyframes, `round(2.35×24)=56` ✔; pytest `31 passed`, validator `0 findings`; `PROJECTS/` + `CORE/GLOBAL_WORKFLOW.md` restored |
| 2026-11-09 | **Pipeline V2 Gate 1**: corrected false hardware/capability facts, wrote the replacement pipeline spec and the bake-off that decides engine + facial method, added shot/take and memory guard tooling | `P0_GAP_MATRIX.md` (+Corrections), `PIPELINE/PIPELINE_V2.md`, `PIPELINE/BAKEOFF.md`, `PIPELINE/BAKEOFF/scorecard.json`, `scripts/pipeline/env_guard.ps1`, `scripts/pipeline/shot_manifest.py`, `AGENTS.md` | scorecard parses (2 shots / 5 tracks / 6 criteria / 0 rows); manifest full lifecycle + approve-without-take guard exit 1; env_guard PASS (RAM 3.89 GB, VRAM 7209 MB, D: 104.9 GB); pytest `31 passed`; validator `0 findings`; `PROJECTS/` + `CORE/GLOBAL_WORKFLOW.md` restored |
| 2026-11-09 | Documented the test-run side effect (`PROJECTS/` rewritten by the demo runner) in §5 and §7, and restored the dirtied tracked files | `AGENTS.md`; reverted `CORE/GLOBAL_WORKFLOW.md`, `PROJECTS/PROJECT_001`, `PROJECTS/PROJECT_RND` | `git status` clean of test noise; validator `0 findings`; pytest `31 passed` |
| 2026-11-09 | Fixed all pre-existing instruction-repo findings: broke the agent/contract dependency cycle, renamed task ID to `MODELING_RIGGING`, completed the tool-manual audit inventory | `DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md`, `TOOLS/CATALOG.json`, `TOOLS/ACCURIG/TOOL.md`, `TOOLS/FACEFORM_WRAP/TOOL.md`, `TOOLS/ZBRUSH/TOOL.md`, `DOCS/INSTRUCTION_REPOSITORY_AUDIT.md` | validator `127 files, 9 rules, 0 findings`; pytest `31 passed` |
| 2026-11-09 | Created this AI context + update rule; added README pointer | `AGENTS.md`, `README.md` | 10 sections present (104 lines); `git status` shows new `AGENTS.md`; tests unchanged at `29 passed, 2 failed` |
