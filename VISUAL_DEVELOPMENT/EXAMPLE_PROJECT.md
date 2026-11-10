# Example Project — a complete run on an approved screenplay

This is a real, reproducible end-to-end run of the module against the only screenplay in
`animation_forge.db` that is `APPROVED` and immutable.

Nothing in this document is illustrative. Every number comes from the run, and every
image referenced here was produced by the local ComfyUI instance.

---

## The input

| Field | Value |
|---|---|
| Script id | `SCR_PROJECT_001_V01` |
| Project | `PROJECT_001` |
| Approval status | `APPROVED` (immutable) |
| Source SHA-256 | `ea80754c9b86849c61e9bd57552db5860edd2912db3f62747245a78517100e1a` |
| Title | THE FORGOTTEN KINGDOM — SCREENPLAY (REVISION v1) |
| Genre | Fantasy Comedy |
| Target runtime | 45 s |
| Tone | Dry British fantasy satire with slapstick visual timing |
| Project directory | `PROJECTS/VDEV_PROJECT_001_SCR_PROJECT_001_V01_V1/` |

The module refuses any script that is not `APPROVED` or is not marked immutable. The ten
YouTube experiment scripts and the EP10 screenplay revision 2 are all
`AWAITING_HUMAN_REVIEW`, so they are **not** eligible inputs.

## The analysis

3 sequences (acts), 3 scenes, 9 shots, 3 described characters.

| Sequence | Title | Timecode | Scene | Heading | Shots |
|---|---|---|---|---|---|
| `SEQ_01` | THE CRUMBLING THRONE ROOM | 0:00–0:15 | `SCN_01_01` | INT. FORGOTTEN CITADEL THRONE ROOM - MORNING | 3 |
| `SEQ_02` | THE AWAKENING | 0:15–0:32 | `SCN_02_01` | INT. FORGOTTEN CITADEL THRONE ROOM - CONTINUOUS | 3 |
| `SEQ_03` | THE SLAPSTICK SETTLEMENT | 0:32–0:45 | `SCN_03_01` | *(no heading in the script)* | 3 |

| Shot | Size | Purpose | Duration | Characters |
|---|---|---|---|---|
| `SHT_SCN_01_01_001` | wide | Action beat | 6.41 s | Sir Pip, Gloop |
| `SHT_SCN_01_01_002` | close-up | Dialogue: Sir Pip | 4.60 s | Sir Pip |
| `SHT_SCN_01_01_003` | medium | Dialogue: Gloop | 3.99 s | Gloop |
| `SHT_SCN_02_01_001` | wide | Action beat | 7.02 s | Sir Pip, Stone Golem |
| `SHT_SCN_02_01_002` | close-up | Dialogue: Stone Golem | 5.41 s | Stone Golem |
| `SHT_SCN_02_01_003` | close-up | Dialogue: Sir Pip | 4.57 s | Sir Pip |
| `SHT_SCN_03_01_001` | wide | Action beat | 3.51 s | Sir Pip, Gloop |
| `SHT_SCN_03_01_002` | medium | Dialogue: Stone Golem | 5.01 s | Stone Golem |
| `SHT_SCN_03_01_003` | medium | Dialogue: Gloop | 4.48 s | Gloop |

Durations are distributed proportionally to the source excerpt length inside each
sequence's timecode, so the shots of `SEQ_01` sum to exactly 15 s.

### The honest gap

Act III of the screenplay contains **no scene heading** — the act goes straight from the
heading into action. The analyzer therefore creates an implicit scene with an **empty
location** and an **empty time**, and records:

> `SEQ_03 has no scene heading; location and time are unknown.`

It does not copy the location from Act II. That is a human decision, and it appears in
the continuity report as `scene_location_continuity: REVIEW` and in the handoff as an
unresolved issue.

## Character registry

Extracted from the screenplay itself, with source spans:

| Character | Appearance text from the script |
|---|---|
| Sir Pip | 20s, earnest squire in oversized dented pauldrons |
| Gloop | translucent emerald slime familiar wearing a tiny monocle |
| Stone Golem | 3 meters tall, mossy basalt plates, glowing amber eyes |

"Stone Golem" and "Stone Golem Bailiff" are normalised to one character so continuity
checks do not treat them as two.

## Art-direction comparison

8 candidates, all rendered from **the same scene** (`SCN_01_01`) with the **same seed**
(`536354036775427`), the same 768x768 dimensions, the same workflow and the same
checkpoint. Only the style description changes.

| Candidate | Style | Image |
|---|---|---|
| `ART_01` | Cinematic Realism | `art_direction/candidate_ART_01/GEN_F00A30124247.png` (first run) |
| `ART_02` | Stylized 3D Animation | `art_direction/candidate_ART_02/GEN_7A4C8F1C04E5.png` (first run) |
| `ART_03` | Miniature Diorama | `art_direction/candidate_ART_03/GEN_B7CEF814267A.png` (first run) |
| `ART_04` | Painterly Environments | `art_direction/candidate_ART_04/GEN_E0EFE635B54F.png` (first run) |
| `ART_05` | Graphic Novel Noir | `art_direction/candidate_ART_05/GEN_ECED51852614.png` (first run) |
| `ART_06` | Stop-Motion Aesthetic | `art_direction/candidate_ART_06/GEN_B5B997ED5994.png` (first run) |
| `ART_07` | Documentary Visualization | `art_direction/candidate_ART_07/GEN_5887D48612DA.png` (first run) |
| `ART_08` | Low-Poly Stylization | `art_direction/candidate_ART_08/GEN_ED1A5E4B667F.png` (first run) |

> The image filenames above are from the **first** pilot run. The committed pilot project
> was regenerated after the shot-id fix, so the generation ids in the committed
> `candidates_v001.json` differ. The candidate ids, styles and shared seed do not.

Comparing `ART_02` (Stylized 3D) with `ART_05` (Graphic Novel Noir) in the first run
showed exactly what the design intended: the same emerald slime subject rendered with
completely different rendering language — a glossy soft-shaded 3D read versus a hard,
inked, high-contrast graphic read.

**Selection:** `ART_02` (Stylized 3D Animation), chosen as the pilot default because it
is the most directly translatable to a Blender/Unreal stylised pipeline. This was an
operator decision during the pilot, not a rule inside the system; any candidate can be
selected with the `select` command or the review UI, and the selection is recorded as a
review event.

## Style Bible

`style_bibles/style_bible_v001.json` — version 1, status `DRAFT`.

Global rules (immutable between versions): visual principles, colour palette
("Saturated primaries balanced by neutral stone; teal-and-amber contrast"), materials,
geometry, character design, environment design, lighting, camera language, composition,
atmosphere, accuracy requirements, restrictions, positive prompt, negative prompt, and
generation settings (`dreamshaper_8.safetensors` + `arcane_offset.safetensors` @ 0.65,
768x768, 25 steps, cfg 8.0, euler/simple, seed 536354036775427).

Scene variables (changeable per scene or shot): location, time, weather, action,
lighting conditions, camera angle.

## Storyboard and blocking

| Artifact type | Images | Time per image | Total |
|---|---|---|---|
| Art direction | 8 | 8.0–8.1 s | 64.4 s |
| Storyboard | 9 | 8.0–8.1 s | 72.3 s |
| Blocking | 9 | 12.0–16.1 s | 112.5 s |
| **Total** | **26** | | **249.2 s** |

Blocking is slower because it additionally uploads the layout PNG and runs the Canny
ControlNet branch. The first image of a session also pays the model load (~18 s instead
of ~8 s).

Per shot the package holds two different things:

- `blocking/<SEQ>/<SCN>/<SHOT>/layout_v*.json|.svg|.png` — the deterministic normalized
  plan view: stage rectangle, subject markers with initials and names, prop markers,
  camera marker, field-of-view cone and sightline.
- `blocking/<SEQ>/<SCN>/<SHOT>/GEN_*.png` — a ComfyUI render that uses the layout PNG as
  a Canny ControlNet reference, so the rendered reference keeps the staging.

The layout PNG carries the literal disclaimer: *"Normalized staging only - not
Blender/Unreal coordinates, no scale or unit."*

## Review

The review UI was exercised against the real project:

- `GET /` returned HTTP 200 with the 32 KB dashboard.
- `GET /media/<path>` returned the actual PNG (885 777 bytes, `image/png`).
- `GET /media/../../../etc/passwd` was refused (404 from the containment check).
- `POST /api/action` with `APPROVE` recorded an append-only event and set
  `review_status` to `APPROVED` on the matching generation manifest.
- `REGENERATE` submits a new ComfyUI job with a changed seed and writes a new revision;
  the approved image is not overwritten.

The pilot left `SHT_SCN_01_01_001` approved for both storyboard and blocking, which is
why `handoff/handoff_v001.json` contains one approved storyboard image and one approved
blocking image.

## Continuity report

`reports/continuity_v001.json`:

| Check | Status |
|---|---|
| `shot_ids_unique` | PASS |
| `shot_script_reference` | PASS |
| `character_identity_known` | PASS |
| `scene_location_continuity` | REVIEW — Act III has no scene heading |
| `source_hash_current` | PASS |
| `style_version_current` | PASS |
| `generation_metadata_complete` | PASS |
| `visual_identity_between_images` | **NOT_CHECKED** — no validated vision comparison model |

Overall status `REVIEW`: 6 passed, 0 failed, 1 needs review, 1 not checked.

## Production handoff

`handoff/handoff_v001.json` and `.md` contain the approved script reference, the Style
Bible, the full sequence/scene/shot breakdown with `scene_projection` and shot
projections using the field names of the existing `SCHEMAS/SCENE.schema.json` and
`SCHEMAS/SHOT.schema.json`, the approved images, character and prop references, camera
and lighting notes, animation and environment-construction requirements, production
complexity, unresolved issues and the review history.

`engine_notes` records `coordinate_space: NONE`, `world_coordinates: false`,
`scale: UNSPECIFIED` and states that the package is shot intent and references only.

## Two defects this run found and fixed

1. **Shot ids were not globally unique.** The first run produced `SHT_001` in three
   different sequences. The analyzer now derives ids from the sequence and scene
   (`SHT_SCN_01_01_001`), the pilot was regenerated, and `shot_ids_unique` now passes.
2. **Review status used the wrong vocabulary.** The review UI stored the literal action
   name `APPROVE` while the handoff filtered on `APPROVED`, so approved images were
   invisible in the package. The mapping is now `APPROVE -> APPROVED`,
   `REJECT -> REJECTED`.

A third defect (a failed manifest write leaving an orphan PNG behind) was fixed by
making `write_generation_artifact` delete the image when the manifest cannot be written.

## Reproducing this run

```powershell
$proj = "PROJECTS/VDEV_PROJECT_001_SCR_PROJECT_001_V01_V1"
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli init --database animation_forge.db --script-id SCR_PROJECT_001_V01 --project-dir $proj
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli analyze --project-dir $proj
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli art-direction --project-dir $proj
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli generate-candidates --project-dir $proj
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli select --project-dir $proj --candidate-id ART_02
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli style-bible --project-dir $proj --candidate-id ART_02
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli storyboard --project-dir $proj
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli blocking --project-dir $proj --generate-images
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli check --project-dir $proj
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli handoff --project-dir $proj
```

With ComfyUI running, the whole run takes roughly **5 minutes** on the verification
machine.

## Second pilot: a narrated explainer (YS01)

The module was then re-used on a **different script format** to prove it is not tied to
the Animation Forge screenplay layout.

| Item | Value |
|---|---|
| Script | `PROJECTS/YOUTUBE_SCRIPT_EXPERIMENT/SCRIPTS/REVISED/YS01_THE_FOG_THAT_CHANGED_THE_AIR.md` |
| Format | Narrated documentary/explainer (single narrator) |
| Import path | `init-file` (exploration only, source recorded as `NOT_APPROVED`) |
| Project directory | `PROJECTS/VDEV_YS01_YS01_REVISED_V1/` |
| Detected format | `NARRATOR` |

### What the narrator parser produced

6 sequences, 6 scenes, 8 shots, running 0:00 to 8:10 (490 s, the runtime stated in the
script's own metadata). Every `### MM:SS` segment became a sequence with one scene, and
the segment's `[VISUAL]` direction became the shot beats.

| Sequence | Segment | Shots |
|---|---|---|
| `SEQ_01` | 0:00-1:15 The city disappears | 1 |
| `SEQ_02` | 1:15-2:45 Why the smoke stayed | 1 |
| `SEQ_03` | 2:45-4:40 A familiar danger | 1 |
| `SEQ_04` | 4:40-6:25 Why did policy take time? | 2 |
| `SEQ_05` | 6:25-7:45 The fog was made by choices | 2 |
| `SEQ_06` | 7:45-8:10 Ending | 1 |

`[NARRATION]`, `[SOUND]` and `[EDITOR NOTE]` blocks are stored as explicit facts, not as
shots. `[ON-SCREEN TEXT]` becomes a graphic shot. All 8 shots carry exact source spans
that slice back to the script text.

### The comparison frame, and a defect this pilot found

The first attempt produced **triptychs** instead of single frames. The comparison prompt
had carried the whole multi-sentence visual direction, and SD 1.5 read the several
sentences as several panels. That is worse than a cosmetic problem: a split-panel image
makes the candidates differ by *composition*, which defeats the entire point of the
comparison, and it throws away two thirds of the resolution.

Two fixes were made and verified:

1. The comparison now uses a **single concrete subject** - the first sentence of the
   first shot, plus the location, characters and props - instead of the whole scene
   action.
2. The comparison prompt carries an explicit single-frame constraint
   (`single continuous frame, one shot only, no split panels, no collage, no grid`) and
   the negative prompt forbids `split panel, multiple panels, comic layout, collage,
   diptych, triptych, storyboard sheet, grid of images`.

After the fix, all 8 candidates are single full-bleed frames that share the same subject
(a London street fading into fog, Big Ben in the distance, a lit streetlamp) and differ
only in rendering language. That is the comparison the assignment asks for.

### Result

8 art-direction candidates generated at ~8 s each from the same scene, the same seed
(`536354036775427`), the same 768x768 dimensions and the same workflow.

Because the source is a draft, the project records `approval_status: NOT_APPROVED`, the
review UI shows a red exploration-only banner, and the production handoff lists the
missing approval as its first unresolved issue. The database approval gate is unchanged
and still rejects every non-`APPROVED` row.

## Repository note

The pilot images are 18.2 MB across 36 PNGs. Pushing that in one pack from this machine
is reset by the network (`RPC failed; curl 55 Send failure: Connection was reset`), so
the pilot was committed as the code and documentation in one commit, followed by the
binaries in several smaller commits. Each generation manifest stores the SHA-256 of its
own image, and the test suite asserts that every committed manifest still matches its
file byte for byte, so the split history does not weaken the integrity contract.

Do not modify the committed PNGs to shrink the payload: their hashes are recorded in the
manifests and in the handoff package.
