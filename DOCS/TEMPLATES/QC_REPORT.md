---
prompt_id: TEMPLATE_DOC_QC_REPORT
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable technical quality-control findings template, separate from creative approval
dependencies: ["SCHEMAS/APPROVAL.schema.json", "SCHEMAS/ASSET.schema.json", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable QC report template
document_type: reusable_document_template
---
# TEMPLATE — QC REPORT

> Reusable technical-inspection report, not an executable agent prompt or a creative approval. A technical pass never sets a deliverable to human-approved.

## Inspection record
- **QC report ID / project ID / date**: `[IDS; DATE]`
- **Target type / ID / revision**: `[TARGET]`
- **QC category / inspector / environment**: `[DETAIL]`
- **Source files / hashes / tool versions**: `[REFERENCES; ONLY VERIFIED VALUES]`
- **Inspection scope / method**: `[WHAT WAS AND WAS NOT CHECKED]`

## Checks and findings
| Check | Requirement / threshold | Method and evidence | Result | Issue severity / affected location |
|---|---|---|---|---|
| `[CHECK]` | `[SPEC]` | `[OBSERVED EVIDENCE OR NOT RUN]` | `[PASS / FAIL / NOT RUN / MANUAL INSPECTION REQUIRED]` | `[DETAIL]` |

## Summary
- **Technical outcome**: `[APPROVED_TECHNICALLY / NEEDS_REVISION / REJECTED / MANUAL_INSPECTION_REQUIRED]`
- **Defects / reproducibility notes**: `[DETAIL]`
- **Recommended targeted corrections**: `[ISSUE; ASSET/SHOT/LINE ID; ACTION]`
- **Unverified requirements / limitations**: `[DETAIL]`
- **Retest scope**: `[AFFECTED CHECKS ONLY OR JUSTIFICATION]`

## Separate human decision
- **Creative approval status**: `[AWAITING_HUMAN_REVIEW / APPROVED / REVISION_REQUESTED / REJECTED / NOT YET SUBMITTED]`
- **Human reviewer / decision ID / date / comments**: `[RECORD OR PENDING]`

`SCHEMAS/APPROVAL.schema.json` describes an approval-gate record, not a QC-report schema. Record technical QC independently; do not claim a human decision or infer approval from a passing check.
