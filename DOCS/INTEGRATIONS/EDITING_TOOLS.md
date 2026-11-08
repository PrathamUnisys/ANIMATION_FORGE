---
prompt_id: INTEGRATION_EDITING_TOOLS
version: 1.0.0
modified_date: 2026-11-09
description: Interoperability and approval guidance for editing applications.
dependencies: ["TOOL_INTEL_REQUIREMENTS", "TOOL_INTEL_TOOLCHAIN_APPROVAL"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial editing tools guidance
---
# Editing Tools

## Status
The inspected adapter writes a JSON object labeled OpenTimelineIO-compatible and an SRT file as sample outputs; it does not invoke an editor, validate OTIO against the official schema, or render/export a master (`backend/integrations/blender_unreal_adapters.py`). Treat application handoff and editing software connections as guidance/planned unless separately verified.

## Interchange and application checks
Choose the target editor only after checking current official import/export documentation, OTIO or interchange version, media codecs, color/audio settings, subtitle format, timebase, and round-trip limitations. Mark community importers and experimental features clearly. Keep an unmodified source project and versioned draft exports.

Validate actual interchange in the target application: open/import, inspect media links, frame rate/timecode, duration, transitions, audio sync, subtitles, color, and export settings. Record application version, warnings, test file hashes, and measured export results. A valid JSON/SRT file is not proof of a functioning timeline or playable master.

Require human approval for software/toolchain selection, media use, paid services, and final creative deliverables. Perform visual/audio QC and human playback review before delivery; documentation and automated checks cannot replace them.
