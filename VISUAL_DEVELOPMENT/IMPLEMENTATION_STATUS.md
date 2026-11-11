# Implementation Status

**Updated:** 2026-11-10
**Branch:** `visual-development-storyboard`
**State:** The local pipeline is implemented, tested and was run end to end against a
live local ComfyUI 0.34.2 instance. Two milestones remain open: integration into the
Animation Forge application, and any form of automated research or model-driven script
writing.

## What exists and is verified

### Code

| Area | Files | Verified by |
|---|---|---|
| Shared utilities | `common.py` | Unit tests + project-core smoke run |
| Approved-script loader | `approved_script.py` | Reads `animation_forge.db` read-only; rejects non-`APPROVED` and non-immutable records (tested) |
| Project store | `storage.py` | No-overwrite creation, immutable revisions, append-only events, orphan cleanup on manifest failure (tested) |
| Script analysis | `analyzer.py` | 3 sequences / 3 scenes / 9 shots; every source span slices back to the exact screenplay text (tested) |
| Art direction | `art_direction.py` | 8 profiles, one shared comparison scene and seed, exactly one selection (tested) |
| Style Bible | `style_bible.py` | Refuses to build without a human selection; revisions create new versions (tested) |
| Prompt builder | `prompt_builder.py` | Modular output; structured shot spec preserved separately (tested) |
| ComfyUI client | `comfyui_client.py` | Live generation through `/prompt`, `/history`, `/view`; hermetic mock-server test |
| Workflow templates | `workflows.py` | Two API-format templates; every node class and required input validated against the live `/object_info` (tested) |
| Generation | `generation.py` | 26 images generated with complete provenance manifests |
| Blocking | `blocking.py` | Deterministic normalized layout, JSON + SVG + PNG (tested) |
| Continuity | `continuity.py` | 8 checks; visual identity reported as `NOT_CHECKED` (tested) |
| Handoff | `handoff.py` | JSON + Markdown package with engine projections and explicit no-3D-geometry notes (tested) |
| Review UI | `review_server.py` | HTTP 200 dashboard, real image bytes served, path traversal refused, approve/reject/regenerate recorded |
| CLI | `cli.py` | 13 subcommands, used for the whole pilot |

### Schemas

`project`, `review_event`, `generation_manifest`, `analysis`, `candidate`,
`style_bible` — all Draft 2020-12, all validated in the test suite.

### Pilot

A complete run on `SCR_PROJECT_001_V01` (the only `APPROVED` screenplay in the
database) produced **26 real images** through the local ComfyUI instance: 8 art-direction
candidates, 9 storyboard frames and 9 blocking references, plus 9 deterministic blocking
layouts. Details, timings and the exact file paths are in `EXAMPLE_PROJECT.md`.

## Live ComfyUI status

Verified at run time, not assumed:

- ComfyUI **0.34.2**, frontend 1.49.6, python 3.13.9, pytorch 2.9.1+cu130, win32.
- GPU NVIDIA GeForce RTX 4060 Laptop GPU, VRAM 8 585 216 000 total / 7 411 204 096 free
  at idle, RAM 12 554 305 536 total.
- Checkpoints `dreamshaper_8.safetensors` and `sd_xl_base_1.0.safetensors`; LoRA
  `arcane_offset.safetensors`; ControlNet `control_v11p_sd15_canny.pth`.
- Measured generation time at 768x768: about 8 s per image with the model resident
  (about 18 s for the first image of a session), 12-16 s for the ControlNet branch.

The portable build was started with:

```powershell
$env:PYTHONUTF8='1'; .\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --fast fp16_accumulation --port 8188 --disable-auto-launch
```

Two custom nodes fail to import in this build (`ComfyUI-Trellis2` needs `trimesh`,
`ComfyUI-KJNodes/PatchTritonVAE` needs `triton`). Neither is used by this module.

## Not implemented and not claimed

- No automatic research or source verification.
- No model-provider or prompt orchestration. The prompt assets are for a human/model
  workflow.
- No vision-based continuity metric. Image-to-image identity is `NOT_CHECKED` by
  design.
- No 3D scene, measured coordinates, `.blend` file, Sequencer or engine automation. The
  handoff carries shot intent and references only.
- The module is now reachable from the Animation Forge app through
  `backend/integrations/visual_development.py` and four token-protected
  `/api/visual-development/*` routes. That bridge is **read-mostly**: it lists
  projects, serves the real image files and records review decisions in the module's
  own append-only event log. It never writes to `animation_forge.db`, and it adds no
  table, no protected instruction file and no agent definition.
- The pilot script is short and single-location, so multi-location and historical
  environment coverage is untested.
- No approved style, shot or package. Every generated image is a draft until a human
  decides.

## Defects found and fixed during the pilot

1. Shot ids were not globally unique (`SHT_001` repeated in every sequence). The
   analyzer now derives ids from sequence and scene; the pilot was regenerated.
2. The review UI stored the literal action name `APPROVE` while the handoff filtered on
   `APPROVED`, so approved images were missing from the package. Now mapped to
   `APPROVED` / `REJECTED`.
3. A failed generation-manifest write left an orphan PNG behind. `write_generation_artifact`
   now removes the image when the manifest cannot be written.
4. The review page served a blank shell. An inline `onerror="..."` attribute on the
   image markup put a raw double quote inside a double-quoted JavaScript string, so the
   browser refused to parse the whole script block. The page now carries **no inline
   event handler at all**: image errors are handled by a delegated capture-phase
   listener, because image error events do not bubble.
5. The renderer filled the tab sections but never switched the `active` class, and the
   stylesheet hides every section that does not carry it. The page rendered its
   content and showed nothing. `render()` now toggles the class.
6. The `composition` and `atmosphere` rules of a Style Bible were verbatim copies of
   `camera_language` and `lighting`. Every style profile now carries its own
   composition and atmosphere direction. The pilot's Style Bible v1 still holds the
   duplicated text, because `atmosphere` feeds the shot prompts: re-versioning it
   would describe images that were generated under different rules.
7. The project manifest reported `SOURCE_IMPORTED` for the whole life of a project.
   The CLI now advances the stage as the pipeline progresses.

## Verification performed

- `pytest TESTS/test_visual_development.py TESTS/test_visual_development_bridge.py` ->
  **58 passed** (including a suite that fetches the review page over real HTTP,
  parses its script with `node --check`, asserts that the served page carries no
  inline event handler, and renders the page in a real headless browser to prove the
  gallery is visible).
- Live ComfyUI: health, node discovery, model discovery, workflow validation, queue
  submission, status polling, image retrieval and reference upload all exercised
  against the running server.
- Review UI exercised over HTTP: dashboard, real image bytes, refused path traversal,
  approve / reject / regenerate actions, and persisted `review_status`.
- Review UI exercised in a real browser (Edge headless): the six tabs, the eight
  art-direction candidates with their generated images, and the selection buttons all
  render.
- Continuity report on the pilot: 6 PASS, 0 FAIL, 1 REVIEW, 1 NOT_CHECKED.
- Repository-prescribed checks are recorded in the root `AGENTS.md`.

## Next steps

1. Keep the app bridge read-mostly until a Change Request per `CORE/CHANGE_CONTROL.md`
   says otherwise.
2. Pilot a second, longer script with multiple locations to test the analyzer and the
   continuity checks more honestly.
3. Add reference-image conditioning (IP-Adapter) if a model becomes available, then
   benchmark it before claiming any continuity improvement.
4. Add a Blender camera-export adapter only after a measured scale and coordinate
   convention exist and are tested.
