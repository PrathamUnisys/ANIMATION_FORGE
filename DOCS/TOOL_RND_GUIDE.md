---
prompt_id: DOCS_TOOL_RND_GUIDE
version: 1.0.0
modified_date: 2026-11-09
description: Project-specific tool research, comparison, and authorization workflow
dependencies: ["CORE/TOOL_SELECTION_POLICY.md", "CORE/HUMAN_APPROVAL_POLICY.md"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Clarify R&D policy versus implemented behavior and link the operational guides
---
# Mandatory Per-Project Tool R&D Guide

## Entry requirements

Begin production R&D only after the screenplay has the required human approval.
Read its approved revision, project requirements, current toolchain decision,
budget and restrictions. Do not copy the toolchain of another project as a
default.

## Research and comparison

Use the procedures in:

- `DOCS/TOOL_INTELLIGENCE/REQUIREMENT_ANALYSIS.md`
- `DOCS/TOOL_INTELLIGENCE/ONLINE_RESEARCH_RULES.md`
- `DOCS/TOOL_INTELLIGENCE/TOOL_DISCOVERY.md`
- `DOCS/TOOL_INTELLIGENCE/TOOL_EVALUATION.md`
- `DOCS/TOOL_INTELLIGENCE/COST_ANALYSIS.md`
- `DOCS/TOOL_INTELLIGENCE/LICENSING_CHECK.md`
- `DOCS/TOOL_INTELLIGENCE/HARDWARE_COMPATIBILITY.md`
- `DOCS/TOOL_INTELLIGENCE/POC_PLANNER.md`
- `DOCS/TOOL_INTELLIGENCE/TOOLCHAIN_APPROVAL.md`

Derive requirements before searching. Record dated sources, versions,
uncertainty, cost assumptions, licensing questions, and reproducible test
evidence. Score the eleven schema dimensions only when evidence supports a
score; mark the rest unknown. Documentation research is not a proof of
concept. A candidate is not tested until an authorized test has actually run.

## Application boundary

`ProductionRndEngine` contains project R&D methods and checks screenplay
approval, but this does not establish that the full policy workflow is
available as an HTTP endpoint, that hardware is profiled from the current
machine, or that online research happened. The current hardware profile uses a
fixed baseline. Consult the capability registry and audit before describing an
operation as automated.

The tool candidate states in `TOOL.schema.json` are
`DISCOVERED`, `RESEARCHED`, `TESTED`, `RECOMMENDED`, `APPROVED`, `REJECTED`,
and `RETIRED`. Only a human can approve the selected project toolchain.

## Proof of concept and approval

Before any POC, document its exact scope, data, tool/version, network access,
downloads/installation, estimated cost, limit, hardware, acceptance tests,
cleanup and rollback. Obtain explicit human authorization for paid usage,
downloads, installation, external data transfer and destructive work.

Present the comparison, recommendation, rejected alternatives, risks, cost
limit and unresolved license questions for human review. Record approval only
after a human decision through the supported approval path. A research report
or generated `APPROVED_TOOLCHAIN.json` file is not itself proof of approval.
