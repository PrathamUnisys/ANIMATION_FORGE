---
prompt_id: TEMPLATE_DOC_SHOT_LIST
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable shot breakdown and continuity tracking template
dependencies: ["TEMPLATE_DOC_SCREENPLAY", "SCHEMAS/SCENE.schema.json", "SCHEMAS/SHOT.schema.json"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable shot-list template
document_type: reusable_document_template
---
# TEMPLATE — SHOT LIST

> Reusable planning document, not an executable agent prompt or proof that shots have been generated. Use stable IDs and distinguish estimates from measured values.

## Sequence metadata
- **Project / sequence / scene ID**: `[IDS]`
- **Approved screenplay revision / storyboard revision**: `[SOURCE REFS]`
- **Shot-list revision / owner / date**: `[DETAIL]`
- **Animation method / runtime target**: `[2D | 2.5D | 3D | HYBRID; TARGET]`
- **Review status / decision**: `[STATE; HUMAN REVIEW REFERENCE IF ANY]`

## Shots
| Shot ID | Scene ID / beat | Shot size / angle | Camera position / movement / focal length (mm) | Characters / placement / action | Duration (sec) | Audio cues | Required assets | Continuity / notes |
|---|---|---|---|---|---:|---|---|---|
| `[SHT_ID]` | `[SCENE; PURPOSE]` | `[DETAIL]` | `[DETAIL]` | `[IDS AND ACTION]` | `[ESTIMATE]` | `[CUES]` | `[ASSET IDS]` | `[NOTES]` |

## Scene breakdown and dependencies
- **Location ID / scene title**: `[ID; TITLE]`
- **Character IDs**: `[IDS]`
- **Lighting / VFX / production dependencies**: `[DETAIL]`
- **Expected outputs**: `[PLANNED DELIVERABLES; NOT CLAIMS OF COMPLETION]`
- **Duration total / estimation assumptions**: `[TOTAL; METHOD]`
- **Open questions / blockers**: `[OWNER; IMPACT; RESOLUTION NEEDED]`

Structured scene entries use `SCHEMAS/SCENE.schema.json`; structured shot entries use `SCHEMAS/SHOT.schema.json`. The shot schema requires `shot_id`, `scene_id`, `camera_angle`, `shot_size`, `camera_movement`, `focal_length_mm`, `duration_sec`, `fps`, and `resolution`.

## Review and revision
- **Continuity/coverage review**: `[FINDINGS]`
- **Human review status/comments**: `[RECORD; NO AUTO-APPROVAL]`
- **Change summary and affected shots**: `[DETAIL]`
