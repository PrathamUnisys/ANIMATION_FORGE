# Engineering Remediation Baseline

**Change request:** CR_002  
**Audit phase:** Phase 0 baseline  
**Repository snapshot:** branch `main`, commit `34fb71a096a82874434de7b5352934552ed0418a`  
**Audit date:** 2026-11-09

## Scope and method

This is a read-only baseline of the current application, source, desktop configuration, database schema metadata, and tests. No application records were queried or displayed. The database file was already modified in the worktree when this audit began; preserve that live state. The local virtual environment was used for the regression suite.

The inspected surfaces include FastAPI routes and approval flow, archive import/export, the project-path guard, desktop IPC and Vite proxy configuration, provider and integration implementations, database migration metadata, and the existing Python tests. This report distinguishes working code from simulated/demo behavior.

## Repository and data state

- Current Git branch and commit: `main`, `34fb71a096a82874434de7b5352934552ed0418a`.
- `animation_forge.db` is tracked, is modified in the worktree, and appears in two prior commits. `.gitignore` does not exclude it. No records or historical database contents were inspected. No evidence was collected that the repository or database history was pushed to a remote.
- The database reports 38 tables and one recorded migration (`initial_36_entities_schema`, version 1). The application schema is declared in `backend/database.py`.
- Do not overwrite or reset the live database. Removing it from version control and any history cleanup are not included in this approved phase; inspect and authorize those separately.

## Findings

| Priority | Finding | Evidence and impact | Recommended disposition |
|---|---|---|---|
| P0 / Critical | Project bundle import permits archive path traversal and arbitrary project-directory selection. | `backend/database.py:634-660` trusts `new_project_id` in a path, joins unvalidated ZIP member names to the destination, creates parent directories, and writes contents. It updates the project row before extracting files. A malicious bundle can write outside the intended project directory and leave partial database/filesystem state. | Validate project IDs and every extracted member; reject traversal, absolute/drive paths, symlinks, special files, and duplicate destinations. Extract into a fresh staging directory, refuse existing targets, and avoid committing project metadata until validation/extraction succeeds. Add traversal and rollback tests. |
| P0 / High | The API's IPC token is fixed, public in source, and accepted by default. | `backend/main.py:15,32-33` embeds a fallback token and makes the same value the default request header. `src-tauri/src/main.rs:11-20` returns that fixed token to the frontend. `frontend/vite.config.ts:10-15` injects it into dev proxy requests. Knowing the published value is sufficient to reach every protected API route. | Remove all fixed/default secrets. Use per-launch unpredictable credentials, fail closed when no secure credential is configured, and limit trust to the intended desktop origin/channel. Do not use a committed Vite proxy secret. |
| P0 / High | A caller can assert that they are a human reviewer. | `backend/main.py:41,113-120` accepts a caller-selected reviewer ID (defaulting to `HUMAN_EXEC_PRODUCER`) and forwards it. `backend/governance/approval_engine.py:87-96` treats any string beginning `HUMAN_` as authenticated. With the exposed token, a caller can forge approval decisions. | Do not accept reviewer identity from request data. Require a trusted reviewer-authentication result. Until that exists, fail closed on API approval decisions. Decide the local reviewer identity/authentication model before enabling approvals through IPC. |
| P1 / High | Project path guard is vulnerable to filesystem aliasing and uses a non-boundary string prefix. | `backend/orchestration/agent_executor.py:53-66` checks textual paths and a string prefix, but does not resolve symlinks before access. A symlink beneath an allowed project directory can point outside the intended sandbox; sibling paths can also share string prefixes. | Validate project IDs and enforce containment using resolved paths and path-aware comparisons, including symlink cases, before reads/writes. Add regression tests. |
| P1 / High | Live application database is tracked in Git history. | `animation_forge.db` is tracked and appears in two historical commits; `.gitignore` has no database exclusion. The current database is modified in the worktree. This can expose evolving project state to anyone receiving repository copies. | Preserve the local file; separately approve removing it from future tracking and assess historical exposure. History rewriting and remote cleanup require explicit authorization. |
| P1 / Medium | Desktop packaging did not establish a working backend lifecycle. | At audit time, `src-tauri/tauri.conf.json` listed an `externalBin`, but `src-tauri/src/main.rs` did not spawn it, and `backend/main.py` had no executable Uvicorn entry point. Production API reachability was not established. | Implement and test sidecar startup, readiness, shutdown, and production frontend connection before claiming a packaged end-to-end app. |
| P1 / Medium | Application data export/import semantics are incomplete. | `backend/database.py:611-660` exports many project tables, but import only inserts the project row and writes project files; it does not restore the exported table rows. | Specify the archive compatibility contract and implement transactional import or clearly constrain/document the format. |
| P2 / Medium | Provider, research, generation, and QC behavior is mostly simulated. | `backend/providers/manager.py:51-99,111-155` records estimates rather than invoking providers; the credential vault is in-memory (`:14-48`). ComfyUI validates/records but does not dispatch (`backend/integrations/comfyui_adapter.py:10-155`). R&D uses embedded candidates and fixed PoC data (`backend/rnd/research_engine.py:54-80,90-187,280-305`). Media generation stages synthetic PNG/WAV output; Blender/Unreal stages files without launching renders; QC checks are predeclared as passing (`backend/departments/production_studios.py`, `backend/integrations/blender_unreal_adapters.py`, `backend/qc/quality_controller.py`). MCP and StoryQuest dispatch are also simulations/local outbox behavior (`backend/integrations/mcp_gateway.py`, `backend/integrations/storyquest_connector.py`). | Keep simulated results labeled as simulated; do not report provider calls, renders, hardware checks, external MCP execution, or measured QC unless those operations are actually implemented and verified. |

## Current API surface

`backend/main.py` exposes four routes: `/api/health`, `/api/dashboard`, `/api/projects`, and `/api/approvals/decide`. All depend on the same IPC token check. The React dashboard reads health and dashboard data; the inspected `frontend/src/App.tsx` does not implement approval submission or sign-in.

## Baseline validation

- `python -m unittest discover -s TESTS -v` using the system Python could not import `jsonschema` and `yaml`.
- `.\.venv\Scripts\python.exe -m unittest discover -s TESTS -v` passed: **24 tests**.
- No remediation changes were included in that test run.

## Acceptance criteria for the authorized P0 work

1. No source/config default or committed credential can authorize API access; absent/invalid credentials fail closed.
2. The approval API cannot accept an asserted `HUMAN_` identity as proof of authentication. Approval requires trusted Windows account identity and a native confirmation; unsupported platforms fail closed.
3. Archive import rejects path traversal, absolute/drive paths, unsafe project IDs, symlink/special entries, and pre-existing targets without changing database or filesystem state.
4. Valid imports stage files safely, preserve the current accepted bundle behavior, and leave no partial project on failure.
5. Add focused regression tests and rerun the existing 24-test suite.

## CR_002 Phase 1 implementation status

- **Archive extraction:** implemented project-ID and ZIP member validation, rejects symlinks/special files and duplicate/conflicting paths, stages content before database insertion, refuses existing destinations, and cleans staged output on failure. Focused regression cases are in test 16.
- **Local IPC and desktop lifecycle:** source now has no token fallback; API requests require an environment token of at least 43 characters and an allowed browser origin. Tauri selects a loopback port, generates a 256-bit per-launch token, starts the sidecar in a process group, waits for an authenticated health response, and stops it on exit. The frontend obtains the URL/token through Tauri IPC. The ignored PyInstaller sidecar binary was not rebuilt or replaced, so these changes are not active in that existing binary until it is rebuilt.
- **Human approval:** the API no longer accepts `human_user_id`; Windows derives the reviewer from the signed-in account and displays a native confirmation for each action. Declines and non-Windows environments fail closed. The current UI does not provide a complete deliverable-inspection experience, and the native dialog confirms target identifiers and comments rather than displaying the full deliverable; this remains a review-UX limitation.
- **Path sandboxing:** `AgentExecutor` now rejects unsafe project IDs and path components (including Windows device names), resolves candidate paths before access, uses path-aware containment checks, and blocks symlinked project roots and allowed directories. Regression coverage was added for directory symlinks and unsafe path components.
- **Unresolved:** the tracked live database and its two historical revisions were not changed. The sidecar package still needs an end-to-end test: `backend/main.py` derives `ROOT_DIR` from `__file__`, while `src-tauri/tauri.conf.json` bundles the frontend and external binary but does not map `CORE/`, `SCHEMAS/`, or other runtime resources into the packaged app. Bundle import also has no archive-size or expanded-size limits.
- **Validation after these source changes:** the project virtual-environment test run passed **27 tests** with no skips; `npm run build` passed; `cargo check` passed. `cargo fmt --check` could not run because the Rust toolchain lacks the `rustfmt` component. No production binary was rebuilt or launched.

## Out of scope / requires separate authorization

- Removing `animation_forge.db` from tracking or rewriting Git history.
- Provider, research, MCP, ComfyUI, Blender/Unreal, audio, production, QC, frontend-workspace, and CI implementation milestones.
- Paid APIs, external sharing, large downloads, system-wide installation, or destructive cleanup.
