# Deep Research: Automated VRM-to-Unreal Body & Facial Rig Conversion

**Date:** 2026-11-09 · **Targets:** UE 5.8 / Blender 5.x / VRM 1.0-preferred (+0.x) / Faceit allowed
**Status:** Research only — no POC code. All claims cited to URL or disk evidence; unverifiable items marked NEEDS-POC.

## 0. Environment (verified on disk)

- Installed UE: **UE 5.8 at `D:\Work\Epic\UE_5.8`** (verified: `.egstore` + `Engine` + `FeaturePacks` present). Also `C:\Program Files\Epic Games\UE_5.6` exists. POC target 5.8 is installed.
- Blender: **5.2** (`C:\...\Blender Foundation\Blender\5.2\extensions`: `vrm` 4.10.4 Blender 4.2–5.3 MIT+GPL; `faceit` **2.3.65** Blender min 4.2 GPL, with `shape_keys/`, `ctrl_rig/`, `retarget_fbx/` modules + `FaceitRig.blend`). Blender MCP still not connected (WinError 10053), but extension versions verified on disk.
- Reallusion installed: Auto Setup **v2.01** (`EngineVersion: 5.7.0`, `PlatformAllowList: Win64`, enables IK Rig, Control Rig, Live Link, ChaosCloth, HairStrands — `RLPlugin.uplugin`). Current release **v2.03 supports UE 5.6/5.7/5.8** (reallusion.com/auto-setup download page). Installed copy is one version behind.
- Local prior proof (this repo): `scripts/pipeline/vrm_inspect.py` imports VRM headless via `bl_ext.blender_org.vrm` (`import_scene.vrm`); `mouth_drive.py` drives `Fcl_MTH_*` + `Fcl_EYE_Close` shape keys; `shot1_vrm.py` combines turn+gesture+mouth (T15/T20). This proves **Blender-side** VRM import/mouth/blink automation already works.

## 1. Feasibility verdict

**Yes with custom development — the chain exists, the turnkey converter does not.** VRM→Blender (humanoid + expressions as shape keys) is FULLY automated and proven locally. Blender→UE (FBX skeletal mesh + morph targets) is PARTIAL (FBX path is standard; mapping + auto-setup is the custom part). No verified open repo does end-to-end VRM→Sequencer-ready UE char with independent body/face; **Reallusion Auto Setup is the reference standard for UE-side automation, but CC/iClone-only** (README: "fully automated shader and skeleton assignments for Character Creator (CC) and iClone characters").

## 2. Approach comparison

| | A: Custom tool | B: Blender+Faceit | C: Hybrid (A+B+UE Python) |
|---|---|---|---|
| Body | Map VRM humanoid → Manny/Quinn via IK Retargeter (verify chain) | Rigify/custom + FBX | Same as A, Blender-side normalize |
| Face | VRM expressions → Morph Targets directly | Faceit ARKit 52 + Control Rig | Direct Morph Targets; Faceit optional for missing ARKit |
| Automation | Highest (headless Python) | Faceit is GUI-first; Python automation NEEDS-POC | Highest if Faceit kept optional |
| Effort | M (parser+maps+exporter) | S–M if Faceit fits, L if custom ARKit gen | M (recommended) |
| Risk | Bone-map drift per model | Faceit↔VRM mismatch (see §5) | Manageable, modular |

**Recommendation: C.** Blender headless (VRM addon API is documented: `bpy.ops.import_scene.vrm`, humanoid + MToon + expression scripting — vrm-addon-for-blender.info scripting-api) + bone/face maps + FBX + UE Python (Epic Control Rig docs confirm "Python Scripting for Rigging with Control Rig" exists). Faceit optional, never required.

## 3. Sequencer architecture (core)

- **Option 1 — Single Skeletal Mesh (RECOMMENDED):** one `SkeletalMesh`, body skeleton + Morph Targets. Body seq on Animation track; morph channel curves on separate Sequence curves. Independent control = yes (different tracks/curves, no overwrite). Best perf, best Movie Render Queue story, simplest reuse. *NEEDS-POC M5 gate to confirm morph curves don't overwrite body seq.*
- **Option 2 — Mesh + facial Control Rig:** morphs driven by Control Rig controls (MetaHuman-style). More artist-friendly face controls; extra asset + sync work. Reallusion ships equivalent (`CC UE Control Rig` — MetaHuman control rig for CC chars). Recommend **phase 2**, behind Option 1.
- **Option 3 — Separate face mesh:** reject for YouTube production — attachment/sync/export cost, no benefit if Option 1 works.

## 4. Body rig strategy

VRM humanoid (54+ bones, `hips/spine/head/upper_arm...`) → UE via **Retargeter, not rename**: keep VRM bone names, author `IK Rig` (VRM chain) + `IK Retargeter` (VRM→Manny/Quinn). Direct skeleton compatibility (rename-only) is FRAGILE across models — avoid. Physics Asset: auto-generate, manual tune. MToon → UE PBR conversion needed (VRM addon documents MToon settings; UE has no native MToon — custom material map).

## 5. Face rig strategy + Faceit verdict

- VRM 1.0 expressions (`VRMC_vrm_expression`: presets happy/angry/sad/relaxed/lookUp/lookDown/lookLeft/lookRight/blink/aa/ih/ou/ee/oh/look* + custom) import to Blender as **shape keys** (proven locally).
- Mapping to ARKit 52 is **PARTIAL**: vowels/blink/look* map; happy/sad/etc are compound, many ARKit shapes missing → must generate or accept VRM-native set. **Do not claim automatic ARKit fill.**
- **Faceit 2.3.65 installed** (`user_default\faceit`, docs at faceit-doc.readthedocs.io, GPL-3.0 per manifest — note: manifest says GPL, store may be paid tier; verify license). Has `shape_keys/`, `ctrl_rig/`, `retarget_fbx/` modules. Compatibility with existing VRM shape keys, FBX morph survival, and headless Python are **still NEEDS-POC** (no run yet), but install blocker is cleared.
- FBX shape keys → UE Morph Targets: NEEDS-POC (Epic Morph Targets page fetch returned TOC-only; JS-rendered, unverified text).

## 6. Existing solutions (verified via GitHub API / vendor pages)

| Repo/tool | License | Activity | Versions | Body/Face/Sequencer |
|---|---|---|---|---|
| `saturday06/VRM-Addon-for-Blender` (MIT, 1,740★, 170 forks, pushed 2026-11-08) | MIT (repo); extensions page adds GPL for extension | Active | Desc: "Blender 2.93 to 5.2"; ext 4.10.4 (2026-11-04) compat 4.2LTS–5.3 zip | Import/export + humanoid + MToon + Python API; no UE |
| `ruyo/VRM4U` (C++, 2,010★, 245 forks, pushed 2026-10-17) | Other/NOASSERTION | Active | UE5 runtime loader ("Runtime VRM loader for UnrealEngine5") | Runtime load; **not** editor conversion; Sequencer conversion unverified |
| Reallusion Auto Setup v2.03 | Proprietary | Current | UE 5.6/5.7/5.8, Win64, CC 5.11/4.71, iClone 8.73 | CC/iClone-only; shader/skeleton/Control Rig/Live Link; no VRM |
| Faceit 2.3.65 (installed, `user_default\faceit`) | GPL-3.0 per manifest | Installed | Blender min 4.2; docs faceit-doc.readthedocs.io | shape_keys/ctrl_rig/retarget_fbx modules; VRM compat NEEDS-POC |

Not verified (no invention): no other repo found that automates VRM→UE conversion.

## 7. Standardized output

| Asset | Auto | Manual |
|---|---|---|
| SkeletalMesh, Skeleton (VRM names), Morph Targets | Yes | — |
| Physics Asset, Materials (MToon→PBR), Textures | Template | Tune (outline/toon) |
| IK Rig, Retargeter (Manny/Quinn) | Template | Verify per model |
| Control Rig, AnimBP template, Face Rig | Template/gen | Art-direct |
| Blueprint (Sequencer-ready) + conversion report | Yes (UE Python) | Review |

## 8. POC plan (6 milestones, per brief)

M1 import+map extraction (done locally: `vrm_inspect.py`) → M2 Retargeter Manny/Quinn check → M3 expression map + missing-vs-generated list → M4 FBX import smoke (morphs visible, no overwrite) → **M5 gate**: walk+turn+blink+mouth+smile+talk, body/face independence → M6 headless % automation + manual-fix report. UE 5.8 + Faceit 2.3.65 installed — no install blocker; next is M2–M4 trials.

## 9. Repo structure (proposed)

`vrm-pipeline/{core/{vrm_parser,bone_map,face_map}, blender/{import,normalize,fbx}, ue/{import,ik,controlrig,blueprint}, validators, examples, docs}`. Form: **CLI + Blender scripts + UE Python** (skip standalone addon/UE plugin until POC proves need).

## 10. Final answers (8)

1. **Yes** — via Retargeter + Morph Targets (custom dev). 2. **Original expressions preserved** as Morph Targets (yes; mapping table required). 3. **Missing ARKit shapes not auto-generatable** reliably — manual/gen needed. 4. **Faceit optional/NEEDS-POC** — do not depend. 5. **Yes — Option 1**, separate tracks, NEEDS-POC M5 proof. 6. **Yes** — structure above. 7. **Simplest reliable: Hybrid CLI (C).** 8. **Build first:** M1–M2 skeleton+orbit (bone map + Retargeter template), defer Faceit.

## 11. Risks / complexity

UE 5.8 + Faceit installed (blockers cleared); Epic morph/IK doc pages JS-only (fetch TOC-only); VRM4U license unclear; FBX morph survival NEEDS-POC. Complexity: M (2–4 wk POC, 4–8 wk reusable tool). If M4 fails (morphs lost in FBX), fall back to UE Python Morph editing — L effort.

---
*Evidence: `scripts/pipeline/vrm_inspect.py:22,29-32`; `mouth_drive.py:22-31,44-51`; `shot1_vrm.py:28-51`; `RLPlugin.uplugin: EngineVersion 5.7.0, Plugins [IKRig,ControlRig,LiveLink]`; docs.blender.org (5.2 LTS); dev.epicgames.com (Control Rig overview — Python scripting); vrm-addon-for-blender.info scripting-api; extensions.blender.org VRM 4.10.4; api.github.com (saturday06, ruyo/VRM4U search); reallusion.com auto-setup (v2.03, UE 5.6–5.8).*
