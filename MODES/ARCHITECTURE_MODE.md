---
prompt_id: MODE_ARCHITECTURE_MODE
version: 1.0.0
modified_date: 2026-11-09
description: Restricted mode allowing authorized modifications to application architecture, agent definitions, system-wide Markdown rules, workflow structures, and global templates via approved Change Requests.
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE_RULE_HIERARCHY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial definition of ARCHITECTURE_MODE
---
# OPERATING MODE: ARCHITECTURE_MODE

## Description
Restricted mode allowing authorized modifications to application architecture, agent definitions, system-wide Markdown rules, workflow structures, and global templates via approved Change Requests.

## Allowed Operations
- `create_change_request`
- `apply_approved_change_request`
- `rollback_architecture`

## Forbidden Operations
- `apply_unapproved_change`
- `auto_approve_change_request`
