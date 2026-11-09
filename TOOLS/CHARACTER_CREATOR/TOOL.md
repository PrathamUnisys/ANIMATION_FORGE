---
prompt_id: TOOL_CHARACTER_CREATOR
version: 1.1.0
modified_date: 2026-11-09
description: Operational guide for Character Creator 5 in Animation Forge
dependencies: ["TOOLS_INDEX"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Add Character Creator 5 manual, verified 5.12.1927.1
---
# Tool Manual — Character Creator 5

## Identity and verification

- Tool ID / name: `CHARACTER_CREATOR` / Character Creator 5
- Category / supported tasks: CHAR_GEN / CHARACTER_ASSETS
- Official site: https://www.reallusion.com/
- Current local status: INSTALLED
- Last verified: 2026-11-09 PowerShell FileVersion

## Installation and location

- Installed: `C:\Program Files\Reallusion\Character Creator 5\Bin64\CharacterCreator.exe` (5.12.1927.1)
- Libraries: `D:\Work\Reallusion Custom\Accessory,Actor,Hair,Props,Set…`, `D:\Work\Reallision\Reallusion Templates`
- Pipeline: `D:\Downloads\Plugins\Blender_Pipeline_Plugin_for_CC5_Hub.exe`, `cc_blender_tools-2_3_2.zip`

## Connection and configuration

- Connection type: LOCAL_PROCESS / PLUGIN (Blender Pipeline Plugin, Auto Setup to UE)
- No HTTP. Export FBX/USD + export profiles `D:\Library\CC to Blender\Base.3dxProfile`

## How to use

- Create CC5 character, export to Blender via CC5 Hub, or to UE via Auto Setup `Character_Creator_and_iClone_Auto_Setup_201_0317_for_Unreal.exe`.

## Debugging and recovery

| Symptom | Likely cause | Diagnostic | Fix |
| Bridge empty | Bridge not installed | Test-Path Bridge exe | Resolve Quixel Bridge separately |

## Limits and operational notes

- iClone app not installed — CC5-only right now, confirm where iClone lives if needed.
- HeadShot 300 plugin installer in Downloads (`Headshot_300_0505_Plugin_for_CC5_Full pinocchio vfxMed.rar`).

## Verification history

| Date | Machine / OS | Version | Test performed | Result |
|---|---|---|---|---|
| 2026-11-09 | sb291 / Windows 11 | 5.12.1927.1 | FileVersion CharacterCreator.exe | INSTALLED |
