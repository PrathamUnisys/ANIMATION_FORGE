---
prompt_id: INTEGRATION_BLENDER
version: 1.0.0
modified_date: 2026-11-09
description: Safe workflow guidance for Blender scene and animation tooling.
dependencies: ["TOOL_INTEL_POC", "TOOL_INTEL_TOOLCHAIN_APPROVAL"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial Blender integration guidance
---
# Blender Integration

## Status
The current `SafeBlenderAndUnrealAdapter` validates a fixed Python script with an AST denylist, writes a sample Blender script under a project draft path, and emits example timeline/subtitle files after an animatic approval gate (`backend/integrations/blender_unreal_adapters.py`). It does **not** launch Blender, import `bpy`, render, or verify a Blender installation/version. AST checks are not a complete sandbox and do not establish script safety.

## Operational procedure
- Confirm exact Blender version/build, add-ons, OS, Python/API compatibility, hardware, render engine, codecs, and licensing from official current sources and the target installation.
- Obtain human approval for the project toolchain and any script execution/download. Back up work and operate in isolated draft files; never overwrite approved scenes.
- Inspect scripts and dependencies manually; use least privilege and a restricted environment. AST validation is only one screening layer.
- Run a minimal approved scene test using the real Blender executable, capture command/version/logs, render settings, resource use, and output. Mark unsupported/unrun behavior as planned.
- Validate the resulting `.blend`, rendered frames, timing, and creative intent in Blender and by human review before promotion.

Do not claim headless rendering or Blender 5.2 compatibility based only on the adapter's sample script. Application-level creative approval remains required.
