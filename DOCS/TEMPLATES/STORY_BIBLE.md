---
prompt_id: TEMPLATE_DOC_STORY_BIBLE
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable story canon, theme, and continuity reference template
dependencies: ["TEMPLATE_DOC_PROJECT_BRIEF", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable story bible template
document_type: reusable_document_template
---
# TEMPLATE — STORY BIBLE

> Reusable reference template, not an executable agent prompt. Separate approved canon from proposals, interpretations, and open questions.

## Record
- **Project ID / title**: `[PROJECT]`
- **Version / date / author**: `[VERSION; DATE; OWNER]`
- **Source brief and approved screenplay revisions**: `[IDS / LINKS]`
- **Status**: `[DRAFT / AWAITING HUMAN REVIEW / APPROVED / REVISION REQUESTED]`

## Story foundation
- **Premise / logline**: `[CORE CONCEIT]`
- **Theme / dramatic question**: `[WHAT THE STORY EXPLORES]`
- **Genre, tone, audience**: `[CONSTRAINTS]`
- **World rules and boundaries**: `[ONLY ESTABLISHED FACTS; CITE SOURCE/DECISION]`
- **Central conflict and stakes**: `[WHY IT MATTERS]`
- **Narrative promise / ending constraints**: `[INTENDED EXPERIENCE; NO UNAPPROVED LOCKS]`

## Story structure
| Beat / act | Purpose | Key event | Character change | Approx. time |
|---|---|---|---|---|
| `[BEAT]` | `[PURPOSE]` | `[EVENT]` | `[CHANGE]` | `[TIME]` |

## Character and continuity
| Character / element | Role or fact | Approved source | Invariants | Open questions |
|---|---|---|---|---|
| `[ID / NAME]` | `[DETAIL]` | `[SOURCE REVISION]` | `[MUST REMAIN TRUE]` | `[UNKNOWN]` |

## Canon and change log
- **Approved facts**: `[FACT; APPROVAL REFERENCE]`
- **Proposed / unapproved ideas**: `[IDEA; OWNER; REVIEW NEEDED]`
- **Continuity risks / contradictions**: `[ISSUE; AFFECTED SCENES; RESOLUTION]`
- **Revision summary**: `[WHAT CHANGED AND WHY]`

## Review and downstream use
- **Human reviewer / decision / date / rationale**: `[RECORD; DO NOT INFER APPROVAL]`
- **Impacted screenplay, character, environment, audio, or shot records**: `[IDS]`
- **Handoff notes**: `[UNRESOLVED QUESTIONS; NEXT OWNER]`

No dedicated Story Bible JSON Schema is defined. Use `SCHEMAS/PROJECT.schema.json` only for applicable project metadata; this narrative reference is not schema-validated by that schema.
