# T14 — MetaHuman route: environment measurement (2026-11-09)

**Honest status: environment VERIFIED, MetaHuman asset NOT YET CREATED.**

## Verified on disk
| Item | Evidence |
|---|---|
| UE 5.8.4 | `D:\Work\Epic\UE_5.8`, Build.version `++UE5+Release-5.8`, `UnrealEditor-Cmd.exe` present |
| MetaHuman suite | `Engine/Plugins/MetaHuman/` — MetaHumanAnimator, MetaHumanCharacter, MetaHumanCoreTech, MetaHumanCrowd, LiveLink, SDK — all present |
| Project plugins | `Library.uproject` enables MetaHuman, MetaHumanCharacter, MetaHumanCrowd, MetaHumanGenerator, MetaHumanLiveLink, MetaHumanCalibrationProcessing, VRM4U (project plugin) |
| Python automation | `Engine/Plugins/Experimental/PythonScriptPlugin` exists (not enabled in Library.uproject — needs enabling for T15b scripted Audio Driven Animation) |
| VRM4U | `Library/Plugins/VRM4U` present |

## Baseline memory (measured, pre-asset)
From `scripts/pipeline/env_guard.ps1` run 2026-11-09:
- RAM free 3.89 / 11.69 GB, commit 15.07 / 24.07 GB
- VRAM free 7209 / 8188 MB (RTX 4060 Laptop, driver 621.14)
- D: 104.9 GB free

Ollama holds ~78 MB as a process but ~4 GB resident as app (per earlier session); `-StopOllama` reclaims it.

## What remains (T14 completion)
1. Create one MetaHuman asset (MetaHuman Creator, optimised LOD0 fallback=LOD2).
2. Record measured editor RAM/VRAM at viewport and at MRQ render (≥1080p, no OOM).
3. Enable PythonScriptPlugin in Library.uproject for T15b automation.

Until step 2 is recorded, do **not** claim the MetaHuman route is proven. The VRM route (T13/T15) is the proven one for the bake-off baseline.
