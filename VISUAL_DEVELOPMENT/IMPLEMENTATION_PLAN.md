# Implementation Plan and Progress

**Status:** The local pipeline is implemented and was run end to end against a live
ComfyUI instance. The frontend milestone and the governance integration milestone remain
open. See `TASK_BACKLOG.md` and `IMPLEMENTATION_STATUS.md`.

## Milestones

| Milestone | Scope | State |
|---|---|---|
| M0: repository and R&D | Inspect governance, existing interfaces, schemas, approved input, ComfyUI and engine evidence; write research and decisions | **Complete.** ComfyUI was unreachable at first; it was later located, started and verified live. |
| M1: isolated project core | Approved-script loader, immutable project package, internal contracts, parser, stable breakdown IDs, explicit fact/inference tracking | **Complete.** Six module schemas, read-only approved-script loader, file-backed store, deterministic analyzer with source spans and open questions. |
| M2: art direction and Style Bible | 6-8 structured profiles from one scene; comparison manifests; human selection; versioned style bible | **Complete.** 8 profiles, shared comparison scene and seed, single selection enforced, versioned Style Bible with immutable global rules and scene variables. |
| M3: ComfyUI and prompt pipeline | Configurable API-format workflows/bindings, node/model checks, queue/status/retrieval, reference upload, provenance, retries | **Complete.** Two API-format workflow templates, live `/object_info` validation, queue/poll/retrieve, image upload, full provenance, hermetic mock test. |
| M4: storyboard/blocking/handoff | Separate storyboard and spatial blocking outputs; continuity validation; Blender/Unreal handoff | **Complete.** 9 storyboard images, 9 deterministic blocking layouts (JSON/SVG/PNG), 9 ControlNet-rendered blocking references, 8 continuity checks, JSON + Markdown handoff with engine projections. |
| M5: review frontend | Local gallery and controls for candidate selection, Style Bible review, per-shot decisions, regeneration and job status | **Complete as a standalone loopback tool.** Not integrated into the Animation Forge React app (needs an approved Change Request). |
| M6: real approved-script pilot | Run end-to-end on `SCR_PROJECT_001_V01`; record actual ComfyUI status, images, failures and manual steps | **Complete.** 26 real images generated; 2 defects found and fixed; see `EXAMPLE_PROJECT.md`. |
| M7: verification and delivery | Module tests, global prescribed checks, docs, limitations, diff/status, commit and review branch | **In progress.** 30 module tests pass. The repository-prescribed checks, the documentation set and the commit are finished in this change. |

## Out of scope for this module

- Automatic web research or source truth verification.
- Model-driven script writing. The prompts are assets for a human/model workflow, not an
  integrated engine.
- A vision-based continuity metric. Image identity is reported as `NOT_CHECKED`.
- Any 3D scene, measured coordinates or engine-side automation.
- Integration into the Animation Forge backend, database or React app.

## Rules for this implementation

- Use only approved screenplay records as source input; never rewrite them.
- Do not call the existing simulated ComfyUI/Blender/Unreal adapters live.
- Do not modify protected architecture, global schemas, database tables, existing APIs or
  the React app without a separately approved Change Request.
- Do not mark creative work approved or production-ready.
- Treat all generated concepts and shots as drafts until the local human reviewer
  decides.
- Run the repository-prescribed tests/validator after changes and restore only known
  test-generated files.
