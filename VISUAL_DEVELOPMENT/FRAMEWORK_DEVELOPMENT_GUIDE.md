# Framework Development Guide

How this module was built, what was decided and why, how to change it, and how to debug
it.

---

## 1. How it was developed

The work ran in two phases.

**Phase 1 — research and checkpoint (no code).** The repository was inspected, the
governance boundary was identified, the ComfyUI server routes were read from the
official documentation, and the existing screenplay workflow, schemas and adapters were
audited. That produced `RESEARCH_REPORT.md`, `TECHNICAL_DECISIONS.md`, `ARCHITECTURE.md`,
`IMPLEMENTATION_PLAN.md` and `KNOWN_LIMITATIONS.md`, committed as a checkpoint. At that
point ComfyUI was **not reachable**, so no live claim could be made.

**Phase 2 — implementation and live verification.** ComfyUI was found at
`D:\Downloads\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\`, started, and
verified with `/system_stats`, `/object_info` and `/models/*`. The module was then built
stage by stage, each stage verified before the next:

| Stage | What was verified |
|---|---|
| Schemas | All six module schemas pass `Draft202012Validator.check_schema` |
| Project core | Approved-script import from a temp database copy; hash round-trip; event append |
| Analyzer | 3 sequences / 3 scenes / 9 shots; every source span slices back to the exact screenplay text; missing scene heading becomes an open question |
| Art direction | 8 candidates on one shared scene and seed; exactly one selection at a time |
| Style Bible | Refuses to build without a human selection; revision creates a new version |
| Blocking | Deterministic layout; normalized coordinates; SVG and PNG render |
| ComfyUI client | Live generation through `/prompt`, `/history`, `/view`; plus a mock HTTP server for the hermetic test |
| Prompt builder | Modular output; the structured shot spec is preserved separately |
| Generation | 26 real images produced, each with a complete provenance manifest |
| Continuity | 6 PASS / 0 FAIL / 1 REVIEW / 1 NOT_CHECKED |
| Review UI | HTTP 200 dashboard, real image bytes served, path traversal refused, approve/reject/regenerate recorded |
| Handoff | JSON + Markdown package produced with explicit no-3D-geometry notes |

## 2. Architectural decisions

Full detail is in `TECHNICAL_DECISIONS.md`. The decisions that shaped the code:

**Isolated module, file-backed storage.** The module lives in `VISUAL_DEVELOPMENT/` and
writes a self-contained project package. It adds no backend route, no database table, no
global schema and no React change. Integration into the main app needs a separately
approved Change Request.

**Read-only database access.** `approved_script.py` opens `animation_forge.db` with
`mode=ro` and requires `approval_status = APPROVED` and `is_immutable`. A caller cannot
smuggle an unapproved file in as if it were approved.

**Deterministic script analysis instead of an LLM.** The screenplay format is regular
enough to parse deterministically. That removes a network dependency, makes results
reproducible, and guarantees that every shot can be traced to an exact source span.
Where the script is silent, the analyzer records an open question instead of guessing.
An LLM-based enrichment can be added later behind the same interface, but it is not
required and is not claimed.

**File-backed storage with immutable revisions.** Generated images are written with
`write_json_new`-style exclusive creation, so an approved image can never be
overwritten. A regeneration is always a new revision. Review events are appended to a
JSONL log.

**Modular prompts, never one template.** Style, scene, environment, characters, action,
objects, camera, composition, lighting, atmosphere and emphasis are separate modules,
assembled from the Style Bible plus the shot record. The structured shot spec is stored
beside the final prompt in every manifest.

**Blocking as a deterministic plan view.** A 2D image cannot establish calibrated world
coordinates, so the module produces a normalized plan view (JSON + SVG + PNG) as the
authoritative staging record, and optionally feeds that PNG back into ComfyUI as a Canny
ControlNet reference so a rendered blocking reference keeps the staging. Neither output
is labelled as Blender or Unreal coordinates.

**HTTP polling, not WebSocket.** `/prompt`, `/history`, `/queue`, `/view` and
`/upload/image` are enough, they are simpler to test, and they avoid an extra
dependency. A WebSocket transport can be added later without changing job records.

**Workflows built in code, in API format.** The bundled ComfyUI workflows are UI-format
files whose node positions and widget values are not usable for submission, and most of
them reference models that are not installed. The module builds API-format workflows
with explicit node references and validates every node class and required input against
the live `/object_info` before queueing.

**A separate local review UI.** The main React app cannot be changed without an
approved integration, and the assignment requires real images to be inspectable. The
loopback server serves the actual files from the project directory.

## 3. Module map

| File | Responsibility |
|---|---|
| `common.py` | Hashing, path containment, JSON IO, schema validation, UTC timestamps |
| `approved_script.py` | Read-only `APPROVED` screenplay loader with provenance |
| `storage.py` | `ProjectStore`: immutable artifacts, revision numbering, append-only events |
| `analyzer.py` | Screenplay -> episode / sequence / scene / shot with source spans; also the narrated-explainer format |
| `art_direction.py` | 8 style profiles, shared comparison scene, human selection |
| `style_bible.py` | Versioned immutable rules + scene variables |
| `prompt_builder.py` | Modular prompt assembly from Style Bible + shot spec |
| `comfyui_client.py` | Dependency-free HTTP client for the documented ComfyUI routes |
| `workflows.py` | API-format workflow templates and live validation |
| `generation.py` | Submit -> store -> provenance, and blocking layout writing |
| `blocking.py` | Deterministic normalized layout, SVG and PNG renderers |
| `continuity.py` | Deterministic continuity checks with honest `NOT_CHECKED` states |
| `handoff.py` | JSON + Markdown production package and engine projections |
| `review_server.py` | Loopback review UI and decision recording |
| `cli.py` | Command line entry point for every stage |

## 4. Extending it

### Add another ComfyUI workflow

1. Add a builder in `workflows.py` returning an API-format dictionary. Node references
   are `["node_id", output_index]`.
2. Add a `WORKFLOW_*` constant for the id and version.
3. Call it from `generation.generate_image()` with the new `workflow_id`, or extend
   `generate_image()` with a mode switch.
4. Validate it live before queueing:

   ```python
   from VISUAL_DEVELOPMENT.comfyui_client import ComfyUIClient
   from VISUAL_DEVELOPMENT.workflows import validate_workflow
   result = validate_workflow(ComfyUIClient(), my_workflow)
   assert result["status"] == "PASS", result
   ```

### Add another image model

Put the checkpoint in `ComfyUI\models\checkpoints\`, confirm it with
`GET /models/checkpoints`, then set `generation_settings.model` in the Style Bible
(`style_bible.py`, `DEFAULT_GENERATION_SETTINGS`). The model name is recorded in every
manifest, so earlier images keep pointing at the model that produced them.

### Add another script format

1. Write a parser in `analyzer.py` that returns the same analysis structure as
   `parse_screenplay_script()` and `parse_narrator_script()`.
2. Extend `detect_format()` to recognise it and add a branch in `parse_script()`.
3. Every shot must carry a non-empty `source_spans` list whose `text` slices back
   exactly from the source, and a non-empty `explicit_facts` list.
4. Add a test that parses a real file of that format and asserts the spans round-trip.

The structure the parsers must produce is fixed by `schemas/analysis.schema.json`.

### Add another art-direction profile

Add an entry to `STYLE_PROFILES` in `art_direction.py` with a `prompt_suffix` and the
descriptive fields (`palette`, `lighting`, `materials`, `geometry`, `environment`,
`character_design`, `camera`, `storytelling`, `feasibility`, `generation_requirements`,
`strengths`, `limitations`). The candidate count is derived from the list length, so
adding a profile adds a candidate.

### Add a continuity check

Add a function to `continuity.py` that appends a `_check(...)` entry. Use `PASS`,
`FAIL`, `REVIEW`, `NOT_CHECKED` or `NOT_AVAILABLE`. Anything that cannot be verified
with the tools available must be `NOT_CHECKED` — never `PASS`.

### Add a scene or shot field

1. Add the field to `_new_shot()` in `analyzer.py`.
2. Add it to `schemas/analysis.schema.json` under `$defs.shot.properties`.
3. Use it in `prompt_builder.build_shot_prompt()` if it should influence the prompt.
4. Project it in `handoff._shot_projection()` if it matters in production.

## 5. Debugging generation failures

| Symptom | Where to look |
|---|---|
| `ComfyUI unreachable` | `comfy-check`; is the server running on the same port? |
| `Workflow validation failed` | The `missing_nodes` / `missing_inputs` lists name the exact class or input. Compare with `GET /object_info/<ClassType>`. |
| `ComfyUI rejected the workflow` | The server's `node_errors` body explains the reason; the client surfaces it verbatim. |
| `ComfyUI execution failed` | The client raises `ComfyUIError` with the execution status messages. The ComfyUI console log has the node-level trace. |
| `Timed out after Ns` | The queue is busy or the model is too large for the VRAM. Check `system_stats.devices[].vram_free`. |
| Image saved but wrong subject | SD 1.5 limit. Check the stored `prompt` in the manifest next to the image, then adjust the style profile or use a larger checkpoint. |
| Image saved but wrong staging | Check the stored `reference_images` and `control_net` in the blocking manifest; the ControlNet strength is `control_strength` in `generation.py`. |
| Review UI shows a broken image | The image path is in the manifest as `image_path`; it is relative to the project directory. |

Every generation manifest is a complete diagnostic record. Read it before changing
code.

## 6. Testing

```powershell
.\.venv\Scripts\python -m pytest -q TESTS/test_visual_development.py -p no:cacheprovider
```

30 tests covering schemas, analysis, art direction, Style Bible, blocking, prompt
building, storage, the approved-script gate, the ComfyUI boundary (against an in-process
mock HTTP server), continuity checks and the handoff package.

The mock server test is deliberately hermetic: the suite does not need ComfyUI running.
Live generation was verified separately and is recorded in `EXAMPLE_PROJECT.md`.

## 7. Governance rules for this module

- Never modify the protected `CORE/`, `MODES/`, `SCHEMAS/`, `AGENTS/`, backend runtime
  or global workflow structures without an approved Change Request.
- Never write to `animation_forge.db`; open it read-only.
- Never mark a style, a shot or a package approved by the system itself.
- Never claim visual continuity, 3D geometry or production readiness that has not been
  verified.
