---
prompt_id: TOOL_QUICKSEL_BRIDGE
version: 1.1.0
modified_date: 2026-11-09
description: Operational guide for Quixel Bridge in Animation Forge
dependencies: ["TOOLS_INDEX"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Add Quixel Bridge manual, Bridge mystery logged
---
# Tool Manual — Quixel Bridge

## Identity and verification

- Tool ID / name: `QUICKSEL_BRIDGE` / Quixel Bridge
- Category / supported tasks: ASSET_BROWSER / CHARACTER_ASSETS, ENVIRONMENT_ASSETS
- Official site: https://www.quixely.com/
- Current local status: CONFIGURATION_REQUIRED
- Last verified: 2026-11-09 Test-Path

## Installation and location

- Folder `C:\Program Files\Bridge\` exists but 0 files at depth 1-2. Project folder `D:\Work\Quxeil Bridge\New folder\` almost empty.
- Megascans library NOT located yet — likely `D:\Library`, `D:\Content Creation\Material`, or AppData.

## Connection and configuration

- Connection type: LOCAL_PROCESS
- Needs real Bridge exe path before live use.

## How to use

- Browse Megascans, export to UE/Blender via Bridge settings.

## Debugging and recovery

| Symptom | Likely cause | Diagnostic | Fix |
| Bridge empty | Shim / uninstalled | Recurse search for Bridge.exe, check Epic Vault | Reinstall Bridge from Epic launcher |

## Verification history

| Date | Machine / OS | Version | Test performed | Result |
|---|---|---|---|---|
| 2026-11-09 | sb291 / Windows 11 | UNKNOWN | Test-Path + Get-ChildItem Bridge | CONFIGURATION_REQUIRED |
