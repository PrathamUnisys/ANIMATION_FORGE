---
prompt_id: TOOL_BLENDER
version: 1.1.0
modified_date: 2026-11-09
description: Operational guide for Blender in Animation Forge (verified 5.2.1 LTS)
dependencies: ["TOOLS_INDEX", "SCHEMAS/TOOL_PROFILE.schema.json"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Verified 5.2.1 LTS, GPU 8GB, +3 free extensions (Bool Tool, Mio3 UV, Texel Density), Hair brush incompat noted
  - version: 1.0.0
    date: 2026-11-09
    summary: Add Blender operational manual with explicit local-verification boundaries
---
# Tool Manual — Blender

## Identity and purpose

Blender is a desktop 3D creation application used for modeling, rigging, materials, animation, lighting, rendering and compositing.

- **Tool ID:** `BLENDER`
- **Primary task tags:** `3d_modeling`, `rigging`, `character_animation`, `camera_animation`, `rendering`, `compositing`
- **Official site:** https://www.blender.org/
- **Manual:** https://docs.blender.org/manual/en/latest/
- **Local status in this repository:** `INSTALLED` (Blender 5.2.1 LTS + 13 user_default extensions)
- **Executable path / version:** `D:\Program Files\BlenderFoudation\blender.exe` — **5.2.1 LTS** (build 2026-08-25) + RTX 4060 Laptop GPU 8GB for Cycles (GPU available, CPU-only addons still fine)

## Installation and location

Install from the official Blender download page or a trusted package manager selected by the user. Do not assume the default Windows path. Discover the executable by checking the Start Menu shortcut, installed application path, or a configured executable path.

Verify from PowerShell:

```powershell
where.exe blender
blender --version
```

If the command is not on PATH, record the actual executable path in local tool configuration. Do not write the machine-specific path into this shared manual.

## Connection and configuration

Blender is normally invoked as a local process, not through a persistent network daemon. A future adapter should launch the configured executable with an explicit project file, background mode where appropriate, script path, output directory and timeout.

Example capability check:

```powershell
blender --background --python-expr "import bpy; print(bpy.app.version_string)"
```

Expected evidence is a process exit code of zero and a Blender version printed to stdout. This command has not been run by this architecture change.

For unattended production, capture stdout/stderr, process exit code, elapsed time, generated files and hashes. Blender's command-line argument order matters; set output and render arguments after loading the scene file when required by the chosen version.

## How to use

1. Verify the approved Blender version and project toolchain.
2. Open or create a draft `.blend` file in the active project's allowed workspace.
3. Run a minimal scene setup or render test before a full production task.
4. Record Blender version, scene file, script hash, render engine, resolution, frame range, samples and output paths.
5. Save new revisions rather than overwriting approved assets.

## Debugging

| Symptom | Diagnostic | Likely action |
|---|---|---|
| `blender` not found | `where.exe blender` | Configure the actual executable path or PATH entry. |
| Background process exits early | Capture stdout/stderr and exit code | Check script traceback, missing add-ons and project paths. |
| GPU render falls back or fails | Run a minimal render and inspect Blender system info | Check driver, supported backend and device selection. |
| Missing Python module | Run the script in Blender's bundled Python context | Install only supported dependencies in the intended Blender environment. |
| File cannot be saved | Verify output directory and permissions | Use a project draft directory and unique revision filename. |

## Known limitations

- Hair brush 3D extension declares max Blender 5.0.99 — incompatible with 5.2.1 (enable will warn). No render test has run yet beyond Boolean modifier headless check.
- `gemini-code-1782452287130.py` legacy addon missing `bl_info`.
- The existing Animation Forge Blender/Unreal adapter writes demonstration files; it does not prove that Blender was launched or a render completed.

## Verification record

Verified 2026-11-09 headless Blender 5.2.1 LTS:
- `blender --background` starts, Fab + BlenderMCP registered (MCP cannot start in background mode by design — GUI only).
- Boolean modifier test: cube + cutter DIFFERENCE → `BOOLEAN OK Bool Cube` (no GPU crash).
- 2026-11-09 installed free extensions `user_default`: `bool_tool` 2.1.0, `mio3_uv` 2.2.0, `texel_density_checker` 2026.1.1 (all `STATUS Installed`) — extend `user_default` from 10 → 13 folders.
- `scripts/optimize_generated_glb.py` tested: tile-high.glb 12→12 tris (18.5 KB FBX) + CC Base.fbx 17,683 tris (shape-key meshes SKIPPED: CC_Base_Body/Tongue/TearLine/Eye) — decimate present for non-facial meshes.
