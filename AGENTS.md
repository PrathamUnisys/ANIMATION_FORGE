# ANIMATION FORGE — AI CONTEXT & WORKING RULES

> **Read this file first. Do not re-explore the whole repository.**
> This is the single fast-context map for AI agents. It is also the project rule file:
> **update it in the same change as any work you do** (see §8).

---

## 0. Snapshot (verify before trusting)

- **Last source review:** 2026-11-10. CR_006 remains active at ARCH_V1.3.0. EP10 revision 2 and the YouTube script experiment were merged through PR #4 (`8469d6e7c1d67fb337962c53f1efbe6dbd2e2b88`). The `visual-development-storyboard` branch is based on that merge and now contains a **working** local Visual Development / Storyboard module: the full approved-script -> analysis -> art direction -> Style Bible -> storyboard -> blocking -> review -> handoff pipeline, verified against a live local ComfyUI 0.34.2 instance (26 real images). Status and exact limits: `VISUAL_DEVELOPMENT/IMPLEMENTATION_STATUS.md`.
- **Git:** default branch is main. Visual-development work is isolated on `visual-development-storyboard`, based on `origin/main` at PR #4 merge commit. Verify branch and HEAD before any push; do not commit to main directly. The `script-creation-framework` branch (isolated Script Creation Framework MVP, commit `53a5ad33`) was pushed separately and is unrelated to this module.
- **Tests:** historical CR_006 baseline: 45 passed (18 animation_forge_suite + 13 instruction_repository + 8 cr006_story_screenplay + 6 cr006_hardening) on 2026-11-09. Current prescribed run (2026-11-10): 30 passed, 1 failed at the validator-backed CR_007 check. New module suite `TESTS/test_visual_development.py`: **30 passed** (hermetic; uses an in-process mock ComfyUI server). Nine known demo/workflow rewrites plus one extra blank line in the revised YS03 script were restored after the prescribed run.
- **Instruction validator:** historical baseline was 130 files, 9 rules, 0 findings (2026-11-09). Current run (2026-11-10): 131 files, 9 rules, 2 findings for `DOCS/CHANGE_REQUESTS/CR_007_YOUTUBE_SCREENWRITING_AUDIENCE_EXPERIENCE.md` (missing opening YAML delimiter; missing audit inventory entry). These findings are pre-existing and were not changed by the visual-development work.
- **Frontend:** `npm run build` passed (vite 5.4.21); Story Workspace tabs A–G implemented.
- **DB:** animation_forge.db tracked; CR_006 hardening added migration v3 (source/context columns), total 44 tables, ARCH_V1.3.0 active, CR_006 APPROVED. Pre-hardening backup at `C:\Users\sb291\AppData\Local\Temp\opencode\animation_forge_backup_20261109_181757_469325.db` (integrity ok). Migration tested on disposable copy before tracked DB.
- **CR_006 hardening (H1–H8):** outline/approval gates enforced (no outline → fail; latest unapproved → fail; new outline supersedes old approval); collision-resistant artifact IDs (`ART_{project}_{episode}_{type}_{uuid8}`) with BEGIN IMMEDIATE + retry; exact source-revision refs on every downstream artifact; context package feeds every generation stage with hash over project/brief/canon/profiles (no Fantasy fallback, no fabricated channel); QC project+episode isolated with NOT_TESTED semantics and unique report IDs; critique findings validated, dedicated CritiquePayload; staged screenplay approval requires exact-revision QC (no BLOCKER) + critique (+ MAJOR acknowledgement). Live screenplay pilot (opencode/crouton-alpha-free, 6 LIVE stages, real tokens) shows QC FAIL on live output — approval gate correctly blocks; no fake success.
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
| Visual development/storyboard module (working, live-verified) | `VISUAL_DEVELOPMENT/README.md` (entry point), `USER_GUIDE.md`, `COMFYUI_SETUP.md`, `EXAMPLE_PROJECT.md`; status and limits in `IMPLEMENTATION_STATUS.md` and `KNOWN_LIMITATIONS.md`; standalone from backend/frontend until a separate approved integration change |

Do **not** read the full repo by default. Read this file, then only the rows above that match the task.

---

## 3. Reality matrix (most important section)

| Capability | Status | Evidence / boundary |
|---|---|---|
| Project creation | IMPLEMENTED | `POST /api/projects` |
| 17-stage workflow derivation | IMPLEMENTED (read-only) | `backend/main.py:322-402`; derives from DB/files, never backfills DONE |
| Approval engine + Windows confirm | PARTIAL / WINDOWS-ONLY | `approval_engine.py` and `windows_reviewer.py` derive the signed-in Windows account and require a native confirmation dialog. Non-Windows approval fails closed; this is not password/MFA re-authentication. |
| Project file explorer / media serving | IMPLEMENTED | `backend/main.py:284-303`; traversal + symlink containment |
| Story Bible / episode brief | IMPLEMENTED (CR_006 M1) | `story_context.py` versioned Bible (PROPOSED/DRAFT/IN_REVIEW/APPROVED) with SHA-256 revision hash, Episode Brief with genre/channel validation, approved canon only via human-confirmed transition. APIs `GET/POST /api/story-bibles`, `GET/POST /api/projects/{id}/episode-briefs/{ep}`, context assay `GET /api/projects/{id}/story-context`. UI: Story Context panel in `frontend/src/App.tsx`. |
| Screenplay context assembly | IMPLEMENTED + HARDENED (H2) | `StoryContextService.assemble_context()` resolves exact genre/channel profiles + hashes, approved Bible revision, brief, screenwriter instruction into an immutable package; hash covers project/brief/canon/profiles/version (timestamps excluded). No Fantasy fallback; unregistered channel reported, never fabricated. Generation stages consume `prompt_context_text`. |
| Screenplay workflow | IMPLEMENTED + HARDENED (CR_006 M3/H1) | `story_pipeline.py` staged: analysis → hooks → outline (human approve) → scene cards (requires APPROVED latest outline) → screenplay (requires APPROVED latest outline + scene cards; exact source refs) → retention. Collision-resistant IDs, BEGIN IMMEDIATE, new outline supersedes old approval. Legacy scaffold retained for backward compat. Live generation requires Ollama (BLOCKED when down); mock is deterministic and labelled. |
| Creative script critique | IMPLEMENTED (CR_006 M4) | `backend/qc/screenplay_qc.py` CreativeCritique via provider LLM (SCRIPT_CRITIC contract); every finding cites scene/passage with severity + evidence/interpretation/recommendation. Mock path label explicit. No scores. |
| Production breakdown | UNAVAILABLE | `generate_production_breakdown()` fails explicitly until a real approved-script-to-scene parser exists; it creates no scene rows. |
| LLM providers | LIVE LOCAL + MOCK (CR_006 M2) | `providers/manager.py` OllamaOpenAICompatibleAdapter (opencode local `http://localhost:11434/v1`, ornith:9b/qwen3.5:4b) with timeout/retry, auth/rate-limit handling, structured-output validation, usage recorded only from provider response. `WindowsCredentialVault` (Credential Manager) for cloud keys. `DETERMINISTIC_MOCK` for tests. Legacy `invoke_llm()` still returns SIMULATED (never writes usage). Live smoke test BLOCKED 2026-11-09 (Ollama connection refused). |
| TTS | SIMULATED | `production_studios.py:176` writes sine-tone WAVs |
| Character/environment/storyboard images | SIMULATED demo files | generated by `demo_project_runner.py` |
| Animation execution | UNAVAILABLE | no capability |
| Post-production | SIMULATED | OTIO/SRT demo files only |
| Technical QC | IMPLEMENTED (script only, H3) | `DeterministicValidator` is project+episode isolated, exact scene-card revision, canon from approved Bible (missing = NOT_TESTED), scene/screenplay correspondence, unique report IDs (repeat-safe). Media QC remains simulated. |
| ComfyUI / Blender / Unreal adapters | SIMULATION_ONLY / DOCUMENTED_ONLY | validate/record only; do not launch apps or dispatch jobs |
| Visual development / storyboard module (isolated) | IMPLEMENTED + LIVE-VERIFIED (outside the app) | `VISUAL_DEVELOPMENT/` implements approved-script -> analysis -> 8 art-direction candidates (one shared scene/seed) -> human selection -> versioned Style Bible -> storyboard images -> deterministic normalized blocking layouts + ControlNet blocking references -> loopback review UI -> continuity report -> Blender/Unreal handoff. Verified against live ComfyUI 0.34.2 on 2026-11-10 (26 real images). **No** protected file, backend route, DB table or React change; app integration needs an approved CR. Image-to-image identity is `NOT_CHECKED`; no 3D coordinates are produced. |
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

## 4. Last recorded local data snapshot (verified 2026-11-09 after CR_006)

- Projects: `PROJECT_001`, `PROJECT_002` (legacy), `PROJECT_BELL` (CR_006 pilot, mock-backed), `PROJECT_CR006` is tests-only (temp DB, not in main DB).
- Main DB: 44 tables (was 43), migration v3 applied (source/context columns); architecture `ARCH_V1.3.0` active; CR_006 APPROVED, CR_004 still AWAITING.
- Pilot `PROJECT_BELL`: Series Bible 3 revisions (head APPROVED), Episode Brief 3 revisions, story artifacts (analysis/hooks/outline/cards/screenplay/retention), 3 screenplay revisions (V03 QC PASS, pre-hardening).
- Library/tool catalog/genres unchanged (Fantasy, Comedy; CHANNELS empty).
- Provider requests: mock entries only; no live usage (Ollama BLOCKED).
- **Visual development pilot (2026-11-10, new):** `PROJECTS/VDEV_PROJECT_001_SCR_PROJECT_001_V01_V1/` built from the only `APPROVED` screenplay (`SCR_PROJECT_001_V01`). Contains 1 analysis (3 sequences / 3 scenes / 9 shots), 1 candidate set (8 candidates), 1 Style Bible v1, **26 generations** (8 art direction, 9 storyboard, 9 blocking), 9 blocking layouts (JSON+SVG+PNG), 27 review events, 1 continuity report and 1 handoff package. The database was **not** modified; the module reads it read-only.

---

## 5. Verification baseline (run these, record real output)

```powershell
.\.venv\Scripts\python -m pytest -q TESTS/test_animation_forge_suite.py TESTS/test_instruction_repository.py
.\.venv\Scripts\python scripts\validate_instruction_repository.py
.\.venv\Scripts\python -m pytest -q TESTS/test_visual_development.py -p no:cacheprovider
```

Current verification (2026-11-09, CR_006 hardening):
- `.\.venv\Scripts\python -m pytest -q TESTS/test_animation_forge_suite.py TESTS/test_instruction_repository.py TESTS/test_cr006_story_screenplay.py TESTS/test_cr006_hardening.py` → 45 passed
- `.\.venv\Scripts\python scripts\validate_instruction_repository.py` → 130 files, 9 rules, 0 findings
- `npm run build` (frontend) → passed (vite 5.4.21)

Current verification (2026-11-10, Visual Development module):
- `.\.venv\Scripts\python -m pytest -q TESTS/test_animation_forge_suite.py TESTS/test_instruction_repository.py` → **30 passed, 1 failed**. The sole failure is the pre-existing `ContractTests.test_complete_instruction_repository_passes` CR_007 frontmatter/audit-inventory finding, unchanged by this work.
- `.\.venv\Scripts\python scripts\validate_instruction_repository.py` → **131 files, 9 rules, 2 findings**, the same two pre-existing CR_007 findings.
- `.\.venv\Scripts\python -m pytest -q TESTS/test_visual_development.py -p no:cacheprovider` → **30 passed** (hermetic; in-process mock ComfyUI server).
- Live ComfyUI 0.34.2 verified: `/system_stats`, `/object_info`, `/models/{checkpoints,loras,controlnet}`, `/upload/image`, `/prompt`, `/history/{id}`, `/view`. 26 images generated (8 art direction, 9 storyboard, 9 blocking); measured ~8 s per 768x768 image, 12-16 s for the ControlNet branch.
- Nine known demo/workflow rewrites plus `CORE/GLOBAL_WORKFLOW.md` were rewritten by the prescribed run and restored from their exact paths.

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

CR_006 verified + hardened historically: 45 passed / 0 findings / vite build passed (see §5). Prior 39 passed baseline superseded by 45 (6 hardening tests). For the 2026-11-10 YouTube script experiment, the instruction validator returned 131 files / 9 rules / 2 findings, both in CR_007 as recorded in §0. The prescribed pytest command returned **30 passed, 1 failed** (`ContractTests.test_complete_instruction_repository_passes`) because those same CR_007 findings made the validator-backed contract assertion fail. The other 30 tests passed. Pytest also emitted permission warnings when writing `.pytest_cache`. Test-side-effect files were restored; current status was inspected.

**Current validator red (2026-11-10):** `DOCS/CHANGE_REQUESTS/CR_007_YOUTUBE_SCREENWRITING_AUDIENCE_EXPERIENCE.md` is missing its opening YAML front matter delimiter and is absent from `DOCS/INSTRUCTION_REPOSITORY_AUDIT.md` inventory. This experiment does not edit or repair the proposed framework change. The prescribed test command fails only at the validator-backed repository-cleanliness assertion for these two findings; see §0 and the newest change-log entry.

The 2026-11-10 visual-development module now has a behavioral test suite
(`TESTS/test_visual_development.py`, 30 passed, hermetic via an in-process mock ComfyUI
server) and was live-verified against a local ComfyUI 0.34.2 instance. The earlier
checkpoint note (compileall only, ComfyUI unavailable) is superseded. See
`VISUAL_DEVELOPMENT/IMPLEMENTATION_STATUS.md`.

Remaining gaps (not CR_006 scope or BLOCKED):
- Live Ollama smoke test BLOCKED 2026-11-09 (connection refused on localhost:11434). Adapter + mock tests complete; live generation needs Ollama running.
- `generate_production_breakdown()` still NotImplementedError by design (no approved-script-to-scene parser).
- Channel registry empty: channel_style selection requires a registered profile; unknown IDs fail clearly.
- TTS / animation / post-production remain simulated/unavailable (out of CR_006 scope).

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
- **Observed extra test noise:** a 2026-11-10 prescribed test run also inserted a blank line into `PROJECTS/YOUTUBE_SCRIPT_EXPERIMENT/SCRIPTS/REVISED/YS03_LAKE_NATRON.md`; that exact change was restored. Recheck `git status` after future runs.
- **Large pushes get reset:** pushing ~18 MB of generated PNGs to GitHub from this machine fails with `RPC failed; curl 55 Send failure: Connection was reset`. Smaller packs (about 5 MB) push reliably, and a retry often succeeds after a failure. Commit generated image binaries in batches of a few megabytes and push each batch separately; keep code and documentation in their own commit.

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
| 2026-11-10 | **Visual Development module implemented and live-verified**: full approved-script -> analysis -> 8 art-direction candidates (one shared scene/seed) -> human selection -> versioned Style Bible -> storyboard images -> deterministic normalized blocking layouts + ControlNet blocking references -> loopback review UI -> continuity report -> Blender/Unreal handoff. 13 CLI commands, 6 module schemas, 30 module tests. Pilot produced 26 real images through local ComfyUI 0.34.2. No backend route, DB table, protected file or React change. | `VISUAL_DEVELOPMENT/` (14 modules, 6 schemas, 9 docs), `TESTS/test_visual_development.py`, `PROJECTS/VDEV_PROJECT_001_SCR_PROJECT_001_V01_V1/`, `AGENTS.md` | Live ComfyUI 0.34.2 (RTX 4060, 8 GB): `/system_stats`, `/object_info`, `/models/*`, `/upload/image`, `/prompt`, `/history/{id}`, `/view` all exercised; 26 images generated (~8 s each, 12-16 s for ControlNet). Module suite **30 passed**. Review UI: HTTP 200 dashboard, real PNG served (885 777 B), path traversal refused, approve/reject recorded. Continuity: 6 PASS, 0 FAIL, 1 REVIEW (Act III has no scene heading), 1 NOT_CHECKED (image identity). Prescribed pytest: 30 passed, 1 failed on the pre-existing CR_007 findings; validator: 131 files, 9 rules, same 2 findings. Nine test-noise files plus `CORE/GLOBAL_WORKFLOW.md` restored. Three pilot defects found and fixed (non-unique shot ids, `APPROVE` vs `APPROVED` review vocabulary, orphan PNG on manifest failure). |
| 2026-11-10 | Paused visual-development implementation after R&D and initial project-core checkpoint; documented exact implemented/incomplete status. No existing runtime or protected framework structures changed. | `VISUAL_DEVELOPMENT/`, `AGENTS.md` | `compileall` PASS (syntax only); module unit tests NOT_RUN. Prescribed pytest: 30 passed, 1 failed on existing CR_007 frontmatter/audit-inventory findings; validator: 131 files, 9 rules, same 2 findings. Test-generated changes restored. ComfyUI unavailable at `127.0.0.1:8188`. See `VISUAL_DEVELOPMENT/IMPLEMENTATION_STATUS.md`. |
| 2026-11-10 | Added visual-development R&D, architecture and implementation decisions. Selected an isolated file-backed module; documented current approved-script availability and unavailable local ComfyUI without changing runtime structures. | `VISUAL_DEVELOPMENT/{RESEARCH_REPORT.md,TECHNICAL_DECISIONS.md,ARCHITECTURE.md,IMPLEMENTATION_PLAN.md,KNOWN_LIMITATIONS.md}`, `AGENTS.md` | Prescribed pytest: 30 passed, 1 failed on existing CR_007 frontmatter/audit-inventory findings; validator: 131 files, 9 rules, same 2 findings. Nine test-noise files restored. Live ComfyUI health/object-info requests timed out; no process or listener found. |
| 2026-11-10 | Refreshed stale repository snapshot after PR #4 merged EP10 revision 2 and the YouTube script experiment; created the isolated `visual-development-storyboard` implementation branch from current `origin/main` | `AGENTS.md` | Prescribed pytest: 30 passed, 1 failed at the validator-backed contract check because of the existing two CR_007 findings; validator: 131 files, 9 rules, 2 findings (same CR_007 issues). Nine test-noise files restored. Snapshot verified: start HEAD `8469d6e7c1d67fb337962c53f1efbe6dbd2e2b88`, branch `visual-development-storyboard`. |
| 2026-11-10 | Reconciled YouTube experiment counts after the narration-only counter showed YS04 original has 860 spoken words (its preserved header says 873); corrected progress/report references without editing the original draft | `PROJECTS/YOUTUBE_SCRIPT_EXPERIMENT/PROGRESS.md`, `PROJECTS/YOUTUBE_SCRIPT_EXPERIMENT/REPORTS/10_SCRIPT_EXPERIMENT_REPORT.md`, `AGENTS.md` | Recount confirmed YS04 860. Prescribed pytest: 30 passed, 1 failed on the existing CR_007 frontmatter/audit-inventory findings; validator: 131 files, 9 rules, same 2 findings. Nine test-noise files restored. `git diff --check` still reports four existing EP10 Markdown hard-break trailing-space lines; EP10 left untouched. |
| 2026-11-10 | **YouTube Script Experiment — 10 scripts completed editorially**: ten concepts, complete original/revised single-narrator scripts, source notes, independent reviews, change reports, cross-script experiment report, and framework recommendation only; no protected framework/runtime/schema changes, no approval or audience-performance claims | `PROJECTS/YOUTUBE_SCRIPT_EXPERIMENT/`, `AGENTS.md` | Narration/package/timecode audit PASS 10/10. Prescribed pytest: 30 passed, 1 failed due existing CR_007 frontmatter/audit inventory findings; validator: 131 files, 9 rules, 2 findings (same CR_007 findings). `git diff --check` reports four existing EP10 Markdown hard-break trailing-space lines; left untouched. Test noise in nine previously clean project/workflow files was restored; EP10 and experiment work preserved. |
| 2026-11-10 | Created first two batches (YS01–YS04) of the single-voice YouTube script experiment: original and revised scripts, concept packages, separate reviews, research notes, progress tracker, and narration counter. No runtime, protected schema, agent instruction, or framework behavior changed. | `PROJECTS/YOUTUBE_SCRIPT_EXPERIMENT/` | Counts: originals YS01–YS04 958/1,012/835/873; revisions YS01–YS04 821/848/763/885. Independent first reviews complete for all four; second reviews complete for YS01–YS02 and pending for YS03–YS04. Validator: 131 files, 9 rules, 2 CR_007 findings. Prescribed pytest: 30 passed, 1 failed on the validator-backed repository-cleanliness assertion; 9 demo files and `CORE/GLOBAL_WORKFLOW.md` rewritten by tests were restored. No audience measurement. |
| 2026-11-09 | **CR_006 HARDENING (H1–H8)**: workflow gates, collision-resistant artifacts, context-package integrity, QC isolation, critique validation, approval QC gate, Story Workspace tabs A–G, docs reconciled | `backend/database.py` (v3), `backend/departments/story_pipeline.py`, `backend/departments/story_context.py`, `backend/qc/screenplay_qc.py`, `backend/governance/approval_engine.py`, `backend/main.py`, `frontend/src/App.tsx`, `TESTS/test_cr006_hardening.py`, `DOCS/CHANGE_REQUESTS/CR_006*`, `AGENTS.md` | pytest 45 passed; validator 130 files/0 findings; vite build passed; migration v3 tested on copy before tracked DB |
| 2026-11-09 | **CR_006 IMPLEMENTED** (M0-M5): GovernanceEngine CR_006 APPROVED → ARCH_V1.3.0 via Windows dialog; versioned Bible/Brief, Ollama adapter, staged screenplay, deterministic QC + critique, pilot PROJECT_BELL (mock, QC PASS) | `backend/database.py` (v2), `backend/departments/story_context.py`, `backend/departments/story_pipeline.py`, `backend/providers/manager.py`, `backend/qc/screenplay_qc.py`, `backend/main.py` (20 new routes), `backend/governance/rule_loader.py`, `frontend/src/App.tsx`, `SCHEMAS/` (8 new), `TESTS/test_cr006_story_screenplay.py`, `DOCS/CAPABILITY_REGISTRY.md`, `DOCS/INSTRUCTION_REPOSITORY_AUDIT.md`, `DOCS/CHANGE_REQUESTS/CR_005*+CR_006*`, `GENRES/PROPOSED_PROFILE_ROADMAP.md`, `AGENTS.md`, `animation_forge.db` | pytest 39 passed; validator 130 files/0 findings; vite build passed; pilot QC PASS (V03); live Ollama SMOKE BLOCKED (not running) ||
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
