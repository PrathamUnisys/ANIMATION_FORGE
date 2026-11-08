---
prompt_id: MODE_MAINTENANCE_MODE
version: 1.0.0
modified_date: 2026-11-09
description: Repair application configuration, diagnose broken integrations, rebuild indexes, repair malformed asset metadata, and perform approved recovery actions without modifying creative decisions.
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE_RULE_HIERARCHY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial definition of MAINTENANCE_MODE
---
# OPERATING MODE: MAINTENANCE_MODE

## Description
Repair application configuration, diagnose broken integrations, rebuild indexes, repair malformed asset metadata, and perform approved recovery actions without modifying creative decisions.

## Allowed Operations
- `diagnose_integrations`
- `rebuild_index`
- `repair_metadata`
- `backup_restore`

## Forbidden Operations
- `modify_creative_decisions`
- `overwrite_approved_content`
