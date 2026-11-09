# Import Report — RedHairGirl.vrm (M1)

**Date:** 2026-11-09 · **Blender 5.2.1 LTS / VRM 4.10.4 / Faceit 2.3.65 (installed, not yet run)**

## Auto OK

- 1 armature, **225 bones** (54+ `J_Bip_*` body + 32 hair-joint + face adjust bones)
- **57 shape keys** on `Face` object (Basis + 56 `Fcl_*`)
- Vowels aa/ih/ou/ee/oh: **true**; blink: **true**
- MToon materials + meshes (Face/Body/Hair001) merged
- Headless save: `outputs/M1_redhairgirl.blend` + `outputs/M1_redhairgirl.json`

## Manual / warnings

- Addon emitted `Duplicated VRM0 bone` warnings (HIPS…LITTLE_DISTAL) — harmless duplicate-node warning, import still `FINISHED`.
- `hair_brush_3d` incompatible with 5.2.1 — unrelated.
- Hair bones (`transferable_HairJ.*`): decide UE Physics Asset vs drop (M2).
- Face adjust bones (`J_Adj_*`): drop; face is morph-only (Option 1).
- MToon → UE PBR conversion needed (M4).
- Faceit VRM-compat: not yet run — M3 trial queued.

## M2/M4a result (2026-11-09, UE 5.8)

- `vrm_export_fbx.py` → `outputs/M2_redhairgirl.fbx` (Blender 5.2.1, `add_leaf_bones=False`, selection-only).
- `ue_import_fbx.py` (`AssetImportTask` + `FbxImportUI`) → `/Game/VRM_RIG_POC/RedHairGirl` **SkeletalMesh** + `RedHairGirl_Skeleton` (225 bones). Headless run: **Success, 0 errors** (`outputs/ue_import.log`).
- **Morphs LOST:** `mesh.get_all_morph_target_names()` → `[]`. Face-only FBX (`M2b_face.fbx`) also `0`. Blender FBX kwargs have no shape-key flag (probed `export_scene.fbx` RNA) — exporter drops shape keys when `use_selection`/multi-mesh, or UE import ignores FBX blendshapes without a setting. Flagged NEEDS-FIX: try glTF + Interchange, or Faceit `retarget_fbx`.
- Materials exploded into 15+ MToon instances (expected; MToon→PBR map queued).
