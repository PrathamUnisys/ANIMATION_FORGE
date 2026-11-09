# VRM RIG POC — Proof of Concept Folder

**Created:** 2026-11-09 · **Targets:** UE 5.8 @ `D:\Work\Epic\UE_5.8` · Blender 5.2 + VRM 4.10.4 + Faceit 2.3.65
**Research:** `PIPELINE/VRM_UNREAL_RESEARCH.md` (feasibility, A/B/C, Sequencer Option 1)

## Goal

Prove: **one VRM → one UE SkeletalMesh** with **independent** body + face animation in Sequencer (walk + turn + blink + mouth + smile + talk), automated headless as far as possible.

## Milestone plan (from research §8)

| # | Milestone | Status | Evidence required |
|---|---|---|---|
| M1 | Import + bone/expression map | **DONE** — `outputs/M1_redhairgirl.json` (225 bones, 57 shape keys; Blender 5.2.1 LTS headless, import `FINISHED`; see `IMPORT_REPORT.md`) | Re-run `vrm_inspect.py` fresh on this machine |
| M2 | Body: IK Rig + Retargeter (Manny/Quinn) | **PARTIAL** — FBX→UE SkeletalMesh + 225-bone Skeleton OK (`Library /Game/VRM_RIG_POC/RedHairGirl`, Success 0 errors); IK/Retargeter assets queued | Bone-map CSV + UE import smoke |
| M4a | Face morph survival (FBX route) | **FAILED** — full + Face-only FBX both import with **0 Morph Targets** (`get_all_morph_target_names() == []`) | Try glTF route or Faceit retarget_fbx (M3) or UE-Python morph rebuild |
| M3 | Face: expression map to ARKit-52 | QUEUED | Mapping table (have vs missing) |
| M4 | UE import: FBX → SkeletalMesh + Morph smoke | QUEUED | Morph list in UE, no body overwrite |
| M5 | Sequencer gate (M5) | QUEUED | Body/face independence test + MRQ render |
| M6 | Automation % + manual-fix report | QUEUED | Headless run log |

## Folder layout

- `maps/` — bone_map.csv, face_map.csv (VRM → UE Manny/Quinn, VRM → ARKit 52)
- `scripts/` — headless Blender + UE Python (thin wrappers over `scripts/pipeline/vrm_inspect.py`)
- `outputs/` — exported FBX + JSON validation reports
- `IMPORT_REPORT.md` — auto + manual fix list per model

## Test character

`C:\Users\sb291\OneDrive\Documents\3D\Anime Character\RedHairGirl.vrm` (225 bones, Fcl_* shape keys, 32 hair-joint bones). Copy into `outputs/` on first run if licensable; do not commit if restricted.

## Next action

Run M1 fresh (`blender.exe --background --python scripts/pipeline/vrm_inspect.py`), then M2 bone-map extraction.
