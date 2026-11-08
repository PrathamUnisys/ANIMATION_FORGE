---
prompt_id: TOOL_INTEL_TOOLCHAIN_APPROVAL
version: 1.0.0
modified_date: 2026-11-09
description: Prepare and govern human approval of project toolchains.
dependencies: ["TOOL_INTEL_EVALUATION", "TOOL_INTEL_COST", "TOOL_INTEL_LICENSING", "TOOL_INTEL_HARDWARE"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial toolchain approval procedure
---
# Toolchain Approval

## Approval packet
Submit the approved-project requirements, candidate comparison, dated source ledger, PoC evidence/limitations, license review, verified host profile, total-cost scenarios/cap, integration classification, security/data flow, dependencies, version pins, fallback behavior, and outstanding risks. Make every recommendation traceable to evidence. Keep `PLANNED` capabilities out of committed production capability claims.

## Human decision
Only a human decision-maker may select, approve, reject, or revise the project toolchain. Capture approver identity, date, exact tool/version/configuration, scope, cost ceiling, rationale, conditions, and expiry/review triggers. Approval is not blanket permission for future paid calls, downloads, destructive actions, or release of generated assets.

## Lock and change control
The project lock is `PROJECTS/<ID>/TOOLCHAIN/APPROVED_TOOLCHAIN.json`. The R&D engine checks a `HUMAN_` identity before writing a locked profile and `require_locked_toolchain` blocks downstream use when none exists (`backend/rnd/research_engine.py`). The engine constructs generic defaults and does not itself validate that selected candidates were tested or that every approval-packet check is complete. Application checks and human review remain mandatory; this document cannot replace them.

Reopen review for version, license, price, hardware, scope, endpoint, or risk changes. Keep prior versions and rationale; never silently swap a provider, model, or dependency under an existing approval.
