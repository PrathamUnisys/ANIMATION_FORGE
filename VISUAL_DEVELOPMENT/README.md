# Animation Forge Visual Development and Storyboard System

**Status:** Working local module. The full pipeline from an **approved screenplay** to
art-direction candidates, a versioned Style Bible, storyboard images, scene-blocking
references, a human review UI and a Blender/Unreal production handoff package is
implemented and was run end to end against a local ComfyUI 0.34.2 instance.

Automatic research, model-driven script writing and any real 3D production are **not**
implemented and are not claimed. See [Known Limitations](KNOWN_LIMITATIONS.md).

---

## Purpose

Turn an approved screenplay into a coherent, visually consistent production package:

```text
approved screenplay
  -> visual breakdown (sequences / scenes / shots, each traceable to the script)
  -> 6-8 art-direction candidates rendered from ONE shared comparison scene
  -> human selection
  -> versioned Style Bible (immutable global rules + per-scene variables)
  -> storyboard images (ComfyUI)
  -> deterministic normalized blocking layouts + optional rendered blocking references
  -> per-shot human review: approve / reject / regenerate
  -> continuity report + production handoff package
```

The module never rewrites the approved screenplay, never auto-approves a style, and
never claims that a 2D image contains exact 3D geometry or world coordinates.

## Features

- **Approved-script gate.** Imports only `APPROVED`, immutable screenplay records from
  `animation_forge.db` using a read-only SQLite connection. The exact source text is
  stored with a SHA-256 and re-checked before every later stage. A separate,
  explicitly-named `init-file` command exists for **exploring a script that is still in
  draft**; it records the source as `NOT_APPROVED` and the review UI and the handoff
  both flag it.
- **Script analysis.** Deterministic parser producing episode -> sequence -> scene ->
  shot records with exact character-offset source spans. Explicit script facts and
  inferred staging are stored in separate fields. Missing information becomes an open
  question, never an invention. **Two script formats are supported** and detected
  automatically: Animation Forge screenplays (act and scene headings) and narrated
  documentary/explainer scripts (`### MM:SS` sections with `[NARRATION]` and
  `[VISUAL]` blocks).
- **Art-direction exploration.** 6-8 style profiles rendered from the *same* comparison
  scene, workflow, dimensions and seed, so the human compares direction rather than
  content.
- **Style Bible.** Versioned. Global visual rules are immutable between versions; any
  change produces a new version and the previous one is preserved.
- **Modular prompt builder.** Named modules (style, scene, environment, characters,
  action, objects, camera, composition, lighting, atmosphere, emphasis) assembled from
  the Style Bible and the structured shot spec, which is always preserved separately.
- **Live ComfyUI integration.** Configurable API-format workflow templates, node/model
  validation against `/object_info`, queue submission, status polling, image retrieval,
  reference-image upload and full reproducibility metadata.
- **Deterministic blocking.** A normalized plan-view layout (subjects, props, camera,
  sightline) rendered as JSON, SVG and PNG. The PNG can be fed back into ComfyUI as a
  Canny ControlNet reference so the rendered blocking image keeps the staging.
- **Review UI.** A local loopback server that shows the *actual* generated files and
  records append-only approve / reject / regenerate / select events.
- **Continuity checks and handoff.** Deterministic metadata checks (explicitly
  `NOT_CHECKED` for visual identity) plus a JSON + Markdown production package that
  projects to the existing `SCHEMAS/SCENE.schema.json` and `SCHEMAS/SHOT.schema.json`
  field names. The package also carries the script breakdown, the prompt overrides,
  the status of every shot and the animatic.
- **Script breakdown.** Every scene reduced to the elements a department needs, in the
  standard breakdown taxonomy: cast, extras, location, props, set dressing, costume,
  makeup, vehicle, stunt, vfx, livestock, sound, music and special equipment. It
  derives only what the script states, and a category the script does not mention stays
  visible for a human to tag.
- **Your own prompt.** The prompt is three layers: the generated modules minus any the
  user drops, an optional full replacement, and the user's own text. The negative
  prompt and the generation settings (model, LoRA, steps, CFG, sampler, scheduler,
  seed, size) are overridable per shot or per candidate. The user can also attach
  their **own ComfyUI API-format workflow**: every node class is validated against the
  live server and only the prompt text and the sampling inputs are substituted, so the
  graph the user built is kept.
- **Generation presets.** Named pipelines that are known to work on this machine, with
  what each one costs. The SDXL four-step pipeline produces a 1024x1024 image in about
  eight seconds using roughly 2.4 GB of extra video memory, which fits an 8 GB card.
- **Animatic.** The boards cut to a timeline, with the voice on them. The timeline comes
  from the analysis, the words come from the script, and the shots are held long enough
  for the line that is spoken over them.
- **One production spine.** Script, breakdown, visual direction, boards, previz,
  continuity and handoff, in one place, with a shot inspector beside it. The application
  shows it; the command line can run it.

## Requirements

- Python 3.10+ with `jsonschema>=4.22,<5` and `Pillow` (both already in the repo venv).
- A local ComfyUI server reachable over HTTP. Verified against **ComfyUI 0.34.2** on
  Windows with an NVIDIA RTX 4060 Laptop GPU (8 GB VRAM).
- Models: `dreamshaper_8.safetensors` (SD 1.5, default), optional
  `arcane_offset.safetensors` LoRA, optional `control_v11p_sd15_canny.pth` ControlNet.
  See [ComfyUI Setup](COMFYUI_SETUP.md).

No extra Python packages are required for the ComfyUI client: it uses `urllib` from the
standard library.

## Installation

The module is already part of this repository; there is nothing to install.

```powershell
# from the repository root
.\.venv\Scripts\python -c "import jsonschema, PIL; print('deps ok')"
```

## Quick start

```powershell
$proj = "PROJECTS/VDEV_PROJECT_001_SCR_PROJECT_001_V01_V1"

# 1. import the only APPROVED screenplay in the database
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli init `
    --database animation_forge.db --script-id SCR_PROJECT_001_V01 --project-dir $proj

# 2. analyse it into sequences / scenes / shots
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli analyze --project-dir $proj

# 3. build 6-8 art-direction candidates on one shared scene
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli art-direction --project-dir $proj

# 4. render the comparison image for every candidate (needs ComfyUI running)
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli generate-candidates --project-dir $proj

# 5. a human selects one (never automatic)
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli select --project-dir $proj --candidate-id ART_02

# 6. create the versioned Style Bible from that selection
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli style-bible --project-dir $proj --candidate-id ART_02

# 7. storyboard images and blocking references
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli storyboard --project-dir $proj
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli blocking --project-dir $proj --generate-images

# 8. continuity checks, production handoff, status
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli check --project-dir $proj
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli handoff --project-dir $proj
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli status --project-dir $proj

# 9. inspect the real images and approve / reject / regenerate
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli review --project-dir $proj
# -> http://127.0.0.1:8790
```

### Working with a script that is still in draft

```powershell
# exploration only: the source is recorded as NOT_APPROVED everywhere
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli init-file `
    --script-file PROJECTS/YOUTUBE_SCRIPT_EXPERIMENT/SCRIPTS/REVISED/YS01_THE_FOG_THAT_CHANGED_THE_AIR.md `
    --script-id YS01_REVISED --project-id YS01 --episode-id EP01 `
    --project-dir PROJECTS/VDEV_YS01_YS01_REVISED_V1
```

The review UI shows a red banner and the production handoff lists the missing approval
as an unresolved issue. This path never marks a source as approved and never weakens
the database approval gate.

Check the live ComfyUI connection at any time:

```powershell
.\.venv\Scripts\python -m VISUAL_DEVELOPMENT.cli comfy-check
```

## Example workflow

A complete, reproducible run is documented in [Example Project](EXAMPLE_PROJECT.md),
using the only `APPROVED` screenplay in the database (`SCR_PROJECT_001_V01`, a 45-second
fantasy comedy) and generating 26 real images through local ComfyUI.

## Project package layout

```text
PROJECTS/<VISUAL_PROJECT_ID>/
  project.json                       project manifest
  source/approved_script.md          exact imported screenplay
  source/script_manifest.json        database provenance + SHA-256
  analysis/analysis_v001.json        sequences / scenes / shots with source spans
  art_direction/candidates_v001.json the candidate set
  art_direction/candidate_ART_02/GEN_*.png + .json
  style_bibles/style_bible_v001.json
  storyboard/<SEQ>/<SCN>/<SHOT>/GEN_*.png + .json
  blocking/<SEQ>/<SCN>/<SHOT>/layout_v001.json|.svg|.png + GEN_*.png|.json
  reviews/review_events.jsonl        append-only decision log
  reports/continuity_v001.json
  handoff/handoff_v001.json + .md
```

Every generated image is stored next to a manifest that records the prompt, negative
prompt, model, LoRA, seed, dimensions, sampler, scheduler, ControlNet, reference
images, Style Bible hash, source screenplay hash, ComfyUI prompt id and review status.

## Documentation

- [Architecture](ARCHITECTURE.md)
- [User Guide](USER_GUIDE.md)
- [ComfyUI Setup](COMFYUI_SETUP.md)
- [Prompt Engineering Guide](PROMPT_ENGINEERING_GUIDE.md)
- [Framework Development Guide](FRAMEWORK_DEVELOPMENT_GUIDE.md)
- [Example Project](EXAMPLE_PROJECT.md)
- [Research Report](RESEARCH_REPORT.md)
- [Technical Decisions](TECHNICAL_DECISIONS.md)
- [Implementation Plan](IMPLEMENTATION_PLAN.md)
- [Implementation Status](IMPLEMENTATION_STATUS.md)
- [Known Limitations](KNOWN_LIMITATIONS.md)

## Governance

This module is isolated from the protected Animation Forge instruction, schema and
database structures. It does not modify `animation_forge.db` (read-only access only),
and it does not change the protected instruction files, the agent definitions or the
database schema.

It **is** reachable from the application. A read-mostly bridge
(`backend/integrations/visual_development.py`) exposes the packages through token
protected routes under `/api/visual-development/*` and `/api/production/*`, and the
application shows them in the Production workspace. The bridge never writes to the
database. It appends decisions to the module's own review event log and stores the
user's prompt overrides inside the package.

Adding a route, a panel or a table to the Animation Forge application is a change to
the application and needs a Change Request per `CORE/CHANGE_CONTROL.md`. The routes
that carry this module were added as additive, token protected routes and registered
in `DOCS/CAPABILITY_REGISTRY.md`.

A decision recorded in the local review UI is a **local creative decision**. It is not
an Animation Forge GovernanceEngine approval and it does not approve the screenplay.
