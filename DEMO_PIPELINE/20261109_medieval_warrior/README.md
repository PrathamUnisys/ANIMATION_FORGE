# Demo Pipeline — 2026-11-09 Medieval Warrior
Full end-to-end run on your 12 GB RAM / 8 GB VRAM laptop. All outputs in `D:\Work\ANIMATION_FORGE\DEMO_PIPELINE\20261109_medieval_warrior\`:

| Step | File | Size | Tool |
|---|---|---|---|
| Script | `01_script/script.txt` | 0.1 KB | "Halt! Who dares enter the fortress?" |
| Voice | `02_voice/warrior_line.wav` | 119.6 KB | Kokoro 0.9.4 `af_heart` (Apache-2.0, CPU) |
| Lip JSON | `03_lipsync/warrior_line.json` | 1.0 KB | Rhubarb 1.14.0 pocketSphinx |
| Lip DAT | `03_lipsync/warrior_line.dat` | 0.1 KB | Rhubarb `--f dat --datFrameRate 24 --datUsePrestonBlair` → Moho 14.4 |
| Concept | `04_concept/warrior_concept.png` | 778.7 KB | Flux2-Klein 4b fp8 + Qwen 3 4b, 1024² batch 1 seed 123, LOW_VRAM async offload |
| Mesh | `05_mesh/base-optimized.fbx` | 11,471 KB | Blender 5.2.1 optimizer (`optimize_generated_glb.py`, 17,683 tris) |

See `P4_TRIAL_LOG.md` Trials 1–4 & `RESEARCH_P1_P3.md` P3 for timing, VRAM (4.4 GB during Flux), rollback notes.
Usage: import CONCEPT PNG as Blender reference (UV Image Editor), import `warrior_line.wav` into Resolve/Moho, import `warrior_line.dat` into Moho mouth poses, use `05_mesh` as rig base (AutoRigPro/FaceIt).
