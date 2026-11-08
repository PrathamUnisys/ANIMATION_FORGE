---
prompt_id: DOCS_AGENT_GUIDE
version: 1.1.0
modified_date: 2026-11-09
description: Agent role map, dispatch boundaries, output contracts, and human approval rules
dependencies: ["CORE/RULE_HIERARCHY.md", "CORE/HUMAN_APPROVAL_POLICY.md", "DOCS/CAPABILITY_REGISTRY.md"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Replace role list with operational dispatch and permission guidance
  - version: 1.1.0
    date: 2026-11-09
    summary: Document genre/style profile loading, task-based tool lookup and library reuse under CR_003
---
# Specialized AI Production Agents Guide

## Agent roster

Animation Forge defines 17 specialized agents. Agent-specific instructions
live at:

- Story and script: `STORY_ARCHITECT`, `SCREENWRITER`, `SCRIPT_CRITIC`,
  `SCRIPT_BREAKDOWN` under `AGENTS/`.
- World and design: `WORLD_ARCHITECT`, `CHARACTER_ARCHITECT`,
  `CHARACTER_DESIGNER`, `ENVIRONMENT_DESIGNER` under `AGENTS/`.
- Research: `RESEARCH_ANALYST` under `AGENTS/`.
- Audio and previs: `AUDIO_DIRECTOR`, `STORYBOARD_DIRECTOR`,
  `CAMERA_DIRECTOR`, `PREVIS_DIRECTOR` under `AGENTS/`.
- Animation, post, and QC: `ANIMATION_ENGINEER`, `VIDEO_EDITOR`,
  `QUALITY_CONTROLLER` under `AGENTS/`.
- Production orchestration: `PRODUCTION_DIRECTOR` under
  `ORCHESTRATION/PRODUCTION_DIRECTOR/`.

The role list is not proof that every role has an executable backend
dispatcher. Agent instructions specify work boundaries; the current
`AgentExecutor` constructs context, checks paths and validates outputs for
calls made through its interface. Consult the capability registry for the
public API and MCP catalog, and the repository audit for implementation gaps.

## Dispatch procedure

1. Select the project and stage from persisted state; do not infer them from
   an unrelated conversation.
2. Select the narrowest agent role appropriate to the task. Load the governing
   constitution, active mode, project/series memory, department rules, agent
   instruction, and provider profile as applicable.
3. Confirm required inputs, upstream approvals, allowed project paths, and
   registered capabilities before dispatch. For screenplay work, resolve a
   primary genre, optional secondary genres and optional channel style as
   separate versioned profiles. For production tasks, consult the task-based
   tool catalogue and asset library; do not treat catalogue presence as proof
   that a tool is installed or an asset is approved.
4. Give the agent a specific deliverable, project ID, revision, constraints,
   output schema, and acceptance checks.
5. Validate its response and persisted outputs. Report assumptions, warnings,
   test evidence, and blocked/failed states accurately.
6. Route creative work through human review. QC and agent dispatch do not grant
   creative approval.

## Output and approval

Use the applicable entity schema and
`CORE/OUTPUT_CONTRACTS.md`; do not assume one envelope fits every operation.
The backend validates operation envelopes when its executor is used, but this
does not validate arbitrary Markdown or establish that a listed catalog
operation actually dispatches. Distinguish:

- agent analysis from generated creative deliverables;
- technical QC from a human creative decision;
- a registered capability name from an end-to-end implemented handler;
- a proposed idea from approved project canon.

No agent may approve its own script, assets, toolchain, architecture change,
or final production package. Human decisions must pass through the appropriate
approval mechanism. The current reviewer-prefix check is not an identity
provider.

## Collaboration and failure

Pass only the minimum relevant project context to the next role. Identify
upstream dependencies and cite the source revision. If another agent's
deliverable is missing, ambiguous, or unapproved, stop that dependent step and
report what is needed. Preserve draft outputs and diagnostic evidence after
failure; do not silently retry paid, external, or destructive work.
