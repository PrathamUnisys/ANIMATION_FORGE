---
prompt_id: CORE_CHANGE_CONTROL
version: 1.0.0
modified_date: 2026-11-09
description: Change Request lifecycle and rollback rules for Architecture Mode
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial Change Control specification
---
# CHANGE CONTROL POLICY

Any modification to `CORE/`, `MODES/`, `SCHEMAS/`, agent definitions, or global workflow structures requires:
1. Active operating mode set to `ARCHITECTURE_MODE`.
2. Creation of a structured Change Request (`CR_XXX`) containing:
   - `change_request_id`, `current_architecture_version`, `requested_modification`, `reason`, `affected_departments`, `affected_workflows`, `compatibility_impact`, `advantages`, `disadvantages`, `testing_requirements`, `rollback_plan`, `proposed_version`, `approval_status`.
3. Explicit human approval (`approval_status = APPROVED`) before applying the change.
4. Full snapshot retention of the previous architecture version to support deterministic one-click rollback.
