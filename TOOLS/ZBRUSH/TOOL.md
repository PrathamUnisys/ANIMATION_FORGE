---
prompt_id: TOOL_ZBRUSH
version: 1.1.1
modified_date: 2026-11-09
description: Operational guide for ZBrush in Animation Forge
dependencies: ["TOOLS_INDEX"]
change_history:
  - version: 1.1.1
    date: 2026-11-09
    summary: Rename task reference to MODELING_RIGGING to match catalogue schema
  - version: 1.1.0
    date: 2026-11-09
    summary: Add ZBrush manual from disk presence
---
# Tool Manual — ZBrush

## Identity and verification

- Tool ID / name: `ZBRUSH` / ZBrush
- Category / supported tasks: SCULPT / MODELING_RIGGING
- Official site: https://www.maxon.net/en/zbrush
- Current local status: CONFIGURATION_REQUIRED
- Last verified: 2026-11-09 Test-Path folder only

## Installation and location

- Folder `C:\Program Files\Maxon ZBrush 2025\ZData\` only listed at top; full exe deeper — needs pinpoint.
- Maxon ZBrush 2025 folder name is evidence.

## Connection and configuration

- Connection type: LOCAL_PROCESS
- Health check: launch ZBrush.exe (verify path first).

## Verification history

| Date | Machine / OS | Version | Test performed | Result |
|---|---|---|---|---|
| 2026-11-09 | sb291 / Windows 11 | 2025 (folder) | Get-ChildItem Maxon ZBrush 2025 | CONFIGURATION_REQUIRED |
