---
prompt_id: TEMPLATE_DOC_ANIMATION_SPECIFICATION
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable shot-level animation and camera specification template
dependencies: ["TEMPLATE_DOC_SHOT_LIST", "SCHEMAS/SHOT.schema.json", "SCHEMAS/ASSET.schema.json"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable animation specification template
document_type: reusable_document_template
---
# TEMPLATE — ANIMATION SPECIFICATION

> Reusable planning/specification template, not an executable agent prompt, render instruction, or claim that animation has been executed.

## Shot record
- **Project / scene ID / shot ID / revision**: `[IDS]`
- **Source screenplay / approved storyboard revision**: `[REFERENCES]`
- **Animation method**: `[2D | 2.5D | 3D | HYBRID]`
- **Status / reviewer / human decision**: `[STATE OR NONE]`

## Required shot fields
- **Camera angle / shot size / position / movement**: `[SPECIFY; USE SCHEMAS/SHOT.schema.json]`
- **Focal length (mm)**: `[NUMBER OR N/A WITH REASON]`
- **Duration (seconds) / frame rate (fps) / resolution**: `[TARGET VALUES; DO NOT REPORT AS MEASURED]`
- **Character placement / action / facial expression**: `[DETAIL AND CHARACTER IDS]`
- **Lighting and environment state**: `[DETAIL; LOCATION ID]`
- **Audio cues / sync dependencies**: `[LINE OR CUE IDS; EXPECTED TIMING]`
- **Required assets**: `[ASSET IDS AND REVISIONS]`

## Execution plan and constraints
- **Blocking / timing / start-end states**: `[DETAIL]`
- **Approved toolchain profile and workflow**: `[REFERENCE OR NOT SELECTED]`
- **Inputs / dependencies / expected outputs**: `[FILES AND IDS; MARK UNAVAILABLE ITEMS]`
- **Technical constraints / assumptions**: `[DETAIL]`
- **Capability status**: `[AVAILABLE AND CONFIGURED / UNVERIFIED / UNAVAILABLE]`

## Inspection record
| Check | Expected value | Observed result / evidence | Status |
|---|---|---|---|
| `[CONTINUITY / COMPLETENESS / FRAME RATE / SYNC / OTHER]` | `[EXPECTATION]` | `[EVIDENCE OR NOT CHECKED]` | `[PASS / ISSUE / NOT RUN]` |

## Revision and approval
- **Defects / affected frames or elements**: `[DETAIL]`
- **Targeted correction**: `[CHANGE; PRESERVE UNAFFECTED APPROVED WORK]`
- **Technical QC outcome**: `[OUTCOME OR NOT RUN; NEVER CREATIVE APPROVAL]`
- **Human review decision / comments / date**: `[SEPARATE HUMAN DECISION]`

Use `SCHEMAS/SHOT.schema.json` for structured shot data and `SCHEMAS/ASSET.schema.json` for produced asset records. Never represent a plan as a rendered result.
