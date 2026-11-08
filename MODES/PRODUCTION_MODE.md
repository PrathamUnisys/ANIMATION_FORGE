---
prompt_id: MODE_PRODUCTION_MODE
version: 1.0.0
modified_date: 2026-11-09
description: Execute approved production workflows using approved tools and scripts to generate draft deliverables. Architecture modifications are strictly forbidden.
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE_RULE_HIERARCHY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial definition of PRODUCTION_MODE
---
# OPERATING MODE: PRODUCTION_MODE

## Description
Execute approved production workflows using approved tools and scripts to generate draft deliverables. Architecture modifications are strictly forbidden.

## Allowed Operations
- `execute_workflow`
- `generate_draft`
- `read_memory`

## Forbidden Operations
- `modify_architecture`
- `auto_approve`
- `unapproved_tool_execution`
