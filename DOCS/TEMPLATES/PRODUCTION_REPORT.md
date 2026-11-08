---
prompt_id: TEMPLATE_DOC_PRODUCTION_REPORT
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable production progress, provenance, blockers, and handoff report template
dependencies: ["SCHEMAS/TASK.schema.json", "SCHEMAS/ASSET.schema.json", "CORE_OUTPUT_CONTRACTS"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable production report template
document_type: reusable_document_template
---
# TEMPLATE — PRODUCTION REPORT

> Reusable status report, not an executable agent prompt or proof that a listed operation completed. Report observed actions and outputs only.

## Report metadata
- **Project / report ID / reporting period**: `[IDS; DATES]`
- **Owner / date / current stage**: `[DETAIL]`
- **Overall status**: `[ON TRACK / AT RISK / BLOCKED / COMPLETE SUBJECT TO APPROVAL]`
- **Source plan / approved revisions**: `[REFERENCES]`

## Progress and deliverables
| Task / department | Expected output | Actual status | Asset/file ID and revision | Approval/QC state | Evidence / owner |
|---|---|---|---|---|---|
| `[TASK ID]` | `[PLAN]` | `[PROPOSED / GENERATING / QUALITY_CHECK / AWAITING_HUMAN_REVIEW / BLOCKED / OTHER]` | `[ID / PATH OR NONE]` | `[STATE; DO NOT CONFLATE QC WITH APPROVAL]` | `[DETAIL]` |

For structured tasks see `SCHEMAS/TASK.schema.json`; for produced assets see `SCHEMAS/ASSET.schema.json`. This report is a human-readable summary, not a substitute for those records.

## Changes, issues, and dependencies
- **Completed work / actual operations**: `[WHAT OCCURRED AND EVIDENCE]`
- **Changes against plan / reason / affected revisions**: `[DETAIL]`
- **Blockers, risks, and exceptions**: `[IMPACT; OWNER; NEXT ACTION]`
- **Dependencies / missing inputs / pending approvals**: `[IDS AND STATES]`
- **Cost / schedule variance**: `[MEASURED OR ESTIMATED; METHOD]`

## Quality and approvals
- **Technical checks performed / not performed**: `[CHECK; RESULT; EVIDENCE; LIMITS]`
- **Creative review state**: `[AWAITING HUMAN REVIEW / APPROVED / REVISION REQUESTED / REJECTED]`
- **Human decision record**: `[AUTHENTICATED REVIEWER; DATE; COMMENTS OR PENDING]`
- **Outstanding corrective actions**: `[ACTION; OWNER; TARGET]`

## Handoff
- **Next department / gate**: `[DETAIL]`
- **Files and references transferred**: `[LIST]`
- **Unverified claims / limitations**: `[EXPLICITLY LIST]`
