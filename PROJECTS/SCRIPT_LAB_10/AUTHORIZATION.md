# SCRIPT_LAB_10 — One-Time Autonomy Authorization Record

**Project:** `SCRIPT_LAB_10` (isolated experiment project, dedicated series `SCRIPT_LAB_10_SERIES`)
**Date:** 2026-11-10
**Authorization type:** One-time, experiment-scoped, autonomous creative experiment (10-script batch only)
**Source:** User instruction at the start of this session: "ANIMATION FORGE: AUTONOMOUS 10-SCRIPT WRITING CHALLENGE"

## What this authorizes
- Autonomous progression through internal story-development gates (brief → analysis → hooks → outline → scene cards → screenplay → QC/critique → revision) for the 10 episodes of SCRIPT_LAB_10 only, without asking the user per-gate.
- Direct call to `story_pipeline.approve_outline(project_id, episode_id, human_confirmed=True)` for outline gates inside SCRIPT_LAB_10 only (see note below). This bypasses the interactive Windows confirmation dialog for these 10 internal experiment gates only.
- Live generation via the registered `OPENCODE_CLI` provider (`opencode/crouton-alpha-free`) and deterministic QC + creative critique for these 10 episodes.

## What this does NOT authorize (hard boundaries)
- **No global approval-system change.** `ApprovalEngine`, `local_ipc.py`, Windows authentication, and the human-review requirement are untouched. No code, schema, governance-rule, or provider-integration modifications were made for this experiment.
- **No invented reviewer.** Outline progression is recorded as authorized by this one-time user instruction, NOT by a named `HUMAN_*` reviewer, and NOT as the user personally reviewing each outline. Final screenplays remain `AWAITING_HUMAN_REVIEW` in the database (pipeline default) — they are NOT marked approved, canon-approved, or production-approved, and are made available for later human review by the user.
- **No touch of existing data.** Pilot `PROJECT_BELL`, `PROJECT_001`, `PROJECT_002`, approved canon, and all other projects are untouched. All SCRIPT_LAB_10 writes are scoped to `project_id = SCRIPT_LAB_10` and `series_id = SCRIPT_LAB_10_SERIES`.
- **Expiry:** This authorization expires when the ten-script batch is complete. Any further work returns to normal human-gated operation.

## Why direct `human_confirmed=True` is the narrowest option
The HTTP route `POST /api/projects/{project_id}/story/outline/approve` (`backend/main.py`) always triggers a native Windows confirmation dialog via `confirm_windows_human_action`. The user explicitly instructed NOT to request that dialog per internal outline gate during this experiment. The pipeline method itself (`story_pipeline.approve_outline`) requires only `human_confirmed=True`. Calling it directly with the experiment authorization above is therefore the narrowest experiment-scoped path that does not modify the global approval system, does not weaken IPC security, and does not permanently disable human review for any other project or future work.

## Audit trail
- Every outline approval in this project is traceable to this file plus the DB `story_artifacts` rows (artifact_id, revision, status, provider, context_hash, source_refs).
- Provider requests are recorded in `provider_requests` / `provider_usage` (real usage only, from OPENCODE_CLI step-finish events).
- A pre-experiment DB backup was taken before any SCRIPT_LAB_10 write (path recorded in `AGENTS.md` §9 change log).

## Status of final deliverables
**NOT approved.** All 10 screenplays are `AWAITING_HUMAN_REVIEW`. No `submit_human_decision` call is made during this experiment. No Bible/canon is created as APPROVED for this series.
