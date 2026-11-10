# Known Limitations

**Status:** Current limitations of the implemented module as of 2026-11-10. This file
describes what the module does and does not do, not what it might do later.

## What is now implemented (previously unavailable)

- A local ComfyUI instance **is** reachable and was verified live: ComfyUI 0.34.2 on
  `http://127.0.0.1:8188`, with `/system_stats`, `/object_info`, `/models/*`,
  `/upload/image`, `/prompt`, `/history` and `/view` all exercised.
- 26 real images were generated in the pilot: 8 art-direction candidates, 9 storyboard
  frames and 9 blocking references.
- The review UI serves the real generated files and records approve / reject /
  regenerate / select events.
- A complete production handoff package is exported as JSON and Markdown.

## Accuracy and capability limits

- **SD 1.5 cannot reliably compose several characters in one frame.** In the pilot the
  model usually produced one dominant subject per image. This is a model-capacity limit,
  not a prompting defect. A higher-capacity checkpoint (`sd_xl_base_1.0.safetensors` is
  installed but was not used) would compose more reliably at a VRAM and time cost.
- **Visual continuity is not verified.** The continuity report states
  `visual_identity_between_images: NOT_CHECKED`. There is no validated vision comparison
  model in this environment, so the module refuses to claim that characters, clothing or
  palette match between images. Prompt text, a shared seed and a shared Style Bible are
  cues, not guarantees.
- **No IP-Adapter, no depth, no pose, no segmentation conditioning.** Only the built-in
  `Canny` ControlNet is available. Reference-image conditioning of style or character
  identity is not implemented.
- **The 2D output contains no 3D data.** The blocking layout uses normalized 0..1 stage
  coordinates with no unit and no scale. It is not a Blender or Unreal transform, and
  the handoff states this explicitly.
- **`focal_length_mm` in the handoff is a nominal planning equivalent** of the shot
  size, not a measured lens value.
- **No automatic research or source verification.** The module does not look anything
  up and cannot establish that a claim is true.
- **No model-driven script writing.** The prompt assets are materials for a human/model
  workflow; there is no orchestrator that runs them.

## Scope boundaries of the pilot

- The pilot script `SCR_PROJECT_001_V01` is a 45-second fantasy comedy in a single
  location with three characters. It exercises characters, props, action and staging,
  but it does **not** test multi-location coverage, historical environments, large casts
  or long running times.
- Only one script in the database is `APPROVED` and immutable, so it was the only
  eligible pilot input. The ten YouTube experiment scripts and EP10 revision 2 are
  `AWAITING_HUMAN_REVIEW` and are correctly rejected by the approved-script gate.
- The analyzer's rules target the Animation Forge screenplay format (act headings,
  `INT./EXT.` scene headings, bold character cues). A materially different screenplay
  format would need new parsing rules, not new prompts.

## Scope boundaries of the review

- Decisions in the local review UI are **local creative decisions**. They are not
  Animation Forge GovernanceEngine approvals, they do not approve the screenplay, and
  they do not mark anything production-ready.
- Regeneration always creates a new revision; approved images are never overwritten,
  but the module does not garbage-collect superseded revisions.

## Environment limits observed on the verification machine

- `ComfyUI-Trellis2` cannot import (`No module named 'trimesh'`) and
  `ComfyUI-KJNodes/PatchTritonVAE` is skipped (`No module named 'triton'`). Neither is
  used by this module.
- The bundled `sdxlturbo_example.json` workflow references
  `sd_xl_turbo_1.0_fp16.safetensors`, which is **not** installed.
- The bundled ComfyUI workflows are UI-format files; the module builds its own
  API-format workflows instead.
- Port 8765 was already occupied on the verification machine, so the review UI defaults
  to 8790.
- The portable ComfyUI build needs `PYTHONUTF8=1` to avoid a Windows logger crash, and
  `ComfyUI-Manager` was left disabled so startup does not require network access.

## Inherent limits of the planned workflow

- Source access can be incomplete, paywalled, changed or biased. A claim ledger makes
  evidence review easier but does not prove evidence quality.
- Editorial judgments vary by reviewer and by audience.
- Word counts and pace assumptions do not predict final playback.
- A retention map reflects intended progression, not actual audience behaviour.
- A small sample cannot calibrate universal writing rules or scores.

## Shared repository boundaries

- Existing screenwriting review scores and no-score critique guidance are inconsistent; a
  shared schema must not be selected or modified without governance review.
- Existing screenplay pipeline stages do not replace research, claim verification or
  documentary-specific architecture.
- The existing `backend/integrations/comfyui_adapter.py` remains a provenance recorder,
  not a client. This module does not use it and does not change it.
- Any protected integration, including `CORE/`, `MODES/`, `SCHEMAS/`, `AGENTS/`, the
  backend runtime or the global workflow, requires the repository's approved change
  process.

## Manual steps a human still owns

1. Start ComfyUI before generating.
2. Decide which art direction to select, and approve the Style Bible.
3. Resolve the open questions the analyzer reports (for the pilot: the Act III location
   and time).
4. Compare the generated images for character and environment consistency; the tool
   deliberately does not do this.
5. Build the actual 3D environment, rig the characters, animate, and set the final
   cameras in Blender or Unreal.
6. Clear any rights or licence questions for the models, LoRAs and generated content.
