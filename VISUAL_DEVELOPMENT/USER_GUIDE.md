# User Guide

Operating the Visual Development and Storyboard module step by step. Every command is
run from the repository root with the repository virtual environment.

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli <command> --help
```

---

## 0. Before you start

1. Start ComfyUI and confirm it answers:
   ```powershell
   .\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --fast fp16_accumulation --port 8188 --disable-auto-launch
   .\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli comfy-check
   ```
   `comfy-check` prints the ComfyUI version, the GPU, and the checkpoints / LoRAs /
   ControlNets that are actually installed.

2. Choose a script. The module only accepts screenplay records that are `APPROVED` and
   immutable in `animation_forge.db`. To see what is available:
   ```sql
   SELECT script_id, project_id, version, approval_status, is_immutable
   FROM scripts WHERE approval_status = 'APPROVED' AND is_immutable = 1;
   ```

## 1. Start a new episode (import the approved script)

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli init `
    --database animation_forge.db `
    --script-id SCR_PROJECT_001_V01 `
    --project-dir PROJECTS/VDEV_PROJECT_001_SCR_PROJECT_001_V01_V1
```

What happens: the screenplay text is copied verbatim, hashed with SHA-256, and the
database provenance (script id, version, approval status, immutability) is stored in
`source/script_manifest.json`. The project directory is never overwritten — an existing
directory is a hard error.

### Working with a script that is still in draft

Some scripts are not approved yet but you still want to explore art direction for them.
Use the separate `init-file` command, which is deliberately a different command so the
approved gate is never bypassed by accident:

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli init-file `
    --script-file PROJECTS/YOUTUBE_SCRIPT_EXPERIMENT/SCRIPTS/REVISED/YS01_THE_FOG_THAT_CHANGED_THE_AIR.md `
    --script-id YS01_REVISED --project-id YS01 --episode-id EP01 `
    --project-dir PROJECTS/VDEV_YS01_YS01_REVISED_V1
```

The project records `approval_status: NOT_APPROVED`. The review UI shows a red
exploration-only banner, and the production handoff lists the missing approval as its
first unresolved issue. Nothing produced from this path may be presented as a
production-ready package.

### Supported script formats

The format is detected from the file, so nothing needs to be configured:

| Format | Detected by | Structure used |
|---|---|---|
| Screenplay | `## ACT` / `**INT.` headings | Act = sequence, scene heading = scene, action and dialogue = shots |
| Narrated explainer | `### MM:SS` sections with `[NARRATION]` / `[VISUAL]` blocks | Timecoded segment = sequence, `[VISUAL]` direction = shot beats, `[ON-SCREEN TEXT]` = graphic shot |

In the narrated format, `[NARRATION]`, `[SOUND]` and `[EDITOR NOTE]` are recorded as
explicit facts, never as shots.

## 2. Analyse the script

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli analyze --project-dir $proj
```

Output: `analysis/analysis_v001.json` with episode metadata, sequences (acts), scenes,
shots, a character registry with the appearance text from the script, and an
`open_questions` list.

**Read `open_questions`.** It records what the script does *not* say. In the pilot it
reports that Act III has no scene heading, so the location and time are unknown. The
system does not invent a location; it flags the gap for you.

Every shot carries `source_spans` with exact character offsets. You can verify any shot
by slicing the imported screenplay at those offsets.

## 3. Build the art-direction candidates

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli art-direction --project-dir $proj
```

This produces 6-8 structured style profiles. They all describe the **same** comparison
scene (by default the most visually informative scene), so the only variable is the
direction. Pass `--comparison-scene SCN_02_01` to compare a different scene.

## 4. Render the candidates

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli generate-candidates --project-dir $proj
# only some of them:
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli generate-candidates --project-dir $proj --only ART_02 ART_05
```

Each candidate uses one shared seed, so the images differ by style rather than by luck.
Each image is stored with a full manifest.

## 5. Compare and select

Open the review UI (step 9) and use the **Art Direction** tab, or select from the CLI:

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli select --project-dir $proj `
    --candidate-id ART_02 --actor "your-name" --note "why you picked it"
```

Selection is never automatic. Selecting a different candidate later is allowed and
records another event; the candidate set keeps the selection flag on exactly one entry.

## 6. Create the Style Bible

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli style-bible --project-dir $proj --candidate-id ART_02
```

The Style Bible separates:

- **global_rules** — immutable visual identity: visual principles, palette, materials,
  geometry, character design, environment design, lighting, camera language,
  composition, atmosphere, accuracy requirements, restrictions, positive and negative
  prompt guidance, and the generation settings (model, LoRA, seed, steps, cfg, sampler,
  scheduler, size).
- **scene_variables** — what changes per scene or shot: location, time, weather, action,
  lighting conditions, camera angle.

The Style Bible is created as `DRAFT`. Editing global rules produces a new version;
the previous version file is preserved.

Approving it is a human decision, and it is recorded as an event rather than by
editing the immutable file:

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli approve-style-bible --project-dir $proj `
    --actor "your-name" --note "the direction the director signed off"
```

## 6b. Take the prompt over

The generated prompt is a good default, not the only one. Every direction and every
shot can carry your own text.

```powershell
# add your own words on top of the generated prompt
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli set-prompt --project-dir $proj `
    --target-id ART_03 --kind ART_DIRECTION_CANDIDATE `
    --prompt-extra "1920s archive photograph, heavy grain, high contrast" `
    --negative-extra "modern digital render" `
    --exclude-module emphasis `
    --setting seed=987654321 --setting steps=30 `
    --actor "your-name" --note "the director's own direction"

# look at what would be sent, without spending a generation
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli show-prompt --project-dir $proj --target-id ART_03

# back to the generated prompt
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli reset-prompt --project-dir $proj --target-id ART_03
```

A preset sets a whole pipeline at once (model, LoRA, steps, guidance, scheduler and
size). The preset is applied first and your own numbers are applied after it, so a
single value can still be changed by hand:

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli set-prompt --project-dir $proj `
    --target-id SHT_SCN_01_01_001 --kind SHOT --setting preset=sdxl_lightning_4step
```

### Bring your own ComfyUI workflow

A workflow you built in the ComfyUI canvas can be used as it is. The node classes
are validated against the live server, and only the prompt text and the sampling
inputs are substituted, so your graph is kept:

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli import-workflow --project-dir $proj `
    --file C:\path\to\my_workflow_api.json --workflow-id MY_WORKFLOW

.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli validate-workflow --project-dir $proj `
    --workflow-id MY_WORKFLOW

.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli set-prompt --project-dir $proj `
    --target-id ART_03 --kind ART_DIRECTION_CANDIDATE --workflow-id MY_WORKFLOW
```

The workflow must be in **API format** (`File -> Export Workflow (API)` in the ComfyUI
canvas), not the save format, because the save format carries the layout and the
node titles.

## 7. Storyboard

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli storyboard --project-dir $proj
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli storyboard --project-dir $proj --shot SHT_SCN_01_01_001
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli storyboard --project-dir $proj --limit 3

# use a different pipeline, for example the SDXL one
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli storyboard --project-dir $proj `
    --preset sdxl_lightning_4step
```

Each shot is rendered with the Style Bible rules plus that shot's own scene, characters,
action, camera and composition. The structured shot specification is stored separately
from the final prompt in every manifest, so you can always read what the image was asked
to show.

## 8. Blocking

```powershell
# layouts only (fast, no ComfyUI needed)
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli blocking --project-dir $proj

# layouts plus a rendered blocking reference per shot
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli blocking --project-dir $proj --generate-images
```

Two different outputs are produced for the same shot id:

1. **`layout_v*.png` / `.svg` / `.json`** — the deterministic normalized plan view. This
   is the authoritative staging record: subjects, props, camera position, field of view,
   sightline and movement. Coordinates are normalized to a 0..1 stage rectangle and are
   **not** Blender or Unreal world coordinates.
2. **`GEN_*.png`** — a rendered blocking reference produced by ComfyUI with the layout
   PNG used as a Canny ControlNet image, so the rendered view keeps the staging.

## 9. Review the real images

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli review --project-dir $proj
# -> http://127.0.0.1:8790
```

The server binds to loopback only and serves the actual files from the project
directory. Tabs:

| Tab | Contents |
|---|---|
| Overview | Episode metadata, open questions, continuity report |
| Art Direction | All candidates side by side with a **Select** button |
| Style Bible | The full Style Bible JSON |
| Storyboard | Shots grouped by sequence and scene, with **Approve / Reject / Regenerate** |
| Blocking | Storyboard and blocking reference side by side, with **Approve / Reject** |
| Generation Monitor | ComfyUI status and the recent review-event log |

**Regenerate** submits a new image to ComfyUI and appends a new generation. It uses the
plan for that shot, so it uses the prompt you wrote, your settings and your workflow.
Approved images are never overwritten: every attempt is a new revision.

The port can be changed with `--port`. Port 8765 was occupied on the verification
machine, which is why the default is 8790.

## 9b. The Production workspace in the application

The same packages are in the application, under **Visual Development** in the sidebar.
The workspace shows one spine — script, breakdown, visual direction, boards, previz,
continuity, handoff — with a shot inspector beside it.

- **Breakdown** renders as a breakdown sheet: the elements of each scene, coloured by
  category, and the categories the script does not mention.
- **Boards** is a shot strip with the real frames, the shot size, the duration and the
  status. Approve, Reject and Regenerate are on each row.
- **Visual Direction** is the candidate gallery, with **Select this direction** and
  **Approve the Style Bible**.
- The **inspector** is where the prompt is taken over: the generated prompt is shown
  as generated, any module can be dropped, your own text and negative prompt are added
  on top, the settings and the preset are chosen, a ComfyUI workflow is attached, and
  **Render this shot** makes the picture with exactly that.

The stages can be linked to directly: `http://127.0.0.1:1420/?stage=BOARDS#vdev`.

## 9c. Cut the animatic

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli animatic --project-dir $proj
```

The boards are cut to a timeline with the voice on them. The voice uses the local
Kokoro model when it is available; when it is not, the animatic is still cut and the
lines are recorded as silent. The shots are held long enough for the line that is
spoken over them, so the voice is never cut off.

## 9d. Break the script down

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli breakdown --project-dir $proj
```

Every scene is reduced to the elements a department needs. It derives only what the
script states.

## 10. Continuity checks

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli check --project-dir $proj
```

Checks: unique shot ids, every shot traceable to the script, known character identity,
scene location continuity, current source hash, current Style Bible version, complete
generation metadata, and **visual identity between images**.

The last one is reported as `NOT_CHECKED` on purpose. There is no validated vision
comparison model in this environment, so the module refuses to claim that the images
match. Comparing them is a human task.

## 11. Export the production handoff

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli handoff --project-dir $proj
```

Produces `handoff/handoff_v001.json` and `handoff/handoff_v001.md` containing the
approved script reference, the Style Bible, the sequence / scene / shot breakdown, the
approved storyboard and blocking images, character and prop references, camera and
lighting notes, animation and environment-construction requirements, production
complexity, unresolved issues and the review history.

The package also contains `scene_projection` and shot projections using the field names
of the existing `SCHEMAS/SCENE.schema.json` and `SCHEMAS/SHOT.schema.json`.

`engine_notes` states explicitly that the package carries **no** world coordinates, no
scale and no 3D scene. The `focal_length_mm` field is a nominal planning equivalent of
the shot size, not a measured lens value.

## 12. Project status

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli status --project-dir $proj
```

Shows the stage, the source script and its approval status, and how many generations
exist by type and by review status.

---

## Reusing the module for the next episode

1. `init` a new project directory from the next approved script id.
2. `analyze`, then read `open_questions` and fix anything the script left ambiguous.
3. `art-direction` and `generate-candidates`, then a human selects.
4. `style-bible` — reuse the same global rules when the show keeps its look, or create
   a new Style Bible for a different visual identity.
5. `storyboard`, `blocking`, `review`, `check`, `handoff`.

Nothing in the module is tied to a particular episode: the style profiles, the analyzer
rules, the prompt modules and the workflow templates are all reusable.

## What this module will not do

- It will not modify the approved screenplay.
- It will not select a style for you.
- It will not claim that generated images contain exact 3D geometry or coordinates.
- It will not claim visual continuity has been verified.
- It will not mark anything production-ready.
