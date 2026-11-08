# Architecture Decision Records (ADRs)

## ADR-001: Tauri 2 + Python FastAPI Sidecar Over Electron
- **Decision**: Use [Tauri 2.0 Sidecar Architecture](https://v2.tauri.app/develop/sidecar/) paired with a local Python FastAPI daemon bound to `127.0.0.1`.
- **Rationale**: Avoids bundling a multi-hundred-megabyte Chromium binary while giving direct access to Python's AI/MCP/Blender (`bpy`)/OpenTimelineIO ecosystem.

## ADR-002: Database-Enforced Approval State Machine
- **Decision**: Enforce `PROPOSED -> GENERATING -> QUALITY_CHECK -> AWAITING_HUMAN_REVIEW -> APPROVED / REVISION_REQUESTED / REJECTED` inside `backend/governance/approval_engine.py` and SQLite triggers/checks rather than relying on LLM prompt compliance.
- **Rationale**: Guarantees that neither `QUALITY_CONTROLLER` nor `PRODUCTION_DIRECTOR` can ever mark a creative asset as `APPROVED`.

## ADR-003: Mandatory Per-Project Toolchain R&D Lock
- **Decision**: Require an approved, versioned `APPROVED_TOOLCHAIN.json` per project before unlocking downstream production tasks.
- **Rationale**: Prevents locking new 2D, 2.5D, or 3D projects into stale software stacks.
