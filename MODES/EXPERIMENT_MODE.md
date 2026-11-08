---
prompt_id: MODE_EXPERIMENT_MODE
version: 1.0.0
modified_date: 2026-11-09
description: Test new workflows, alternative models, and artistic directions in isolated experimental branches (`DRAFTS/EXPERIMENTS/`) without touching approved production assets.
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE_RULE_HIERARCHY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial definition of EXPERIMENT_MODE
---
# OPERATING MODE: EXPERIMENT_MODE

## Description
Test new workflows, alternative models, and artistic directions in isolated experimental branches (`DRAFTS/EXPERIMENTS/`) without touching approved production assets.

## Allowed Operations
- `run_isolated_experiment`
- `compare_models`

## Forbidden Operations
- `modify_architecture`
- `write_to_approved`
- `overwrite_production_asset`
