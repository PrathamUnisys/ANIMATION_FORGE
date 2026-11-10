# Implementation Plan and Progress

## Milestones

| Milestone | Scope | State |
|---|---|---|
| M0: repository and R&D | Inspect governance, existing interfaces, schemas, approved input, ComfyUI and engine evidence; write research and decisions | Complete (local ComfyUI not reachable) |
| M1: isolated project core | Approved-script loader, immutable project package, internal contracts, parser, stable breakdown IDs, explicit fact/inference tracking | Partial checkpoint only: path/hash utilities, read-only approved-script loader, and file-backed store exist; schemas and analyzer are missing, so project creation is not yet runnable. |
| M2: art direction and Style Bible | 6–8 structured profiles from one scene; comparison manifests; human selection; versioned style bible | Pending |
| M3: ComfyUI and prompt pipeline | Configurable API-format workflows/bindings, node/model checks, queue/status/retrieval, reference upload, provenance, retries | Pending; live endpoint unavailable |
| M4: storyboard/blocking/handoff | Separate storyboard and spatial blocking outputs; continuity validation; Blender/Unreal handoff | Pending |
| M5: review frontend | Local gallery and controls for candidate selection, Style Bible review, per-shot decisions, regeneration and job status | Pending |
| M6: real approved-script pilot | Run end-to-end on `SCR_PROJECT_001_V01`; record actual ComfyUI status, images, failures and manual steps | Pending |
| M7: verification and delivery | Module tests, global prescribed checks, docs, limitations, diff/status, commit and review branch | Not started; only repository baseline checks were run for the documentation checkpoint. |

## Rules for this implementation

- Use only approved screenplay records as source input; never rewrite them.
- Do not call the existing simulated ComfyUI/Blender/Unreal adapters live.
- Do not modify protected architecture, global schemas, database tables, existing APIs, or the React app without a separately approved Change Request.
- Do not mark creative work approved or production-ready.
- Treat all generated concepts and shots as drafts until the local human reviewer decides.
- If ComfyUI remains unavailable, complete and test the client against a local mock HTTP server, then state live image generation is blocked and list exact activation steps.
- Run the repository-prescribed tests/validator after changes and restore only known test-generated files.
