---
prompt_id: MODE_EXPERIMENT_MODE
version: 1.1.0
modified_date: 2026-11-09
description: Test new workflows, alternative models, and artistic directions in isolated experimental branches (`DRAFTS/EXPERIMENTS/`) without touching approved production assets.
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE_RULE_HIERARCHY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial definition of EXPERIMENT_MODE
  - version: 1.1.0
    date: 2026-11-09
    summary: Distinguish implemented R&D methods from unavailable isolated experiment features under CR_001
---
# OPERATING MODE: EXPERIMENT_MODE

## Purpose and scope
Use this mode to investigate and compare candidate production tools or workflows using reversible, non-production experiments. This mode does not authorize edits to architecture, approved assets, or production configuration.

## Activation and context
Activate only when the user requests a bounded experiment or comparison. Load the security policy, constitution, active project brief, relevant R&D report, applicable department constraints, and toolchain approval state. Use only a designated experimental location when one exists and is authorized; the repository does not establish `DRAFTS/EXPERIMENTS/` as an enforced sandbox.

## Implemented operations and allowed work
The verified R&D methods are `ProductionRndEngine.inspect_hardware_profile`, `run_mandatory_project_rnd`, `execute_authorized_poc`, `approve_and_lock_toolchain`, and `require_locked_toolchain` in `backend/rnd/research_engine.py`. `execute_authorized_poc` is approval-gated; the existence of these methods does not imply a user-facing route or an isolated experiment branch. No executable `run_isolated_experiment` or `compare_models` operation was found. Treat comparisons and proposed test plans as analysis unless a wired method actually runs them.

## Forbidden capabilities and permissions
Never alter production settings or approved deliverables, install or execute unapproved software, expose credentials, or call a planned operation as implemented. Do not promote an experiment result into production or approve/lock a toolchain without the required human decision. Preserve project sandbox boundaries.

## Procedure
1. Define a question, hypothesis, candidate set, success measures, risks, permitted resources, and stop conditions.
2. Verify written authorization, toolchain state, environment, and destination before execution.
3. Capture baseline and provenance; keep inputs and outputs isolated and reversible.
4. Run only a verified authorized method; otherwise provide a test plan and label it unexecuted.
5. Compare results against stated criteria, document limitations, clean up only experiment-owned temporary outputs, and report recommendation separately from approval.

## Approval, output, memory, conflicts, and failure
Human approval is required before PoC execution when the method requires it and before any toolchain is selected or locked for production. Return objective, implementation status, method actually invoked, setup/provenance, results, caveats, recommendation, and approval state. Store measured findings as evidence; proposed hypotheses are not project facts. Higher-tier security and governance rules prevail. Stop on missing authorization, unsafe environment, unclear isolation, tool failure, or any risk of touching approved state. Success is a reproducible, bounded result (or an explicitly unexecuted plan) with no production changes. For agent-operation handoff, follow `CORE/OUTPUT_CONTRACTS.md` and `SCHEMAS/AGENT.schema.json`.
