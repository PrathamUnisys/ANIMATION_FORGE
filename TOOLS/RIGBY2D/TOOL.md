---
prompt_id: TOOL_RIGBY2D
version: 1.1.0
modified_date: 2026-11-09
description: Operational guide for Rigby2D in Animation Forge
dependencies: ["TOOLS_INDEX"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Add Rigby2D manual from disk presence
---
# Tool Manual — Rigby2D

## Identity and verification

- Tool ID / name: `RIGBY2D` / Rigby2D
- Category / supported tasks: SKELETAL_2D / ANIMATION
- Official site: https://github.com/ (repo in `D:\Work\Tools\rigby2d\.github`)
- Current local status: INSTALLED
- Last verified: 2026-11-09 Test-Path

## Installation and location

- Portable: `D:\Work\Rigby2D_x64_portable.exe` + source `D:\Work\Tools\rigby2d\src-tauri\` + `D:\Work\Rigby2D-Projects\`

## Connection and configuration

- Connection type: LOCAL_PROCESS (AGENTS workspace `D:\Work\Rigby2D-Projects`)
- No HTTP probe; editor reads `.rigby`/`.skel`.

## How to use

- Open `.rigby`, rig layered PSD, key bones, export `.json`/`.skel`, preview MP4.

## Verification history

| Date | Machine / OS | Version | Test performed | Result |
|---|---|---|---|---|
| 2026-11-09 | sb291 / Windows 11 | UNKNOWN | Test-Path exe + repo layout | INSTALLED |
