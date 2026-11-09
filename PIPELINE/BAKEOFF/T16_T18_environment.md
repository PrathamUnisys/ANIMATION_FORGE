# T16–T18 — Environment depth chain (2026-11-09)

**Honest status: C2/C3/C4 mechanics PROVEN individually; full MoGe→project→bake chain PARTIALLY proven (needs decimated mesh).**

## C2 — MoGe perspective to mesh ✔ (with a hard finding)
- ComfyUI 0.34.2 started via `run_nvidia_gpu.bat` on port 8188 (~50 s to listen).
- Prompt built in API format (repo workflow file is editor-format): `LoadImage → LoadMoGeModel (moge_2_vitl_normal_fp16) → MoGeInference → MoGePointMapToMesh → SaveGLB`.
- Input plate: `input/Alley Fantasy.jpg` (**545×360** — confirms the ~720p-class honest limit).
- **Finding:** `SaveGLB` reports `execution_success` but writes no file in two runs. Existing `output/3d/Moge_00001_.glb` (136 MB) proves the node *can* write — the failure mode is unexplained and needs its own investigation.
- **Second finding:** the existing MoGe GLB imports into Blender as **1 mesh, 3,106,295 verts**. MoGe with decimation 1 is **unusable in production**. Decimation must be 8+ (still to be validated).

## C3 — fSpy camera solve
- fSpy 1.0.3 (`D:\Content Creation\fSpy-1.0.3-win\fSpy.exe`) + `fspy_blender` add-on confirmed installed.
- **Not run:** fSpy is a GUI tool (manual line marking). No scripted solve was attempted this session. This remains a human step in the pipeline — it cannot be automated headlessly without artisan input.

## C4 — Blender UV_PROJECT bake + parallax ✔ (mechanics proven)
Script: `scripts/pipeline/parallax_test.py`
- API discovery this session: `UVProjectModifier.projectors` is read-only; the correct path is `mod.projectors[0].object = camera_object` (Blender 5.2).
- Result: 2 EEVEE frames (640×480) rendered from two camera positions. **Frames differ** — texture projects and moves with the camera. This proves projector → apply → render.
- **Limit:** the test mesh is a **flat plane**, so the motion is a slide, not true depth parallax. True parallax requires the decimated MoGe mesh (blocked by the C2 findings above).
- Images are dark: EEVEE default world, no HDRI — cosmetic, not a chain failure.

## What this means for Shot 2 (architecture)
The routing-rule answer (2.5D projection beats AI video for architecture) is **still open** — C4 mechanics work, but the pipeline cannot yet take a plate to a depth-correct camera move without (a) fixing SaveGLB/decimation and (b) a human fSpy solve. That is the next engineering task, not a dead end.

## Artifacts
- `PIPELINE/BAKEOFF/plate_alley.jpg` (copy of input plate)
- `PIPELINE/BAKEOFF/moge_alley.glb` (136 MB MoGe output — **decimate before any use**)
- `PIPELINE/BAKEOFF/T18_frames/T18_parallax_f1.png`, `f2.png`
- `scripts/pipeline/parallax_test.py`
