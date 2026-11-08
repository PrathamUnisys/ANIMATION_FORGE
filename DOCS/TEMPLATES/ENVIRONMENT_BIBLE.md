---
prompt_id: TEMPLATE_DOC_ENVIRONMENT_BIBLE
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable environment and location design, geography, and continuity template
dependencies: ["TEMPLATE_DOC_STORY_BIBLE", "SCHEMAS/SCENE.schema.json", "SCHEMAS/ASSET.schema.json"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable environment bible template
document_type: reusable_document_template
---
# TEMPLATE — ENVIRONMENT BIBLE

> Reusable location reference template, not an executable agent prompt or an approved environment design. Distinguish approved world facts from proposals.

## Record
- **Project / location ID / name**: `[PROJECT; LOCATION_ID; NAME]`
- **Revision / owner / date / state**: `[VERSION; OWNER; DATE; APPROVAL STATE]`
- **Narrative purpose / source scenes**: `[PURPOSE; SCENE IDS AND SCRIPT REVISION]`
- **Human decision reference**: `[REVIEWER; DATE; DECISION; RATIONALE OR NONE]`

## Location design
- **Layout / geography / entrances and exits**: `[DESCRIBE RELATIONSHIPS; ADD DIAGRAM REFERENCE IF AVAILABLE]`
- **Landmarks / key props / interaction zones**: `[DETAIL]`
- **Scale and character access**: `[MEASUREMENTS OR QUALIFIED ESTIMATES]`
- **Materials / palette / architectural language**: `[DETAIL]`
- **Atmosphere / weather / time-of-day variants**: `[DETAIL]`
- **Lighting direction, sources, and continuity**: `[DETAIL]`
- **Camera, staging, and visibility constraints**: `[DETAIL]`
- **Sound/acoustic considerations**: `[DETAIL; NOT A RECORDED AUDIO CLAIM]`

## World and continuity rules
| Fact or invariant | Approved source / decision | Scenes affected | Open question |
|---|---|---|---|
| `[FACT]` | `[SOURCE]` | `[SCENE IDS]` | `[QUESTION OR NONE]` |

## Scene and asset references
- **Structured scene/location requirements**: `[SCENE IDS; SEE SCHEMAS/SCENE.schema.json]`
- **Location asset records**: `[ASSET IDS, REVISIONS, FILE LOCATIONS; SEE SCHEMAS/ASSET.schema.json]`
- **Required variants / dependencies**: `[SHOT, CHARACTER, PROP, OR TOOL DEPENDENCIES]`
- **Uncreated or unavailable outputs**: `[STATE CLEARLY]`

## Review and changes
- **Continuity / feasibility findings**: `[FINDINGS]`
- **Proposed change / affected revisions**: `[CHANGE AND IMPACT]`
- **Human review status and comments**: `[STATE; REVIEWER; DATE; COMMENTS]`

No dedicated environment-bible schema is defined; the scene and asset schemas cover only applicable structured records.
