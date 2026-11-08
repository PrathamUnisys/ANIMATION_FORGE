---
prompt_id: TEMPLATE_DOC_SCREENPLAY
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable screenplay draft and revision template for the human screenplay approval gate
dependencies: ["TEMPLATE_DOC_PROJECT_BRIEF", "TEMPLATE_DOC_STORY_BIBLE", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable screenplay template
document_type: reusable_document_template
---
# TEMPLATE — SCREENPLAY

> Reusable screenplay document template, not an executable agent prompt or approved script. Replace placeholders with original project-specific material. A draft remains unapproved until an authorized human decision is recorded.

## Cover and revision record
- **Project ID / title**: `[PROJECT]`
- **Script ID / version**: `[SCR_PROJECT_ID_V##]`
- **Date / author**: `[DATE; AUTHOR]`
- **Status**: `[DRAFT / AWAITING_HUMAN_REVIEW / APPROVED / REVISION_REQUESTED / REJECTED]`
- **Previous version / change summary / reason**: `[REFERENCE AND SUMMARY]`
- **Source brief / story-bible revision**: `[REFERENCES]`
- **Language / target runtime**: `[LANGUAGE; MINUTES:SECONDS]`

## Creative intent
- **Logline**: `[LOGLINE]`
- **Audience and tone**: `[AUDIENCE; TONE]`
- **Open questions or assumptions**: `[ITEMS THAT MUST NOT BE MISTAKEN FOR CANON]`

## Script

### SCENE `[SCENE_ID]` — `[INT./EXT. LOCATION — TIME]`
**Action / setting:**  
`[Present-tense visual action. Note essential props, geography, and changes only.]`

**`[CHARACTER NAME]`**  
`[Parenthetical only when needed.]`  
`[Dialogue.]`

`[Continue with action, dialogue, transitions, and next scene heading. Keep dialogue verbatim after approval; identify any proposed changes in the revision record.]`

## Scene and timing summary
| Scene ID | Heading / purpose | Characters | Approx. duration | Open production needs |
|---|---|---|---|---|
| `[SCN_ID]` | `[PURPOSE]` | `[IDS]` | `[SECONDS]` | `[NOTES]` |

- **Estimated total runtime**: `[TIME AND ESTIMATION METHOD]`
- **Continuity / feasibility notes**: `[ITEMS FOR REVIEW; DO NOT CHANGE CANON SILENTLY]`

## Review record
- **Technical/script review findings**: `[CHECKS AND LIMITATIONS; NOT CREATIVE APPROVAL]`
- **Human reviewer and authenticated decision**: `[REVIEWER ID; APPROVED / REVISION_REQUESTED / REJECTED; DATE]`
- **Comments / rationale / required changes**: `[RECORD]`

There is no dedicated screenplay-content schema. The implemented script workflow uses revision and approval records; `SCHEMAS/PROJECT.schema.json` describes project metadata, not screenplay text. Never overwrite an approved revision: create a new version and repeat the screenplay human gate.
