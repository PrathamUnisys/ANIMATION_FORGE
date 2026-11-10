# Architecture

## Boundary

`VISUAL_DEVELOPMENT/` is a self-contained, local-first tool. It does not add routes to `backend/main.py`, change `animation_forge.db`, modify global `SCHEMAS/`, or edit protected instructions. It reads an approved screenplay record from the existing SQLite database in read-only mode. Its generated episode package is file-backed and versioned under `PROJECTS/`.

The standalone review server binds to loopback only. The current Animation Forge React UI remains unchanged. A future embedded UI/API integration needs a separate approved Change Request.

## Components

1. **Approved-script loader:** resolves a script ID, verifies `approval_status == APPROVED` and immutable state, copies exact Markdown, hashes it, and records database provenance.
2. **Analysis engine:** parses known screenplay/narration structures into episode → sequence → scene → shot records. Every beat includes an exact source excerpt and character/byte span. Explicit source facts and inferred staging are separate fields.
3. **Art-direction engine:** combines story-derived setting/character/prop facts with 6–8 structured style profiles. Each comparison uses the same scene excerpt, prompt bindings, generation settings, and seed.
4. **Style Bible engine:** creates immutable versioned visual rules from a human-selected candidate. Scene-specific variables are stored outside global rules. Editing creates a new draft version.
5. **Prompt builder:** composes named modules, preserves the structured shot spec, supports optional reference images and configured controls, and records the final prompt separately.
6. **ComfyUI client:** service-health and node/model discovery; image uploads; workflow validation; queue submission; progress/status polling; output retrieval; errors/retries; provenance.
7. **Blocking renderer:** generates a deterministic plan view with normalized subject/prop positions and camera direction. An optional image workflow can render that plan into a visual blocking reference.
8. **Review store/UI:** local gallery and comparison page; approve/reject/revision-request decisions append immutable events. Approved file revisions are never replaced.
9. **Continuity validator and handoff exporter:** deterministic metadata checks and JSON/Markdown package for Blender/Unreal; no automatic 3D scene creation.

## Data flow

```text
read-only approved screenplay
  -> immutable source + SHA-256
  -> analysis draft (source excerpts, facts, inferences, open questions)
  -> human-edited scene/shot breakdown
  -> six/eight candidates from one shared representative scene
  -> human selection
  -> Style Bible draft -> human review
  -> storyboard + deterministic blocking layout + optional generated blocking image
  -> ComfyUI queue -> output files + exact provenance
  -> per-shot human review / immutable revisions
  -> continuity report + production handoff
```

## Project package layout

```text
PROJECTS/<VISUAL_PROJECT_ID>/
  source/approved_script.md
  source/script_manifest.json
  analysis/analysis_v001.json
  art_direction/candidates_v001.json
  art_direction/candidate_<id>/image_v001.png + generation.json
  style_bibles/style_bible_v001.json
  storyboard/<sequence>/<scene>/<shot>/storyboard_v001.png + generation.json
  blocking/<sequence>/<scene>/<shot>/layout_v001.svg + layout.json
  blocking/<sequence>/<scene>/<shot>/blocking_v001.png + generation.json
  reviews/review_events.jsonl
  reports/continuity_v001.json
  handoff/v001/...
```

Names are illustrative; exact names are fixed by the implemented package API. Each generated revision has a unique ID, SHA-256, workflow version, settings, references, source and style-bible hashes, and review state.

## Failure and state rules

- Missing approval, a changed source hash, absent required configuration, ComfyUI validation errors, timeouts, or missing outputs block the dependent stage and create a readable diagnostic.
- Retry always creates a new generation attempt/revision. It never overwrites an approved image.
- A stale source/style-bible hash marks dependent artifacts stale; it does not delete or mutate them.
- Technical validation reports consistency of metadata only. It does not declare images visually consistent or approve creative choices.
- A human review decision in this local module is not the Animation Forge GovernanceEngine approval of the screenplay or production package.
