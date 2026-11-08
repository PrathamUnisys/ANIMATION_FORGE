# Developer Guide

> Build/test evidence & artifact details: **`DOCS/BUILD_AND_TEST_REPORT.md`**.

## Directory layout
- `CORE/` & `MODES/`: Versioned Markdown constitution and mode rules.
- `AGENTS/`: 16 specialized agent Markdown contracts.
- `SCHEMAS/`: 12 JSON Schemas (Draft 2020-12) validating all machine-to-machine data contracts.
- `backend/`: Modular Python packages (`governance`, `orchestration`, `providers`, `rnd`, `integrations`, `departments`, `qc`). FastAPI sidecar `backend/main.py` (default `127.0.0.1:8765`, `x-forge-token` auth).
- `src-tauri/`: Rust Tauri 2 desktop shell and sidecar bridge. `tauri.conf.json` bundles `frontend/dist` and `externalBin` sidecar `binaries/animation-forge-backend`; `build.rs` + `icons/` required for cargo/tauri build.
- `frontend/`: React + TypeScript + Tailwind (Vite). Vite dev proxies `/api` → `127.0.0.1:8765` with the local token.
- `TESTS/`: `pytest`/`unittest` suite (`test_animation_forge_suite.py`, 15 tests). `ROOT` resolved relative to the test file.

## Local dev workflow (isolated)
- Python: project `.venv` + `requirements.txt` (`fastapi, uvicorn, pydantic, jsonschema, Pillow, pytest`). Run tests via `.\.venv\Scripts\python -m pytest -q TESTS/test_animation_forge_suite.py`.
- Node: **local** `frontend/node_modules` (`npm install --no-audit --no-fund`); no global npm installs. Tauri CLI is a local devDependency (`@tauri-apps/cli`, `frontend\node_modules\.bin\tauri.cmd`).
- Generated/ignored: `.venv/`, `frontend/node_modules/`, `frontend/dist/`, `src-tauri/target/`, `src-tauri/binaries/`, `.pyi-build/`, `.pyi-spec/` (see `.gitignore`).

## Backend notes
- Datetimes are timezone-aware UTC (`datetime.now(timezone.utc)`; ISO stamps normalized to `Z`). Keep new code consistent (no `utcnow`).
- IPC: mutating/read APIs expect `x-forge-token` (`ANIMATION_FORGE_IPC_TOKEN`, default `af-local-ipc-token-2026`).

## Frontend notes
- Build: `cd frontend && npm run build` (`tsc && vite build`) → `dist/`. Dev: `npm run dev` on `127.0.0.1:1420`.
- `src/App.tsx` consumes `/api/health` + `/api/dashboard`; Vite proxy injects the token in dev. Production/Tauri wiring should source the token/config from the sidecar bridge, not the dev proxy.

## Instruction repository validation
- Governed instruction Markdown uses YAML front matter with a unique `prompt_id`, version, date, dependencies, and change history.
- After installing the project requirements, run `.\.venv\Scripts\python.exe scripts\validate_instruction_repository.py` from the repository root.
- Run its focused tests with `.\.venv\Scripts\python.exe -m pytest -q TESTS\test_instruction_repository.py`.
- The validator checks front matter, dependency references/cycles, internal Markdown links, source-to-document operation IDs, schema status mappings, agent approval/output boundaries, and audit inventory coverage. It does not execute application workflows or prove semantic consistency; review results and the audit report as well.

## Packaging notes
- Sidecar: build with venv-local PyInstaller into `src-tauri/binaries/animation-forge-backend-x86_64-pc-windows-msvc(.exe)`.
- `scripts/build_windows_installer.ps1` still references global `pyinstaller`/`npx @tauri-apps/cli@latest`; prefer the venv + local-CLI commands in `DOCS/BUILD_AND_TEST_REPORT.md`. MSI/NSIS bundles require WiX/NSIS installed.

## Adding a new agent or rule
1. Switch active mode to `ARCHITECTURE_MODE`.
2. Submit a Change Request via `GovernanceEngine.create_change_request(...)`.
3. Approve the Change Request with a `HUMAN_` reviewer ID before modifying `CORE/`, `MODES/`, or `AGENTS/`.
