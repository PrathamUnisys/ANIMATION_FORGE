---
prompt_id: CORE_OUTPUT_CONTRACTS
version: 1.0.0
modified_date: 2026-11-09
description: Machine-to-machine JSON output contract and schema enforcement
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Standardize JSON output envelope
---
# OUTPUT CONTRACTS

Every agent operation must return a JSON payload conforming to `SCHEMAS/` and wrapped in the standard operation envelope:
- `operation_id` (string)
- `project_id` (string)
- `agent_id` (string)
- `status` (`awaiting_review` | `completed_analysis` | `failed` | `blocked`)
- `outputs` (array of structured deliverable descriptors)
- `warnings` (array of strings)
- `validation` (`{"schema_valid": bool, "technical_checks_passed": bool}`)
- `requires_human_approval` (boolean, always `true` for creative deliverables)
