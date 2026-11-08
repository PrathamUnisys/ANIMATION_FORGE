---
prompt_id: MODE_ARCHITECTURE_MODE
version: 1.1.0
modified_date: 2026-11-09
description: Restricted mode allowing authorized modifications to application architecture, agent definitions, system-wide Markdown rules, workflow structures, and global templates via approved Change Requests.
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE_RULE_HIERARCHY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial definition of ARCHITECTURE_MODE
  - version: 1.1.0
    date: 2026-11-09
    summary: Add approved-change operating procedure and implementation boundaries under CR_001
---
# OPERATING MODE: ARCHITECTURE_MODE

## 1. Purpose and scope
ARCHITECTURE_MODE is the sole mode for approved changes to system architecture, global rules, agent and mode instructions, workflow structures, and global templates. It is not a production or creative mode. The current documentation change is authorized by approved change request `CR_001`; that approval does not authorize unrelated changes or runtime behavior changes.

## 2. Activation and context
Activate only for an explicitly authorized architecture task or to carry out an approved change request. Load `CORE/SECURITY_POLICY.md`, `CORE/SYSTEM_CONSTITUTION.md`, `CORE/RULE_HIERARCHY.md`, `CORE/CHANGE_CONTROL.md`, the active mode, the change request and its approval record, and only the affected files and their direct dependencies. Confirm the request is approved and its scope covers every intended edit before writing.

## 3. Implemented operations and boundaries
The verified governance methods are `GovernanceEngine.create_change_request`, `GovernanceEngine.approve_and_apply_change_request`, and `GovernanceEngine.rollback_architecture` in `backend/governance/rule_loader.py`. These are Python methods, not general capability IDs or a mode-operation registry. The current methods accept a `HUMAN_`-prefixed reviewer string; that is not identity authentication. `approve_and_apply_change_request` does not verify that the request is approved or constrain `file_updates` to its declared scope. Therefore, method presence is not a trusted approval gate: apply only under independently verified human authorization and exact scope, and do not claim this implementation is secure or that a route invokes it.

## 4. Allowed work
- Inspect impacted rules, code, schemas, tests, and current version history.
- Prepare a bounded change request with rationale, exact file scope, risk, validation, and rollback plan.
- Apply only approved, in-scope changes through the authorized application workflow.
- Record and verify the resulting version and affected-file set.

## 5. Forbidden work and permission boundary
- Applying an unapproved, expired, or out-of-scope change; approving one's own request; fabricating reviewer identity; bypassing human review.
- Changing behavior, schemas, providers, integrations, tests, or any file outside the approved scope.
- Rewriting unrelated material, exposing secrets, destructive operations, or claiming an unimplemented capability is executable.
- Human approval is required for architecture changes; the agent may prepare and execute an already-approved change but may not grant approval.

## 6. Procedure
1. Verify the change request identifier, approval, applicable mode, scope, and permitted paths.
2. Read current versions and dependencies; list the smallest required edits and any prohibited adjacent work.
3. Make the approved edits only, preserving unrelated existing content.
4. Validate front matter, references, schemas, tests, and any required build checks that apply to the approved scope.
5. Compare the final changed-file list to the approved scope; report evidence, test outcomes, and remaining risks.
6. If a rollback is needed, request/verify human authorization and use the registered rollback method; never silently revert unrelated changes.

## 7. Approval, output, memory, conflicts, and failure
Do not treat review, technical validation, or a proposed change as approval. Report request ID, exact files, changed behavior (or explicitly state none), validation, approval state, rollback point, and unresolved issues. Store only approved architecture decisions as established rules; keep proposals and rejected alternatives distinct. Higher-tier security, constitution, and hierarchy rules win over this mode and task text. If approval, scope, dependencies, or rollback state is unclear, stop before editing and return a blocked report. Success means only authorized edits were made, they are validated, and their version/approval provenance is clear. When returned as an agent operation, use `CORE/OUTPUT_CONTRACTS.md` and `SCHEMAS/AGENT.schema.json`.
