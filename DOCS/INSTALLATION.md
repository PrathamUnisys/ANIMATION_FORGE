# Installation Guide

> Verified local build/test details, evidence, and blockers: **`DOCS/BUILD_AND_TEST_REPORT.md`** (2026-11-09).

## Prerequisites
- **Windows 10 / 11 (64-bit)** (or Linux/macOS for backend/web development)
- **Python 3.11+** (verified on 3.12.3)
- **Node.js 18+ & npm 9+** (verified on Node 22.20 / npm 10.9). Frontend deps install into `frontend/node_modules` (local) — no global npm installs required.
- **Rust 1.77+ & Cargo** — only for the Tauri desktop build (verified on cargo/rustc 1.99.1).
- **For MSI/NSIS installers (optional):** WiX Toolset and/or NSIS. If absent, you can still build the release `.exe` and sidecar (see report).

## Local setup (all local environments)
```powershell
cd D:\Work\ANIMATION_FORGE

# Backend (project venv)
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt

# Frontend (local node_modules)
cd frontend
npm install --no-audit --no-fund
npm run build   # produces frontend/dist
```
> If pip hits a TLS CA/certifi path issue on your host (environment-specific), retry with `--trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org` and resolve certs.

## Running locally (dev)
Backend binds `127.0.0.1:8765` and requires header `x-forge-token: af-local-ipc-token-2026` (default). The Vite dev server proxies `/api` with that token.
```powershell
# terminal 1
cd D:\Work\ANIMATION_FORGE
.\.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8765
# terminal 2
cd D:\Work\ANIMATION_FORGE\frontend
npm run dev   # http://127.0.0.1:1420
```
- Health: `GET http://127.0.0.1:8765/api/health` with `x-forge-token`.
- Seed demo data (optional): `.\.venv\Scripts\python -c "import os,sys; os.chdir(r'D:\Work\ANIMATION_FORGE'); sys.path.insert(0,'.'); from backend.demo_project_runner import run_forgotten_kingdom_e2e_project; run_forgotten_kingdom_e2e_project('.','animation_forge.db')"` then Refresh the UI.

## Tests
```powershell
.\.venv\Scripts\python -m pytest -q TESTS/test_animation_forge_suite.py   # expected: 15 passed
```

## Desktop / sidecar (optional)
- Sidecar (venv-local PyInstaller): outputs `src-tauri/binaries/animation-forge-backend-x86_64-pc-windows-msvc.exe`.
- Tauri CLI is a local devDependency (`frontend/node_modules`, `@tauri-apps/cli`); run from `src-tauri` via `..\frontend\node_modules\.bin\tauri.cmd build` (needs WiX/NSIS for MSI/NSIS bundles). `cargo build --release` produces `src-tauri/target/release/animation-forge-desktop.exe`.
See `DOCS/BUILD_AND_TEST_REPORT.md` for exact commands and known blockers.
