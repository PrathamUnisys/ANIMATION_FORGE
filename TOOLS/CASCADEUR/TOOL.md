---
prompt_id: TOOL_CASCADEUR
version: 1.1.0
modified_date: 2026-11-09
description: Operational guide for Cascadeur in Animation Forge
dependencies: ["TOOLS_INDEX"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Add Cascadeur manual from disk verification 2026.1.2
---
# Tool Manual — Cascadeur

## Identity and verification

- Tool ID / name: `CASCADEUR` / Cascadeur
- Category / supported tasks: CHAR_ANIM / ANIMATION, CHARACTER_ASSETS
- Official site: https://www.cascadeur.com/
- Current local status: INSTALLED
- Last verified: 2026-11-09 PowerShell FileVersion

## Installation and location

- Installed: `C:\Program Files\Cascadeur\cascadeur.exe` (2026.1.2.0.15343) + `C:\Program Files\CascadeurOriginal\`
- Version check: `cascadeur.exe` FileVersion; LiveLink DLLs `UnrealLiveLink.dll`, `tool_ue_live_link.dll` present.
- Prerequisites: NVIDIA/AMD GPU, FBX/USD export.

## Connection and configuration

- Connection type: LOCAL_PROCESS (Unreal Live Link optional)
- No persistent HTTP endpoint. Use File > Export FBX or Live Link to UE.
- Health check: launch exe, open `D:\Library\Cascadeur\Maximo_model.casc`.

## How to use

- Import FBX rig, pose with physics, fix feet, export FBX/BVH to `D:\Content Creation\Mocap\` or UE.

## Debugging and recovery

| Symptom | Likely cause | Diagnostic | Fix |
| Phrase "Cascadeur" missing | PATH not set | Test-Path exe | Launch by full path |

## Limits and operational notes

- Not metered as MCP; no headless API documented in catalog yet.
- Live Link needs UE plugin compatible with installed UE version.

## Verification history

| Date | Machine / OS | Version | Test performed | Result |
|---|---|---|---|---|
| 2026-11-09 | sb291 / Windows 11 | 2026.1.2.0.15343 | FileVersion on cascadeur.exe | INSTALLED |
