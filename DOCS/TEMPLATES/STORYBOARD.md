---
prompt_id: TEMPLATE_DOC_STORYBOARD
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable storyboard sequence and panel annotation template
dependencies: ["TEMPLATE_DOC_SCREENPLAY", "TEMPLATE_DOC_SHOT_LIST", "SCHEMAS/SHOT.schema.json", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable storyboard template
document_type: reusable_document_template
---
# TEMPLATE — STORYBOARD

> Reusable storyboard documentation template, not an executable agent prompt or an assertion that panels/animatic have been produced. Insert actual panel files only when available.

## Sequence record
- **Project / sequence / scene IDs**: `[IDS]`
- **Approved screenplay revision / source shot plan**: `[REFERENCES]`
- **Storyboard revision / owner / date**: `[DETAIL]`
- **Aspect ratio / intended frame rate**: `[TARGETS]`
- **Status / human gate**: `[PROVISIONAL / AWAITING HUMAN REVIEW / APPROVED / REVISION REQUESTED / REJECTED]`

## Panels
| Panel / shot ID | Panel image path or “not created” | Framing / camera | Staging and action | Expression / eyeline | Dialogue / sound | Duration / transition |
|---|---|---|---|---|---|---|
| `[SHT_ID]` | `[PATH OR NOT CREATED]` | `[DETAIL]` | `[DETAIL]` | `[DETAIL]` | `[LINE / CUE]` | `[SECONDS; TRANSITION]` |

## Sequence continuity
- **Geography / screen direction / eyelines**: `[DETAIL]`
- **Character, prop, and environment continuity**: `[REFERENCES AND CHECKS]`
- **Pacing and approximate scene duration**: `[ESTIMATE AND METHOD]`
- **Missing coverage / assumptions / open decisions**: `[DETAIL]`
- **Dependencies and required assets**: `[IDS; SEE SCHEMAS/ASSET.schema.json]`

## Animatic (if actually available)
- **Animatic file / revision / status**: `[PATH AND SOURCE OR NOT CREATED]`
- **Timing and audio references**: `[DETAIL]`
- **Assembly capability used / provenance**: `[OBSERVED TOOL DETAILS OR NOT AVAILABLE]`
- **Checks performed and findings**: `[CHECK; RESULT; NOT RUN WHERE APPLICABLE]`

## Review and handoff
- **Reviewer / human decision / date / comments**: `[RECORD]`
- **Requested changes by panel ID**: `[DETAIL]`
- **Handoff notes to Animation / Audio / Previs**: `[DETAIL]`

Structured camera/shot fields may map to `SCHEMAS/SHOT.schema.json`; there is no dedicated storyboard schema. Technical or panel-completeness checks do not grant the storyboard/animatic human approval.
