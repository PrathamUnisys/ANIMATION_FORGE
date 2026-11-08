---
prompt_id: TOOL_INTEL_EVALUATION
version: 1.0.0
modified_date: 2026-11-09
description: Evaluate shortlisted creative tools with evidence and uncertainty.
dependencies: ["TOOL_INTEL_REQUIREMENTS", "TOOL_INTEL_DISCOVERY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial evaluation procedure
---
# Tool Evaluation

Evaluate each candidate against the same requirement set. The engine's 11 dimensions are `quality`, `reliability`, `automation`, `cost`, `hardware`, `consistency`, `performance`, `compatibility`, `licensing`, `maintainability`, and `reusability` (`backend/rnd/research_engine.py`).

For each dimension give a score only when the project defines a scale and evidence supports it. Include rationale, source/test reference, confidence, and unknowns. Otherwise use `N/A`/`UNKNOWN`; do not manufacture a decimal score. If a weighted total is used, state weights and hard gates; an arithmetic mean must not conceal a failed legal, safety, or compatibility requirement.

### Compare
- Validate required workflows end-to-end: input/output, version pinning, repeatability, error recovery, and human review.
- Assess operational burden, update/rollback path, data exposure, accessibility, support horizon, and portability.
- Record performance as measured on named hardware with exact versions, settings, sample size, and date—not vendor claims presented as local results.
- Compare against a baseline and the next-best alternative. State trade-offs and what evidence would change the ranking.

### Decision statuses
Keep discovery, desk research, an actually executed PoC, recommendation, and human approval separate. Recommendations are conditional on unresolved evidence. Do not infer tested/approved from a schema-valid row.

The current engine averages provided dimension scores but embeds example candidate assessments. Treat those values as illustrative until each claim is source-checked and evaluated for the project. Its POC method does not execute a candidate; report that limitation rather than presenting its returned example metrics as measured results.
