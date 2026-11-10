# Architecture

**Status:** Implemented and verified against a live local ComfyUI instance. This
document describes the module that exists, not a proposal.

## Boundary

`VISUAL_DEVELOPMENT/` is a self-contained, local-first tool. It does not add routes to
`backend/main.py`, does not write to `animation_forge.db`, does not modify global
`SCHEMAS/`, and does not edit protected instructions. It reads an approved screenplay
record from the existing SQLite database in read-only mode. Its generated episode package
is file-backed and versioned under `PROJECTS/`.

The review server binds to loopback only. The Animation Forge React UI is unchanged. A
future embedded UI/API integration needs a separate approved Change Request.

## Components

1. **Approved-script loader** (`approved_script.py`) — resolves a script id, verifies
   `approval_status == APPROVED` and `is_immutable`, copies the exact Markdown, hashes
   it, and records database provenance. A separate `load_script_file()` reads a plain
   file for exploration only and always records `approval_status = "NOT_APPROVED"`.
2. **Analysis engine** (`analyzer.py`) — parses the screenplay structure into
   episode -> sequence -> scene -> shot. The format is detected from the source:
   `parse_screenplay_script()` handles act/scene-heading screenplays and
   `parse_narrator_script()` handles `### MM:SS` narrated explainers with
   `[NARRATION]` / `[VISUAL]` blocks. Every beat carries an exact source excerpt and
   character/byte span. Explicit source facts and inferred staging are separate fields.
   Missing scene headings produce an implicit scene plus an open question.
3. **Art-direction engine** (`art_direction.py`) — combines story-derived facts with 8
   structured style profiles. Every comparison uses the same scene, workflow,
   dimensions and seed; only the direction changes. The system never auto-approves.
4. **Style Bible engine** (`style_bible.py`) — creates versioned visual rules from a
   human-selected candidate. Scene-specific variables live outside the global rules.
   Editing produces a new version; the previous version is preserved.
5. **Prompt builder** (`prompt_builder.py`) — composes named modules, preserves the
   structured shot spec separately, and supports mode-specific negative prompts.
6. **ComfyUI client** (`comfyui_client.py`) — health and node/model discovery; image
   uploads; queue submission; history polling; output retrieval; errors and retries;
   provenance. Dependency-free, using `urllib` from the standard library.
7. **Workflow templates** (`workflows.py`) — API-format workflow builders plus live
   validation of every node class and required input against `/object_info`.
8. **Blocking renderer** (`blocking.py`) — deterministic normalized plan view rendered
   to JSON, SVG and PNG; the PNG can be fed back into ComfyUI as a Canny ControlNet
   reference for a rendered blocking view.
9. **Generation orchestrator** (`generation.py`) — submit, store, record provenance, and
   write blocking layouts; guarantees an image never exists without its manifest.
10. **Review store/UI** (`review_server.py`, `storage.py`) — local gallery and comparison
    page; approve/reject/regenerate/select decisions append immutable events. Approved
    file revisions are never replaced.
11. **Continuity validator and handoff exporter** (`continuity.py`, `handoff.py`) —
    deterministic metadata checks and a JSON/Markdown package for Blender and Unreal; no
    automatic 3D scene creation.

## Data flow

```text
read-only approved screenplay
  -> immutable source + SHA-256
  -> analysis (source excerpts, facts, inferences, open questions)
  -> human-edited scene/shot breakdown
  -> 8 candidates from one shared representative scene
  -> human selection
  -> Style Bible draft -> human review
  -> storyboard + deterministic blocking layout + optionally rendered blocking image
  -> ComfyUI queue -> output files + exact provenance
  -> per-shot human review / immutable revisions
  -> continuity report + production handoff
```

## Project package layout

```text
PROJECTS/<VISUAL_PROJECT_ID>/
  project.json
  source/approved_script.md
  source/script_manifest.json
  analysis/analysis_v001.json
  art_direction/candidates_v001.json
  art_direction/candidate_<id>/GEN_<id>.png + .json
  style_bibles/style_bible_v001.json
  storyboard/<SEQ>/<SCN>/<SHOT>/GEN_<id>.png + .json
  blocking/<SEQ>/<SCN>/<SHOT>/layout_v001.json + .svg + .png + GEN_<id>.png + .json
  reviews/review_events.jsonl
  reports/continuity_v001.json
  handoff/handoff_v001.json + .md
```

Each generated revision has a unique id, SHA-256, workflow version, settings,
references, source and Style Bible hashes, and review state.

## State and failure rules

- Missing approval, a changed source hash, absent configuration, ComfyUI validation
  errors, timeouts or missing outputs block the dependent stage and create a readable
  diagnostic.
- Retry always creates a new generation attempt. It never overwrites an approved image.
- A stale source or Style Bible hash marks dependent artifacts stale; it does not delete
  or mutate them.
- Technical validation reports consistency of metadata only. It does not declare images
  visually consistent and it does not approve creative choices. Image-to-image identity
  is reported as `NOT_CHECKED`.
- A human decision in this local module is not the Animation Forge GovernanceEngine
  approval of the screenplay or the production package.

## Runtime dependencies

- Python standard library only for the ComfyUI client.
- `jsonschema` for Draft 2020-12 validation.
- `Pillow` for the blocking PNG renderer.
- A local ComfyUI server over HTTP. Verified against ComfyUI 0.34.2.
