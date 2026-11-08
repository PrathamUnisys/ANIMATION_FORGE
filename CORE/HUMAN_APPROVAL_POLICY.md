---
prompt_id: CORE_HUMAN_APPROVAL_POLICY
version: 1.0.0
modified_date: 2026-11-09
description: State machine and enforcement rules for mandatory human review
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Formalize creative deliverable state machine
---
# HUMAN APPROVAL POLICY

## Deliverable State Machine
Every creative deliverable transitions strictly through:
`PROPOSED` → `GENERATING` → `QUALITY_CHECK` → `AWAITING_HUMAN_REVIEW`

From `AWAITING_HUMAN_REVIEW`, only an authenticated human reviewer action may transition the state to:
- `APPROVED`
- `REVISION_REQUESTED`
- `REJECTED`

## Separation of Technical QC and Creative Approval
- The `QUALITY_CONTROLLER` agent may set technical validation status to `APPROVED_TECHNICALLY`, `NEEDS_REVISION`, `REJECTED`, or `MANUAL_INSPECTION_REQUIRED`.
- `APPROVED_TECHNICALLY` **never** marks `approval_status = APPROVED`.
- Any attempt by an AI agent ID to invoke the human approval transition raises `ApprovalPolicyViolationError`.
