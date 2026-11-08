---
prompt_id: CORE_TOOL_SELECTION_POLICY
version: 1.0.0
modified_date: 2026-11-09
description: Mandatory per-project R&D and evidence-based tool selection rules
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Tool selection and R&D rules
---
# TOOL SELECTION POLICY

1. Never assume the previous project's toolchain is optimal for a new project.
2. Every tool candidate progresses through explicit states: `DISCOVERED`, `RESEARCHED`, `TESTED`, `RECOMMENDED`, `APPROVED`, `REJECTED`, `RETIRED`.
3. Reading documentation transitions a tool to `RESEARCHED`, never `TESTED`. Only executing a verified Proof of Concept transitions a tool to `TESTED`.
4. Candidates are scored across 11 dimensions: Quality, Reliability, Automation, Cost, Hardware, Consistency, Performance, Compatibility, Licensing, Maintainability, and Reusability.
