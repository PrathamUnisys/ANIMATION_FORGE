---
prompt_id: TEMPLATE_DOC_PROJECT_BRIEF
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable human-authored project brief template; aligns project metadata with SCHEMAS/PROJECT.schema.json
dependencies: ["SCHEMAS/PROJECT.schema.json", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable project brief template
document_type: reusable_document_template
---
# TEMPLATE — PROJECT BRIEF

> Reusable document template, not an executable agent prompt or a completed/approved brief. Replace bracketed instructions; identify assumptions and obtain required human decisions.

## Project identity
- **Project ID** [Use `PROJECT_...` format]: `[PROJECT_ID]`
- **Title**: `[TITLE]`
- **Owner / requester**: `[NAME OR ROLE]`
- **Created / updated**: `[DATES]`
- **Status / current stage**: `[DRAFT | IN REVIEW | APPROVED FOR NEXT STAGE | BLOCKED]`

## Creative premise
- **Logline**: `[One-sentence hook]`
- **Synopsis**: `[Short beginning-to-end summary]`
- **Genre and tone**: `[GENRE; TONE]`
- **Target audience**: `[AGE / AUDIENCE / CONTENT CONSIDERATIONS]`
- **Intended runtime (seconds)**: `[INTEGER, MINIMUM 5]`
- **Language(s)**: `[LANGUAGE AND LOCALE]`
- **Animation technique**: `[2D | 2.5D | 3D | HYBRID]`

## Direction and constraints
- **Creative brief / themes**: `[INTENT, THEMES, AUDIENCE PROMISE]`
- **Visual direction**: `[STYLE, COLOR, COMPOSITION, REFERENCES AND RIGHTS]`
- **Production goals**: `[MEASURABLE OR QUALITATIVE GOALS]`
- **Restrictions / exclusions**: `[CONTENT, TECHNICAL, LEGAL, SCHEDULE, BUDGET]`
- **Delivery targets**: `[FORMATS, RESOLUTION, FRAME RATE, DESTINATION, IF KNOWN]`

## Open decisions and risks
| Question / risk | Impact | Owner | Needed by | Resolution / status |
|---|---|---|---|---|
| `[OPEN ITEM]` | `[IMPACT]` | `[OWNER]` | `[DATE/STAGE]` | `[OPEN / RESOLVED]` |

## Review and handoff
- **Human decision required**: `[WHAT MUST BE DECIDED; WHO IS AUTHORIZED]`
- **Decision/status**: `[PROPOSED / AWAITING HUMAN REVIEW / APPROVED / REVISION REQUESTED / REJECTED]`
- **Reviewer, date, rationale**: `[HUMAN REVIEW RECORD]`
- **Next department / deliverable**: `[HANDOFF]`

For machine-readable project metadata, map applicable fields to `SCHEMAS/PROJECT.schema.json`. This prose template does not itself satisfy schema validation or confer approval.
