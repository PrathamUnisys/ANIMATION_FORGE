---
prompt_id: DOCS_BLENDER_INTEGRATION_GUIDE
version: 1.1.0
modified_date: 2026-11-09
description: Operational guide for safe Blender adapter use and capability verification.
dependencies: ["CORE_SYSTEM_CONSTITUTION", "TOOL_INTEL_TOOLCHAIN_APPROVAL", "INTEGRATION_BLENDER"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Added instruction metadata while retaining guide content
---
# Blender Adapter Status and Safe Workflow

`backend/integrations/blender_unreal_adapters.py` provides an AST denylist check, stages a sample Blender Python script under a project draft path, and writes example timeline/subtitle output after checking the animatic approval gate. The adapter does **not** launch Blender, import `bpy`, render, or verify a Blender version. Do not describe Blender 5.2 compatibility or headless execution as tested based on this code.

The AST check rejects selected imports and calls but is not a complete sandbox; it does not make arbitrary scripts safe. Inspect generated scripts and dependencies, use least privilege and an isolated environment, and preserve draft/approved asset boundaries.

Before real Blender use, verify the exact host installation/version, APIs, add-ons, render engine, codecs, license, and hardware from current official sources and local checks. Obtain human approval for the toolchain, downloads, and execution. Run a minimal test, capture actual logs/settings/results, and validate the scene/render in Blender. Human review is required before approving creative output. See `DOCS/INTEGRATIONS/BLENDER.md`.
