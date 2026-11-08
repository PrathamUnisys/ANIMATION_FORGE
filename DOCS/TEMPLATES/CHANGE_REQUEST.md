---
prompt_id: TEMPLATE_DOC_CHANGE_REQUEST
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable structured change-request template with impact, tests, rollback, and human decision
dependencies: ["CORE_CHANGE_CONTROL", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable change request template
document_type: reusable_document_template
---
# TEMPLATE — CHANGE REQUEST

> Reusable change proposal, not an executable agent prompt or authorization to make a change. Required for architecture-controlled surfaces as specified by `CORE/CHANGE_CONTROL.md`. Approval must precede protected changes.

## Identification
- **Change request ID**: `[CR_###]`
- **Title / requester / date**: `[DETAIL]`
- **Current architecture version**: `[VERSION OR NOT APPLICABLE]`
- **Proposed version**: `[VERSION OR NOT APPLICABLE]`
- **Approval status**: `[PROPOSED / AWAITING_HUMAN_REVIEW / APPROVED / REVISION_REQUESTED / REJECTED]`

## Requested modification
- **Requested modification**: `[SPECIFIC CHANGE AND BOUNDARIES]`
- **Reason / problem statement**: `[WHY THE CHANGE IS NEEDED]`
- **Affected departments**: `[DEPARTMENTS]`
- **Affected workflows / files / interfaces**: `[EXACT SCOPE]`
- **Out of scope**: `[EXPLICIT EXCLUSIONS]`

## Impact analysis
- **Compatibility impact**: `[BACKWARD/UPSTREAM/DOWNSTREAM EFFECTS]`
- **Advantages**: `[EXPECTED BENEFITS]`
- **Disadvantages / risks**: `[TRADE-OFFS AND MITIGATIONS]`
- **Data, security, licensing, or migration impact**: `[DETAIL OR NONE WITH BASIS]`
- **Dependencies / prerequisites**: `[IDS AND REQUIRED ORDER]`

## Verification and rollback
- **Testing requirements**: `[TARGETED TESTS; ACCEPTANCE CRITERIA; MANUAL CHECKS]`
- **Migration / rollout plan**: `[STEPS; ONLY PROPOSED UNTIL APPROVED]`
- **Rollback plan**: `[RECOVERY STEPS; SNAPSHOT / VERSION TO RESTORE]`
- **Failure / stop conditions**: `[WHEN TO HALT AND ESCALATE]`

## Human review
- **Reviewer / role**: `[AUTHORIZED HUMAN]`
- **Decision / date**: `[APPROVED / REVISION_REQUESTED / REJECTED; DATE]`
- **Rationale / conditions**: `[COMMENTS]`
- **Implementation record after approval**: `[ACTUAL FILES/REVISION/TEST RESULTS; COMPLETE AFTER WORK]`

For changes governed by `CORE/CHANGE_CONTROL.md`, active `ARCHITECTURE_MODE` and explicit human approval are prerequisites. Do not perform protected edits while the request is merely proposed.
