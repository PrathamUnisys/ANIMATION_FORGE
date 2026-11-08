---
prompt_id: TOOL_INTEL_POC
version: 1.0.0
modified_date: 2026-11-09
description: Plan safe, reproducible proof-of-concept tests for candidate tools.
dependencies: ["TOOL_INTEL_REQUIREMENTS", "TOOL_INTEL_EVALUATION", "TOOL_INTEL_COST"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial POC planning procedure
---
# PoC Planner

## Plan before execution
For each unresolved decision, define the hypothesis, requirement IDs, exact tool/model/plugin/version, host and baseline, inputs (rights-cleared synthetic or approved samples), configuration, expected output, objective pass/fail criteria, instrumentation, run count, and rollback/cleanup. Record any data sent off-device, download size, account/credit use, and maximum cost.

Minimize scope and permissions. Isolate draft outputs, avoid production credentials, and do not overwrite approved assets. Require explicit human authorization before installation, model/asset downloads, network transfer, paid usage, or risky/destructive actions. Reconfirm if scope/cost changes.

## Run and report
Only record metrics actually observed. Preserve commands/settings, timestamps, logs, output hashes, errors, host conditions, and reviewer. Separate a synthetic/unit check, adapter validation, simulated response, and live integration test. Report deviations and non-reproducible results; do not turn expected/example values into measurements.

## Current implementation limit
`ProductionRndEngine.execute_authorized_poc` checks a human flag and candidate existence, then marks `TESTED` and returns fixed example metrics; it does not execute the named software (`backend/rnd/research_engine.py`). Do not use that return value as PoC evidence. A genuine PoC must run the tool through an independently verified path and be reviewed by a human.
