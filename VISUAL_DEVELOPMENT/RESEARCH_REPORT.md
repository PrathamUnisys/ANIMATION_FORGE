# Visual Development and Storyboard System — R&D Report

**Research date:** 2026-11-10
**Status:** Desk research and local inspection; implementation and integration tests are tracked separately.

## Repository evidence

- Existing `SCHEMAS/SCENE.schema.json` and `SCHEMAS/SHOT.schema.json` cover basic production fields but do not carry the full screenplay passage, sequence, interpretation, provenance, generation, or review history required by this module. They remain unchanged.
- `backend/integrations/comfyui_adapter.py` validates against hard-coded model/node names and writes supplied image bytes to disk. It does not contact ComfyUI. `check_connection_health()` trusts a caller-provided boolean. This module will not reuse it as evidence of live integration.
- Existing department rules correctly make storyboard/animatic decisions human-reviewed. The project-level capability registry says current app image/storyboard output is demo data.
- The only script row in `animation_forge.db` marked `APPROVED` is immutable `SCR_PROJECT_001_V01` (PROJECT_001, 45-second fantasy comedy, one throne-room location, three characters). The ten YouTube scripts are editorial drafts; EP10 screenplay revision 2 is `PROPOSED`. They are not valid pilot inputs under the approved-script gate.
- ComfyUI at `http://127.0.0.1:8188` did not answer `/system_stats` or `/object_info` during this inspection; no listener on port 8188 or ComfyUI process was found. No live generation result is claimed.
- The test venv has Python 3.12, Pillow 11.3.0, and jsonschema 4.26.0. Existing framework tests rewrite nine tracked demo files plus `CORE/GLOBAL_WORKFLOW.md`; restore only those known side effects after test runs.

## Research findings

### Art direction and consistency

Text prompts alone are a weak way to specify a visual identity. A useful art-direction comparison must hold the story content, reference composition, dimensions, generation workflow, and seed constant while changing a clearly described bundle of visual properties: medium, shape language, palette, material, light, and camera treatment. Each candidate must use the same representative scene so that differences are attributable to direction rather than subject matter.

After selection, a Style Bible should express stable episode-wide rules separately from shot variables. Each image request can combine that Bible with a shot's own passage, staging, and camera plan. Optional image-reference conditioning can strengthen style or subject cues; it cannot promise exact identity or geometry. IP-Adapter research describes image and text conditioning together, while noting that image-prompt methods can be only partially faithful. ControlNet research supports structural inputs such as edges, pose, segmentation, and depth, but requires a compatible model/workflow and does not turn a 2D control into validated 3D coordinates.

### Storyboard versus blocking

- **Concept art** explores what a world, character, or material language might look like. It need not correspond to a final shot.
- **Storyboard** is a cinematic image for one shot: subject, action, emphasis, and composition.
- **Blocking reference** prioritizes spatial relationships: stage layout, subject/object positions, camera location/direction, and movement. A top-down diagram can encode those relationships explicitly; a generated perspective image is only an illustrative view.
- **Production layout** is a constructed 3D scene with measured coordinates and camera transforms. This module does not produce or validate that scene.

The module will generate a deterministic 2D blocking diagram from normalized positions and camera direction, then optionally pass that diagram to a configured ComfyUI workflow for a visualized blocking reference. The diagram is the more reliable staging record; neither output is labeled as exact Blender or Unreal coordinates.

### ComfyUI

ComfyUI's documented local server routes include `/prompt` for validated queue submission; `/queue` and `/history/{prompt_id}` for status; `/view` for output retrieval; `/upload/image` for reference images; `/object_info` and `/models/{folder}` for runtime discovery; and `/ws` for live progress events. The system will use the built-in HTTP routes and bounded status polling first. This avoids making WebSocket support a prerequisite while preserving queue/error reporting. It will read workflow JSON exported in API format and apply explicit configured input bindings rather than guessing node IDs or assuming custom nodes.

The default workflow must use only the workflow's own configured nodes and model. IP-Adapter, ControlNet/depth/pose, LoRA, or inpainting are optional workflow capabilities, not hard dependencies. There is no automatic model download, custom-node install, or license assertion. If a selected workflow requires a node/model that is missing, validation must show that error before queuing.

### Blender and Unreal handoff

Blender's camera view is a direct way to compose and preview a camera frame; lens/FOV and camera transforms belong in shot data. Unreal's Sequencer supports camera cuts and Control Rig animation. Therefore the handoff should carry camera intent and measured source values when they exist, while leaving actor creation, environment construction, real coordinates, rigging, animation, and final camera validation to the 3D production stage. Existing app adapters are simulations and are not used as a production exporter.

## Sources

Primary sources and implementation evidence:

1. Comfy-Org, [ComfyUI Server Routes (HTTP and WebSocket API)](https://github.com/Comfy-Org/docs/blob/main/development/comfyui-server/comms_routes.mdx), accessed 2026-11-10.
2. Comfy-Org, [ComfyUI OpenAPI definition](https://github.com/Comfy-Org/ComfyUI/blob/master/openapi.yaml), accessed 2026-11-10.
3. Ye et al., [IP-Adapter: Text Compatible Image Prompt Adapter for Text-to-Image Diffusion Models](https://arxiv.org/abs/2308.06721), 2023.
4. Zhang et al., [Adding Conditional Control to Text-to-Image Diffusion Models (ControlNet)](https://arxiv.org/abs/2302.05543), 2023.
5. Blender Foundation, [Blender 5.2 Camera Manual](https://docs.blender.org/manual/en/latest/render/cycles/object_settings/cameras.html) and [Camera View Manual](https://docs.blender.org/manual/en/latest/editors/3dview/navigate/camera_view.html), accessed 2026-11-10.
6. Epic Games, [How to Animate with Sequencer, Unreal Engine 5.8](https://dev.epicgames.com/documentation/unreal-engine/how-to-animate-with-sequencer), accessed 2026-11-10.
7. Local evidence: `backend/integrations/comfyui_adapter.py`, `backend/integrations/blender_unreal_adapters.py`, `DEPARTMENTS/STORYBOARD/DEPARTMENT_RULES.md`, `DEPARTMENTS/PREVIS/DEPARTMENT_RULES.md`, `SCHEMAS/SCENE.schema.json`, `SCHEMAS/SHOT.schema.json`, and read-only queries against `animation_forge.db`.

Research is not a claim that any model, node, local server, or generated image has been tested live. Live ComfyUI execution remains a required validation once a reachable instance and selected API workflow are available.
