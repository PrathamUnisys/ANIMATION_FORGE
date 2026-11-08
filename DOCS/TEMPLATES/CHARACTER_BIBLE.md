---
prompt_id: TEMPLATE_DOC_CHARACTER_BIBLE
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable character identity, design, continuity, and production reference template
dependencies: ["TEMPLATE_DOC_STORY_BIBLE", "SCHEMAS/ASSET.schema.json", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable character bible template
document_type: reusable_document_template
---
# TEMPLATE — CHARACTER BIBLE

> Reusable design/reference template, not an executable agent prompt or an approved design. Record proposals separately from human-approved identity locks.

## Record and role
- **Project / character ID / name**: `[PROJECT; CHAR_ID; NAME]`
- **Revision / owner / date**: `[VERSION; OWNER; DATE]`
- **Narrative role / source**: `[ROLE; STORY-BIBLE OR SCRIPT REVISION]`
- **Approval state and human decision reference**: `[STATE; REVIEWER; DATE; RATIONALE]`

## Character profile
- **Story function / goal / conflict**: `[DETAIL]`
- **Personality expressed through behavior and design**: `[DETAIL]`
- **Age range / scale / physical constraints**: `[DETAIL OR UNKNOWN]`
- **Silhouette / proportions / distinctive features**: `[DETAIL]`
- **Palette / materials / surface treatment**: `[DETAIL]`
- **Costume / accessories / props**: `[DETAIL; STATE CHANGES]`
- **Expression range / readable emotional cues**: `[DETAIL]`
- **Movement / pose constraints**: `[DETAIL]`
- **Voice identity and pronunciation references**: `[LINK TO VOICE PROFILE; DO NOT INVENT RECORDING]`

## Continuity locks
| Feature | Approved value / invariant | Reference asset or decision | Change permitted? |
|---|---|---|---|
| `[FEATURE]` | `[DETAIL]` | `[ID / REVISION]` | `[ONLY VIA HUMAN-REVIEWED REVISION]` |

## Asset and use references
| Asset ID / revision | View / purpose | File location | Approval status | Dependencies / license |
|---|---|---|---|---|
| `[ASSET_ID]` | `[VIEW]` | `[PATH OR NOT YET CREATED]` | `[STATE]` | `[DETAIL]` |

Use `SCHEMAS/ASSET.schema.json` for each structured asset record. No dedicated character-bible schema exists.

## Open items and review
- **Unresolved design questions / risks**: `[ITEM; OWNER; IMPACT]`
- **Review checklist**: `[SILHOUETTE, CONSISTENCY, SCALE, STYLE, USE CASE]`
- **Human decision**: `[PROPOSED / AWAITING_HUMAN_REVIEW / APPROVED / REVISION_REQUESTED / REJECTED]`
- **Revision summary and affected consumers**: `[WHAT CHANGED; SHOTS/SCENES/ASSETS]`
