---
prompt_id: TOOL_ACCURIG
version: 1.1.0
modified_date: 2026-11-09
description: Operational guide for AccuRIG in Animation Forge
dependencies: ["TOOLS_INDEX"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Add AccuRIG manual from disk presence
---
# Tool Manual — AccuRIG

## Identity and verification

- Tool ID / name: `ACCURIG` / AccuRIG
- Category / supported tasks: AUTO_RIG / CHARACTER_ASSETS, 3D_MODELING_RIGGING
- Official site: https://www.reallusion.com/auto-rig/
- Current local status: INSTALLED
- Last verified: 2026-11-09 Test-Path

## Installation and location

- Installed: `C:\Program Files\AccuRIG\AccuRIG.exe` + `Assets,Common,Sample Character`
- Helpers: `ActorCoreConverterSDK.dll`, Alt installers `D:\Downloads\aco_alt_installers\aco_alt_installers.zip`

## Connection and configuration

- Connection type: LOCAL_PROCESS / MANUAL
- No HTTP. Export rigged actor + facial via ActorCore workflow.

## How to use

- Put T-pose mesh, auto-rig, cleanup, export to CC5/UE.

## Debugging and recovery

| Symptom | Likely cause | Diagnostic | Fix |
| No version in exe | Electron app | check config.json | Record UNKNOWN version |

## Verification history

| Date | Machine / OS | Version | Test performed | Result |
|---|---|---|---|---|
| 2026-11-09 | sb291 / Windows 11 | UNKNOWN | Test-Path AccuRIG.exe | INSTALLED |
