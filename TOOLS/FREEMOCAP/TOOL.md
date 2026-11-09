---
prompt_id: TOOL_FREEMOCAP
version: 1.1.0
modified_date: 2026-11-09
description: Operational guide for FreeMoCap in Animation Forge
dependencies: ["TOOLS_INDEX"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Add FreeMoCap manual, vendor fetched
---
# Tool Manual — FreeMoCap

## Identity and verification

- Tool ID / name: `FREEMOCAP` / FreeMoCap
- Category / supported tasks: MOCAP / ANIMATION
- Official site: https://freemocap.org/ (fetched: markerless, 2+ webcams, CSV/FBX/.blend)
- Current local status: INSTALLED
- Last verified: 2026-11-09 Test-Path data folders

## Installation and location

- Data: `C:\Users\sb291\freemocap_data\logs_info_and_settings,recording_sessions`
- Companions: `C:\Users\sb291\skelly-cam-recordings`, `skellytracker_data`, `skelly_synchronize_data`, `skelly_viewer_data` (Skelly = FreeMoCap tracker)
- Installer/docs: https://docs.freemocap.org/documentation/ , code https://github.com/freemocap/freemocap

## Connection and configuration

- Connection type: LOCAL_PROCESS
- Outputs: CSV analysis, FBX + .blend for animation pipelines.

## Verification history

| Date | Machine / OS | Version | Test performed | Result |
|---|---|---|---|---|
| 2026-11-09 | sb291 / Windows 11 | UNKNOWN | Test-Path freemocap_data + vendor fetch | INSTALLED |
