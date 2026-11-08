# System Architecture Follows Strict Three-Tier Desktop Separation

## 1. Responsibility Boundaries
- **Tauri 2 / Rust Layer (`src-tauri/`)**: Manages Windows process lifecycle, spawns the Python FastAPI sidecar binary (`binaries/animation-forge-backend`), injects a per-session IPC bearer token (`X-Forge-Token`), and handles native file dialogs.
- **React / TypeScript Layer (`frontend/`)**: Implements the 13 studio modules (Dashboard, Projects, Creative Studio, Production Pipeline, R&D Lab, Toolchain Manager, Integration Manager, Asset Library, Review Studio, Quality Control, Agent Workshop, Creative Memory, System Configuration).
- **Python / FastAPI Layer (`backend/`)**: Executes the 8-tier Governance Rule Loader, 16 specialized AI agents, Provider-Agnostic R&D Engine, MCP Client/Server Gateway, ComfyUI/Blender/Unreal adapters, 5-stage QC Engine, and SQLite persistence.

## 2. Local-First Offline Operation
Projects, Markdown rules, Story Bibles, approved assets, and revision history reside on the local filesystem (`PROJECTS/<ID>/`) and inside `animation_forge.db`, allowing full inspection, editing, and review with zero internet connectivity.
