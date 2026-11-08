---
prompt_id: TOOL_BLENDER
version: 1.0.0
modified_date: 2026-11-09
description: Operational guide for locating, configuring, running and debugging Blender in Animation Forge
dependencies: ["TOOLS_INDEX", "SCHEMAS/TOOL_PROFILE.schema.json"]
change_history:
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
- **Local status in this repository:** `NOT_VERIFIED`
- **Executable path / version:** Not yet configured for the current machine.

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

- Blender installation, version, GPU support and add-ons are not verified on the current machine.
- The existing Animation Forge Blender/Unreal adapter writes demonstration files; it does not prove that Blender was launched or a render completed.
- AST inspection of a Python script is not a security sandbox. Any future script execution needs a separate, restricted execution design.

## Verification record

No local Blender version or successful render test is recorded yet. Update this section only after a real local check.
