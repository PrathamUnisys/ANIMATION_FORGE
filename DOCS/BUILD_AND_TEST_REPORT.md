# Animation Forge — Local Build, Test & Packaging Report

**Date:** 2026-11-09 02:02 +05:30  
**Scope:** (A) backend + frontend + tests in fully local environments (no global npm installs; Python deps in project venv), plus (B/partial) sidecar + Tauri desktop release binary and code-quality fixes.  
**Workspace:** `D:\Work\ANIMATION_FORGE` (not a git repo).  
**Host/tooling observed:** Windows (win32), Python **3.12.3**, Node **v22.20.0**, npm **10.9.3**, Rust/cargo **1.99.1** (`rustc 1.99.1`).

> This is a historical build report from before approved `CR_001`; the health
> smoke test below observed `ARCH_V1.0.0`. Instruction-authoring and current
> repository validation results are tracked in
> [INSTRUCTION_REPOSITORY_AUDIT.md](./INSTRUCTION_REPOSITORY_AUDIT.md).
> The token, API, and sidecar behavior described below predates CR_002. The
> current security baseline and remediation status are in
> [ENGINEERING_REMEDIATION_BASELINE.md](./ENGINEERING_REMEDIATION_BASELINE.md);
> do not use the historical fixed-token instructions as current setup guidance.

## Summary (outcome)
| Area | Status | Evidence |
|---|---|---|
| Backend local env | **Done** | `.venv` + `requirements.txt`; imports OK |
| Backend tests | **Done** | `pytest -q TESTS/test_animation_forge_suite.py` → **15 passed, 0 warnings** (after `utcnow` fix) |
| Backend smoke | **Done** | `GET /api/health` (token `af-local-ipc-token-2026`) → **200 healthy**, `ARCH_V1.0.0`, DB integrity OK, 38 tables |
| Frontend deps (local) | **Done** | 138 packages in `frontend/node_modules` via `npm install --no-audit --no-fund` (no global installs) |
| Frontend build | **Done** | `npm run build` (`tsc && vite build`) → **35 modules, built**, `frontend/dist/` produced |
| Demo data | **Done (optional)** | `run_forgotten_kingdom_e2e_project` seeded `PROJECT_001` “The Forgotten Kingdom”; dashboard non-empty |
| `utcnow` deprecations | **Done** | 0 `utcnow` hits remaining in `backend/`; tests now **0 warnings** |
| PyInstaller sidecar (venv-local) | **Done** | `src-tauri/binaries/animation-forge-backend-x86_64-pc-windows-msvc.exe` (16,476,108 B) |
| Tauri desktop release exe | **Done** | `cargo build --release` → `src-tauri/target/release/animation-forge-desktop.exe` (8,745,472 B) |
| Tauri MSI/NSIS bundles | **Blocked** | No WiX (`candle/light`)/NSIS (`makensis`)/`wix` and no `winget` on host; `bundle/` not produced |

## What changed (files)

### Modified
- `TESTS/test_animation_forge_suite.py:10-11` — replaced hardcoded `ROOT = "/working_dir/.../ANIMATION_FORGE"` with `os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))` for local/portable runs.
- `src-tauri/tauri.conf.json` — `build.beforeDevCommand/beforeBuildCommand` adjusted to run from the correct directory (`cmd /c npm --prefix ..\frontend run dev|build`) to avoid root `package.json` lookup; for the final `--no-bundle` cargo build these were removed (kept `devUrl` + `frontendDist: ../frontend/dist`). `bundle.targets` remain `["msi","nsis"]`, `externalBin: ["binaries/animation-forge-backend"]`.
- `backend/**/*.py` (14 files) — replaced deprecated `datetime.utcnow()` with timezone-aware UTC:
  - `datetime.now(timezone.utc).isoformat().replace("+00:00","Z")` for ISO stamps,
  - `datetime.now(timezone.utc).strftime(...)` for formatted stamps,
  - `datetime.now(timezone.utc).timestamp()` for numeric IDs.
  - Added `timezone` import where needed. Files: `backend/database.py`, `backend/main.py`, `backend/demo_project_runner.py`, `backend/departments/production_studios.py`, `backend/departments/story_pipeline.py`, `backend/governance/approval_engine.py`, `backend/governance/rule_loader.py`, `backend/integrations/comfyui_adapter.py`, `backend/integrations/mcp_gateway.py`, `backend/integrations/plugin_manager.py`, `backend/orchestration/agent_executor.py`, `backend/providers/manager.py`, `backend/qc/quality_controller.py`, `backend/rnd/research_engine.py`.
- `DOCS/INSTALLATION.md`, `DOCS/DEVELOPER_GUIDE.md` — updated to reflect local env/build/test reality and this report.

### Added
- `requirements.txt` — backend/test deps (pinned ranges): `fastapi>=0.115,<1`, `uvicorn>=0.30,<1`, `pydantic>=2.7,<3`, `jsonschema>=4.22,<5`, `Pillow>=10.3,<12`, `pytest>=8.2,<9`, `PyYAML>=6,<7` (used by the instruction repository validator).
- `.gitignore` — `.venv/`, `frontend/node_modules/`, `frontend/dist/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`, `src-tauri/target/`, `src-tauri/binaries/`, `.pyi-build/`, `.pyi-spec/`, `*.spec`.
- `frontend/` scaffolding (was missing; required by `package.json` scripts and Tauri `frontendDist`): `index.html` (entry `/src/main.tsx`), `src/main.tsx`, `src/index.css` (Tailwind), `vite.config.ts` (React plugin; dev `127.0.0.1:1420`, strict; **proxy `/api` → `127.0.0.1:8765` with `x-forge-token` header** for local dev), `tsconfig.json`, `tsconfig.node.json`, `tailwind.config.js`, `postcss.config.js`. Existing `frontend/src/App.tsx` and `frontend/src/store/useForgeStore.ts` retained; `App.tsx` wired to fetch `/api/health` + `/api/dashboard` and render status/nav/counts/JSON.
- `src-tauri/build.rs` — `fn main(){ tauri_build::build(); }` (required; `cargo build` failed with `OUT_DIR env var is not set` without it).
- `src-tauri/icons/icon.ico` — minimal generated icon (build prerequisite).
- `frontend` devDependency: `@tauri-apps/cli@2` (local, `tauri-cli 2.12.4`), used instead of global `npx @tauri-apps/cli@latest`.

## Reproducible steps (PowerShell, all local)

### 1) Backend — project venv
```powershell
cd D:\Work\ANIMATION_FORGE
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip --disable-pip-version-check
.\.venv\Scripts\python -m pip install -r requirements.txt --disable-pip-version-check
# if TLS CA path issues occur in your environment: add --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org
.\.venv\Scripts\python -c "import fastapi,uvicorn,pydantic,jsonschema,PIL,pytest; print('imports_ok')"
```

### 2) Tests (backend)
```powershell
.\.venv\Scripts\python -m pytest -q TESTS/test_animation_forge_suite.py
# expected: 15 passed
.\.venv\Scripts\python -m pytest -q TESTS/test_instruction_repository.py
.\.venv\Scripts\python scripts\validate_instruction_repository.py
```

### 3) Frontend — local node_modules (no global npm installs)
```powershell
cd frontend
npm install --no-audit --no-fund
npm run build   # tsc && vite build -> frontend/dist
```

### 4) Run locally (dev)
```powershell
# terminal 1 — backend (requires x-forge-token header; default af-local-ipc-token-2026)
cd D:\Work\ANIMATION_FORGE
.\.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8765
# terminal 2 — frontend dev (proxies /api to 8765 with token)
cd D:\Work\ANIMATION_FORGE\frontend
npm run dev   # http://127.0.0.1:1420
```
Open http://127.0.0.1:1420. Stop: kill listeners on 8765/1420.

### 5) Seed demo data (optional)
```powershell
.\.venv\Scripts\python -c "import os,sys; os.chdir(r'D:\Work\ANIMATION_FORGE'); sys.path.insert(0,'.'); from backend.demo_project_runner import run_forgotten_kingdom_e2e_project; run_forgotten_kingdom_e2e_project('.','animation_forge.db')"
```
Seeds `PROJECT_001` “The Forgotten Kingdom” (approvals/assets/toolchain/integration/decisions/QC). Click Refresh in UI.

### 6) PyInstaller sidecar (venv-local) for Tauri
```powershell
.\.venv\Scripts\python -m pip install pyinstaller --disable-pip-version-check
.\.venv\Scripts\pyinstaller --noconfirm --onefile --name "animation-forge-backend-x86_64-pc-windows-msvc" backend/main.py --distpath src-tauri/binaries --workpath .pyi-build --specpath .pyi-spec
# output: src-tauri/binaries/animation-forge-backend-x86_64-pc-windows-msvc.exe
```
> `tzdata` hidden-import warning observed (non-fatal in this build).

### 7) Tauri desktop binary / installers
```powershell
# frontend build must exist (step 3) and sidecar exe present (step 6)
cd frontend; npx --no-install tauri --version   # tauri-cli 2.12.4 (local)
cd ..\src-tauri
cargo build --release   # => target/release/animation-forge-desktop.exe (verified)
# Bundles (MSI/NSIS) — requires WiX Toolset and/or NSIS installed:
..\frontend\node_modules\.bin\tauri.cmd build   # => target/release/bundle/
```

## Verification evidence (observed)
- Imports (venv): `fastapi,uvicorn,pydantic,jsonschema,PIL,pytest` → `imports_ok`.
- Tests: **`15 passed in 1.42s`** (post-fix; pre-fix 15 passed / 85 `utcnow` DeprecationWarnings).
- API smoke: `GET /api/health` → `{"status":"healthy","architecture_version":"ARCH_V1.0.0","database_integrity":{"ok":true,"table_count":38},"bound_interface":"127.0.0.1"}`.
- Demo seed: inserted 1 project, 15 approvals, 4 assets, 1 locked toolchain, 1 integration, 8 decisions, 5 QC reports (verified via `/api/dashboard`).
- Frontend: Vite **35 modules** → `frontend/dist/index.html` + hashed assets.
- Artifacts: `src-tauri/binaries/animation-forge-backend-x86_64-pc-windows-msvc.exe` (16.5 MB), `src-tauri/target/release/animation-forge-desktop.exe` (8.7 MB). No `src-tauri/target/release/bundle/` (installers blocked).

## Known issues / blockers
1. **MSI/NSIS installers blocked:** WiX (`candle`/`light`), NSIS (`makensis`), `wix` CLI, and `winget` not found on host; bundle targets `msi,nsis` cannot be produced until those are installed.
2. **Tauri config vs repo layout:** original config assumed repo-root `npm` and a packaged sidecar; fixed to `frontend`-scoped commands and local CLI. `scripts/build_windows_installer.ps1` still uses global `pyinstaller` and `npx @tauri-apps/cli@latest` — prefer the venv/local-CLI steps above for reproducibility.
3. **`cargo tauri` subcommand not installed globally** (expected); use local `frontend\node_modules\.bin\tauri.cmd` or `cargo install tauri-cli`.
4. **PyInstaller `tzdata` hidden-import warning** (non-fatal) — revisit if timezone data is needed at runtime in the frozen exe.
5. **Pip TLS CA quirk (this host):** after `pip` self-upgrade, `certifi/cacert.pem` path under venv caused install failure; `--trusted-host` to PyPI hosts was used. Treat as environment-specific; verify in clean envs.
6. **Dev servers may be left running** on `8765/1420` if started during verification; stop listeners before re-running on same ports.

## Rollback
- Remove local artifacts (gitignored): `.venv/`, `frontend/node_modules/`, `frontend/dist/`, `src-tauri/target/`, `src-tauri/binaries/`, `.pyi-build/`, `.pyi-spec/`.
- Revert code/config if undesired: `TESTS/test_animation_forge_suite.py` (ROOT), `backend/*` (utcnow → prior form), `src-tauri/tauri.conf.json`, `frontend/src/App.tsx` & `vite.config.ts`, and delete added files (`requirements.txt`, `.gitignore`, `frontend/{index.html,src/main.tsx,src/index.css,vite.config.ts,tsconfig*.json,tailwind.config.js,postcss.config.js}`, `src-tauri/build.rs`, `src-tauri/icons/`, `DOCS/BUILD_AND_TEST_REPORT.md`).

## Notes
- This is a local/dev build report; Tauri `security.csp` allows `http://127.0.0.1:8765`. The Vite dev proxy injects the local IPC token for `/api` — **dev convenience only**, not for production exposure.
- `animation_forge.db` may be modified by seeding/runs; treat as local state.

## CR_002 current source validation (2026-11-09)

- Added ZIP project-bundle path validation and staging, resolved-path sandbox checks, per-launch Tauri IPC tokens and loopback ports, fail-closed API token/origin checks, authenticated sidecar readiness/shutdown, and signed-in Windows reviewer confirmation.
- Current Python regression run: **27 passed**. API auth was also smoke-tested through Uvicorn using a temporary database; the live `animation_forge.db` was not used for the smoke test.
- `npm run build` passed; `cargo check` passed.
- `cargo fmt --check` could not run because `rustfmt` is not installed for the active Rust toolchain.
- The ignored PyInstaller sidecar artifact was not rebuilt or replaced. Rebuild it from the updated source before testing the Tauri desktop flow. Packaged application-resource discovery remains an open verification item.
