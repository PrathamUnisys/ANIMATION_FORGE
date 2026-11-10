# Prompt Engineering Guide

How prompts are constructed in this module, why they are modular, and what each part
controls.

---

## 1. Principle: one fixed paragraph template does not work

A single fixed prompt string forces the style, the story content and the camera into the
same sentence, so changing the camera rewrites the style and changing the style
rewrites the scene. This module instead assembles named modules and keeps the
structured shot specification separate from the rendered prompt string.

Two things are always kept apart:

- **`shot_spec`** — the structured shot record from the analysis (purpose, environment,
  characters, positions, actions, props, camera, composition, lighting, duration,
  complexity, source spans). This is the truth about what the shot is for.
- **`prompt`** — the assembled text actually sent to ComfyUI.

Every generation manifest stores both, so a reviewer can always tell what was asked for
independently of how it was phrased.

## 2. The modules

`VISUAL_DEVELOPMENT/prompt_builder.py` assembles these modules.

| Module | Source | Purpose |
|---|---|---|
| `style` | Style Bible `global_rules.positive_prompt` | The immutable visual identity. Always present. In blocking mode it is prefixed with "production blocking reference render, previs staging view". |
| `scene_context` | Scene heading and time of day | Where and when. |
| `environment` | Scene location | The space itself. |
| `characters` | Shot character list + the script's own appearance text | Identity, pulled from the screenplay, e.g. "Sir Pip (20s, earnest squire in oversized dented pauldrons)". |
| `action` | Shot visual description and character actions | What is happening. |
| `objects` | Shot prop list | The story props that must read. |
| `camera` | Shot type, angle, perspective, movement | The framing. |
| `composition` | Composition plus foreground / middle ground / background | Depth structure. |
| `lighting` | Style Bible lighting + shot lighting + weather | Light direction and quality. |
| `atmosphere` | Style Bible atmosphere and materials | Overall mood and surface response. |
| `emphasis` | Shot purpose | The narrative beat the image must carry. |

Modules are joined with `, `. Empty modules are dropped, so a shot without weather does
not get a stray weather clause.

## 3. Character identity comes from the script

The analyzer extracts character appearance from the screenplay itself:

```text
SIR PIP (20s, earnest squire in oversized dented pauldrons)
GLOOP (translucent emerald slime familiar wearing a tiny monocle)
STONE GOLEM BAILIFF (3 meters tall, mossy basalt plates, glowing amber eyes)
```

These are stored in the analysis `characters` registry with source spans and are injected
into every prompt that contains that character. This keeps the prompt grounded in the
approved script rather than in an invented description.

## 4. The negative prompt

The negative prompt is the Style Bible `negative_prompt` (identity drift, extra
characters, changing outfits, unreadable composition, watermark, text, anatomy errors,
cropping) plus mode-specific additions:

- storyboard: duplicate character, crowd, floating objects, inconsistent lighting
  direction.
- blocking: text overlay, annotation labels, photorealistic skin, busy background.

Keeping the negative prompt in the Style Bible means a style change can also tighten or
relax the negative prompt once, for every later shot.

## 5. Style conditioning and its limits

Three conditioning paths exist in this environment:

1. **Prompt text** — always available. It is a cue, not a guarantee.
2. **ControlNet Canny** — used for blocking. The deterministic layout PNG is uploaded to
   `/upload/image` and fed through the built-in `Canny` node, so the rendered blocking
   image follows the staging.
3. **LoRA** — `arcane_offset.safetensors` at strength 0.65 is available and used by the
   default text-to-image workflow.

**IP-Adapter is not available here** (no model, no custom node). Reference-image
conditioning for style or character identity is therefore not implemented, and no
continuity guarantee is claimed from prompt text alone.

The continuity report deliberately reports image-to-image identity as `NOT_CHECKED`.

## 6. Seeds

- **Art-direction comparison:** one shared seed for every candidate. Differences between
  candidates come from the style description, not from sampling noise. This is what makes
  the comparison meaningful.
- **Storyboard / blocking:** a deterministic per-shot seed derived from the base seed in
  the Style Bible and the shot id:

  ```python
  seed = (base_seed + sum(ord(c) for c in shot_id) * 7919) % 2**53
  ```

  The same shot therefore reproduces the same image, and two different shots never
  collide. Re-running `storyboard` for one shot produces the same result; the
  **Regenerate** button in the review UI deliberately advances the seed to get a
  different take.

## 7. Model and sampler settings

The default Style Bible generation settings, verified on an RTX 4060 Laptop (8 GB VRAM):

```json
{
  "model": "dreamshaper_8.safetensors",
  "lora": "arcane_offset.safetensors",
  "lora_strength": 0.65,
  "width": 768,
  "height": 768,
  "steps": 25,
  "cfg": 8.0,
  "sampler": "euler",
  "scheduler": "simple",
  "seed": 536354036775427
}
```

Measured generation time for a 768x768 image on that machine: **about 8 seconds** with
the model resident in VRAM (the first image of a session pays the model load, roughly
18 s).

SD 1.5 cannot reliably compose several characters in one frame. In the pilot the model
usually chose one dominant subject per image. This is a model-capacity limit, not a
prompting bug, and it is the main reason the blocking layout exists as a separate,
deterministic record of staging.

## 8. Changing the prompt system

- **New style identity:** add or edit a profile in `STYLE_PROFILES` in
  `art_direction.py`. Each profile needs a `prompt_suffix` plus the descriptive fields
  that are stored in the candidate set.
- **New prompt module:** add a key to the `modules` dictionary in `build_shot_prompt()`
  and add the corresponding field to the shot record in the analyzer.
- **Different negative guidance:** edit `global_rules.negative_prompt` in the Style
  Bible. It applies to every later shot.
- **Different model:** change `generation_settings.model` in the Style Bible. The model
  name is recorded in every manifest, so existing images keep pointing at the model that
  produced them.

## 9. Reproducing a specific image

Every manifest records enough to reproduce an image: prompt, negative prompt, model,
LoRA and strength, seed, width, height, steps, cfg, sampler, scheduler, ControlNet name
and strength, reference image names, workflow id, and the ComfyUI prompt id.

To reproduce one, rebuild the workflow from `workflows.py` with those values and submit
it to `POST /prompt` on the same ComfyUI instance. The image SHA-256 is stored next to
the file so a reproduction can be compared byte for byte.
