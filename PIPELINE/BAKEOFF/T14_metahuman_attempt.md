# T14 — MetaHuman asset creation: headless attempt result (2026-11-09)

**Status: environment READY, asset creation GUI-BOUND (like fSpy). Verified headless probes:**

## What works headless (UnrealEditor-Cmd + PythonScriptPlugin, Library.uproject)
- `UnrealEditor-Cmd` launches the project (~45 s), Python executes, logs to file.
- 311 `MetaHuman*` Python classes present (Character, Animator, Calibration, LiveLink, Crowd).
- `MetaHumanPerformanceFactoryNew` exists with `create_new()` — the asset-creation entry point for the Audio Driven Animation track.
- `PythonScriptPlugin` + `EditorScriptingUtilities` added to `Library.uproject` (backup: `Library.uproject.bak-20261109-t14`).

## What does NOT work headless
- `MetaHumanPerformanceFactoryNew().set_editor_property("factory_name", ...)` → `Failed to find property`.
- No `EditorAssetLibrary.create_asset` in UE 5.8 Python.
- The MetaHuman **Creator** (choosing a face preset, generating mesh/grooms, optimizing LODs) has **no Python API** — it is a GUI window (`MetaHumanGenerator` subsystem). A full-fidelity MetaHuman cannot be generated headlessly.
- MovieRenderQueue / Sequencer export of an animation sequence requires the Performance asset to exist first (audio → animation).

## Prepared for the user (5-minute GUI session)
1. Open `Library.uproject` in UE 5.8 editor.
2. MetaHuman Creator → generate one MetaHuman (any preset), optimize for 8 GB VRAM.
3. MetaHuman Animator → new Performance asset, Input Type: **Audio**, import `PIPELINE/audio/test_line.wav`, Process.
4. Export the animation curves. That file is the T15b artifact.

## Staged
- Audio: `PIPELINE/audio/test_line.wav` (110 KB, same WAV used for the VRM track — like-for-like comparison).
- Scripts: `C:\Users\sb291\AppData\Local\Temp\opencode\mh_probe*.py` (probe results), `mh_create.py` (failed factory attempt, recorded).
- Memory baseline: env_guard PASS (RAM 3.89 GB, VRAM 7209 MB).

## T15c comparison (when T15b exists)
| | VRM track (T1a, proven) | MetaHuman track (T1b, pending) |
|---|---|---|
| Mouth drive | Rhubarb→Fcl_MTH_* shapes, 13 keyframes, 56 frames | MetaHuman Animator Audio Driven Animation |
| Identity across angles | perfect (rig) | perfect (rig) |
| Lip accuracy | human-scored | human-scored |
| Wall clock | ~8 min (T13+T15) | TBD |
| Peak RAM/VRAM | TBD | TBD |

The constraint is documented, not hidden: MetaHuman creation is a human step in this pipeline, same as the fSpy solve.
