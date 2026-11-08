# Developer Guide

> Build/test evidence & artifact details: **`DOCS/BUILD_AND_TEST_REPORT.md`**.

## Directory layout
- `CORE/` & `MODES/`: Versioned Markdown constitution and mode rules.
- `GENRES/`: Reusable versioned genre instructions and genre registry.
- `STYLES/`: Separate versioned style guides and registry for each publishing channel.
- `TOOLS/`: Per-tool manuals plus a task/tag-based tool catalogue; availability is verified separately from adapter maturity.
- `LIBRARY/`: Asset metadata index, controlled tag taxonomy and configurable storage-root references; binary assets are stored outside Git.
- `AGENTS/`: 16 specialized agent Markdown contracts.
- `SCHEMAS/`: JSON Schemas (Draft 2020-12) validating machine-to-machine data contracts, including genre/style registries, tool catalogue, asset index and screenplay context manifest.
- `backend/`: Modular Python packages (`governance`, `orchestration`, `providers`, `rnd`, `integrations`, `departments`, `qc`). FastAPI binds to loopback (port 8765 in standalone development) and requires a strong `x-forge-token`.
- `src-tauri/`: Rust Tauri 2 desktop shell selects a loopback port, launches and monitors the bundled `externalBin` backend, creates a per-launch IPC token, waits for authenticated readiness, and stops the sidecar on exit.
- `frontend/`: React + TypeScript + Tailwind (Vite). Tauri uses the sidecar connection returned over Tauri IPC; the Vite proxy injects a token only when configured in the local environment.
- `TESTS/`: `pytest`/`unittest` suite (`test_animation_forge_suite.py`, 18 tests). `ROOT` resolved relative to the test file.

## Local dev workflow (isolated)
- Python: project `.venv` + `requirements.txt` (`fastapi, uvicorn, pydantic, jsonschema, Pillow, pytest`). Run tests via `.\.venv\Scripts\python -m pytest -q TESTS/test_animation_forge_suite.py`.
- Node: **local** `frontend/node_modules` (`npm install --no-audit --no-fund`); no global npm installs. Tauri CLI is a local devDependency (`@tauri-apps/cli`, `frontend\node_modules\.bin\tauri.cmd`).
- Generated/ignored: `.venv/`, `frontend/node_modules/`, `frontend/dist/`, `src-tauri/target/`, `src-tauri/binaries/`, `.pyi-build/`, `.pyi-spec/` (see `.gitignore`).
- Screenplay context contract: `DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md`; current `StoryAndScreenplayPipeline` still does not implement it.
- Project selectors: `primary_genre_id`, `secondary_genre_ids`, and optional `channel_style_id` are defined in `SCHEMAS/PROJECT.schema.json`; database migration and UI support remain future work.

## Backend notes
- Datetimes are timezone-aware UTC (`datetime.now(timezone.utc)`; ISO stamps normalized to `Z`). Keep new code consistent (no `utcnow`).
- IPC: mutating/read APIs require `ANIMATION_FORGE_IPC_TOKEN` of at least 43 characters; there is no fallback. Tauri generates a fresh 256-bit token for its sidecar. Browser-only development must configure one in both processes.
- Approval API: reviewer identity is derived from the signed-in Windows account and each decision requires a native confirmation. No caller-supplied `HUMAN_` value is treated as authentication.

## Frontend notes
- Build: `cd frontend && npm run build` (`tsc && vite build`) → `dist/`. Dev: `npm run dev` on `127.0.0.1:1420`.
- `src/App.tsx` consumes `/api/health` + `/api/dashboard`; Tauri obtains the per-launch URL/token through the registered host command. Browser dev uses the Vite proxy.

## Instruction repository validation
- Governed instruction Markdown uses YAML front matter with a unique `prompt_id`, version, date, dependencies, and change history.
- After installing the project requirements, run `.\.venv\Scripts\python.exe scripts\validate_instruction_repository.py` from the repository root.
- Run its focused tests with `.\.venv\Scripts\python.exe -m pytest -q TESTS\test_instruction_repository.py`.
- The validator checks front matter, dependency references/cycles, internal Markdown links, source-to-document operation IDs, schema status mappings, agent approval/output boundaries, and audit inventory coverage. It does not execute application workflows or prove semantic consistency; review results and the audit report as well.

## Packaging notes
- Sidecar: rebuild with venv-local PyInstaller into `src-tauri/binaries/animation-forge-backend-x86_64-pc-windows-msvc(.exe)` after backend changes; the Tauri host launches this artifact and uses a process group so the one-file PyInstaller child is stopped on exit.
- Runtime resources: packaged startup is not yet verified. The backend derives its root from `__file__`, while `tauri.conf.json` does not yet map `CORE/`, `SCHEMAS/`, and related files into the bundle.
- `scripts/build_windows_installer.ps1` still references global `pyinstaller`/`npx @tauri-apps/cli@latest`; prefer the venv + local-CLI commands in `DOCS/BUILD_AND_TEST_REPORT.md`. MSI/NSIS bundles require WiX/NSIS installed.

## Adding a new agent or rule
1. Switch active mode to `ARCHITECTURE_MODE`.
2. Submit a Change Request via `GovernanceEngine.create_change_request(...)`.
3. Approve the Change Request with a `HUMAN_` reviewer ID before modifying `CORE/`, `MODES/`, or `AGENTS/`.
