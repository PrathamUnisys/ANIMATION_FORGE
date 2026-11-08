---
prompt_id: TOOL_UNREAL_ENGINE
version: 1.0.0
modified_date: 2026-11-09
description: Operational guide for locating, configuring, running and debugging Unreal Engine in Animation Forge
dependencies: ["TOOLS_INDEX", "SCHEMAS/TOOL_PROFILE.schema.json"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Add Unreal Engine operational manual with explicit local-verification boundaries
---
# Tool Manual — Unreal Engine

## Identity and purpose

Unreal Engine is a real-time 3D engine used for scene assembly, lighting, cameras, Sequencer timelines, animation, virtual production and rendering.

- **Tool ID:** `UNREAL_ENGINE`
- **Primary task tags:** `real_time_3d`, `environment_assembly`, `sequencer`, `character_animation`, `cinematography`, `rendering`
- **Official site:** https://www.unrealengine.com/
- **Documentation:** https://dev.epicgames.com/documentation/en-us/unreal-engine
- **Local status in this repository:** `NOT_VERIFIED`
- **Editor path / version / project path:** Not configured for the current machine.

## Installation and location

Use Epic Games Launcher or an installation source explicitly selected by the user. Do not assume the engine version or installation path. Record the full editor executable path and engine version after checking the launcher or installation folder.

Typical executable name on Windows: `UnrealEditor.exe`. Find the actual path through the Epic Games Launcher installation details or a filesystem search chosen by the user.

## Connection and configuration

Unreal is normally launched as a local editor or command-line process. A future adapter should use a configured engine path and project file, pass explicit command-line arguments, capture process output and enforce timeouts.

Potential invocation shape (illustrative, not a verified command for this machine):

```powershell
& "<UNREAL_EDITOR_PATH>" "<PROJECT_UPROJECT>" -log
```

The engine supports command-line arguments for unattended operation, testing and project startup. Exact switches and rendering automation must be checked against the selected engine version and installed plugins.

## How to use

1. Verify the exact engine version and project compatibility.
2. Open the target `.uproject` and confirm required plugins and content are available.
3. Build a minimal test map and Sequencer shot before importing a full episode.
4. Record project revision, engine version, plugin versions, map, Sequencer sequence, frame rate, resolution and render output.
5. Keep generated content and renders in a new project revision or draft workspace.

## Debugging

| Symptom | Diagnostic | Likely action |
|---|---|---|
| Editor path not found | Inspect launcher installation details | Update local executable path. |
| Project asks to rebuild modules | Inspect engine/project version and compile output | Match engine version and rebuild supported modules. |
| Project fails to load | Capture editor log and missing plugin list | Enable/install only required compatible plugins. |
| Sequencer renders blank | Verify map, camera binding, level visibility and sequence range | Run a short frame-range test. |
| GPU/render crash | Capture crash log and device/driver details | Test a minimal scene with supported rendering settings. |

## Known limitations

- No local Unreal Engine version, installation path, project or render has been verified by this documentation change.
- The existing Animation Forge Unreal adapter is not a verified Unreal execution adapter.
- A generated script or timeline JSON is not evidence that Unreal rendered a frame.

## Verification record

No local Unreal installation or successful render test is recorded yet. Update this section only after a real local check.
