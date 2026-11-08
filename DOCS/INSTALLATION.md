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

## Running locally (desktop dev)
The Tauri host starts the bundled backend on an available loopback port,
waits for an authenticated health response, and stops the sidecar when the
desktop app exits. It generates a fresh 256-bit IPC token for each launch;
no token is stored in the repository.

Build the sidecar after changing backend code:
```powershell
cd D:\Work\ANIMATION_FORGE
.\.venv\Scripts\pyinstaller --noconfirm --onefile --name "animation-forge-backend-x86_64-pc-windows-msvc" backend\main.py --distpath src-tauri\binaries --workpath .pyi-build --specpath .pyi-spec
```

Run the frontend dev server and Tauri host in separate terminals:
```powershell
# terminal 1
cd D:\Work\ANIMATION_FORGE\frontend
npm run dev

# terminal 2
cd D:\Work\ANIMATION_FORGE\src-tauri
..\frontend\node_modules\.bin\tauri.cmd dev
```

The packaged sidecar/runtime-resource layout has not yet been verified:
`backend/main.py` locates `CORE/`, `SCHEMAS/`, and other assets relative to its
source file, but the current Tauri bundle config does not map those resources.
Rebuild and validate the resource layout before relying on the desktop bundle.

For browser-only development, configure a cryptographically random token in
`ANIMATION_FORGE_IPC_TOKEN` for both the backend and Vite processes. Tokens
shorter than 43 characters are rejected. Do not commit the value. The backend
command is:
```powershell
.\.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8765
```

Windows approval decisions display a native confirmation containing the
project, deliverable, revision, decision, comments, and rationale. The
reviewer ID comes from the signed-in Windows account; caller-supplied reviewer
IDs are rejected. Declining the dialog leaves the approval unchanged.

## Tests
```powershell
.\.venv\Scripts\python -m pytest -q TESTS/test_animation_forge_suite.py   # expected: 18 passed
.\.venv\Scripts\python -m pytest -q TESTS/test_instruction_repository.py
.\.venv\Scripts\python scripts\validate_instruction_repository.py
```

## Desktop / sidecar (optional)
- The optional demo runner prompts for native Windows confirmation at each
  approval, PoC, toolchain, and example-plugin authorization gate.
- Sidecar (venv-local PyInstaller): outputs `src-tauri/binaries/animation-forge-backend-x86_64-pc-windows-msvc.exe`.
- Tauri CLI is a local devDependency (`frontend/node_modules`, `@tauri-apps/cli`); run from `src-tauri` via `..\frontend\node_modules\.bin\tauri.cmd build` (needs WiX/NSIS for MSI/NSIS bundles). `cargo build --release` produces `src-tauri/target/release/animation-forge-desktop.exe`.
See `DOCS/BUILD_AND_TEST_REPORT.md` for exact commands and known blockers.
