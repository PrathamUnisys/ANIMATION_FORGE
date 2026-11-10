# CR_007 — YouTube Screenwriting Constitution and Audience Experience Integration

**Document status:** DRAFT PROPOSAL — NOT REGISTERED OR APPROVED  
**Prepared:** 2026-11-10  
**Change type:** Governance, creative contracts, agent guidance, schema alignment, and later runtime integration

> This file is a proposal artifact only. It is not evidence that GovernanceEngine.create_change_request was called, that a request exists in the database, or that a human approved it. Protected files must not be edited until the request is formally registered and approved through the repository's required Architecture Mode approval path.

## 1. Objective

Integrate a model-independent screenwriting standard and the existing Audience Experience design pack into Animation Forge without duplicating existing systems or weakening human authority.

The goal is to improve screenplay quality and audience planning while preserving approved canon and project-specific creative intent; genre, series format, and channel-style separation; immutable revision lineage; technical QC, creative critique, and human approval as separate decisions; and truthful reporting of implemented, partial, simulated, unavailable, and untested capabilities.

## 2. Current repository baseline

The Audience Experience module already contains:
- Hook library and screenplay format templates.
- Audience Plan, Packaging Options, Retention Map, and Creative Review design schemas.
- Retention, analytics, packaging, visual and audio playbooks.
- Mystery/horror genre checklists and creative review checklist.
- Research synthesis, examples, and experiment templates.

Its README labels it a draft design workspace, not an active runtime feature. CR_006 already establishes a story context and screenplay pipeline, with documented limitations. Therefore CR_007 must be additive and verify current implementation before changing any contract.

## 3. Prepared design package

The following draft artifacts are prepared for review:
- AUDIENCE_EXPERIENCE/SCREENWRITING_CONSTITUTION.md
- AUDIENCE_EXPERIENCE/REQUIREMENT_CLASSIFICATION.md
- AUDIENCE_EXPERIENCE/QUALITY_CHECKS/CREATIVE_QUALITY_RUBRIC.md
- AUDIENCE_EXPERIENCE/SCRIPT_FORMATS/RUNTIME_ESTIMATION_STANDARD.md
- AUDIENCE_EXPERIENCE/SCHEMA_ALIGNMENT_PROPOSAL.md
- PROJECTS/SCRIPT_LAB_10/DEVELOPMENT/FRAMEWORK_AUDIT.md
- PROJECTS/SCRIPT_LAB_10/DEVELOPMENT/BENCHMARK_PLAN.md

These files are advisory design and audit documents. Their presence does not activate them as runtime instructions.

## 4. Proposed protected scope after approval

Final scope must be confirmed during formal request registration. Proposed candidates:

### Governance
- CORE/SYSTEM_CONSTITUTION.md: reference the approved creative standard without promoting it above canon/genre/project rules.
- CORE/RULE_HIERARCHY.md: clarify its placement and conflict boundaries.
- CORE/GLOBAL_WORKFLOW.md: add audience planning/review at appropriate existing stages without inventing new executable stages.
- CORE/OUTPUT_CONTRACTS.md: define provenance/reference and separate status reporting for audience artifacts.
- CORE/HUMAN_APPROVAL_POLICY.md: change only if required; default proposal is no change to human approval authority.

### Agent guidance
- AGENTS/STORY_ARCHITECT/INSTRUCTION.md: audience promise, hook alternatives, story structure and packaging proposal responsibilities.
- AGENTS/SCREENWRITER/INSTRUCTION.md: requirement classification, scene-linked Retention Map, natural dialogue and causality checks.
- AGENTS/SCRIPT_CRITIC/INSTRUCTION.md: evidence-backed creative review dimensions and severity; no approval or self-rewrite.

### Schemas and implementation contracts
- Existing SCHEMAS/ contracts and AUDIENCE_EXPERIENCE/SCHEMAS/ must be compared before selecting canonical ownership.
- Define exact revision-scoped scene/beat references and validation rules.
- Decide whether Audience Plan and Packaging Options are persisted entities or draft artifacts.
- No duplicate database columns/tables or parallel schema sources without an ownership decision.

### Runtime and UI
- Inspect existing context assembly, pipeline, QC, APIs, database, frontend and test coverage.
- Implement only verified gaps. Reuse CR_006 components where possible.
- Do not claim an agent, route, screen, provider, validator or migration exists until implemented and tested.

## 5. Proposed implementation milestones

| Milestone | Scope | Exit condition |
|---|---|---|
| M0 — Formal registration and baseline | Register request, verify architecture version, enumerate exact files, preserve outside-snapshot copies/hashes | Request recorded as awaiting review; exact scope and rollback approved |
| M1 — Creative standard | Approve constitution, requirement classification, rubric and runtime evidence model | Human-reviewed creative standard and conflict precedence |
| M2 — Contract alignment | Select canonical schema ownership, define revision references and fixtures | Valid/invalid fixtures and compatibility decision approved |
| M3 — Governance and agent integration | Apply only approved CORE/AGENTS changes | Instruction repository validation and regression tests pass |
| M4 — Runtime integration | Backend/API/frontend implementation for the approved subset | Real persisted workflow with truthful capability status |
| M5 — Controlled benchmark | EP10, EP07, EP04 original-versus-revision comparison | Evidence-backed results and human review for each candidate |

M1 and M2 may be designed in parallel after M0. M3 depends on approved M1/M2. M4 depends on approved contracts and a verified code audit. M5 depends on the implemented workflow.

## 6. Acceptance criteria

- Audience Experience remains distinguished from genre, format, channel style, rights, and canon.
- Story beats/clues are not incorrectly treated as exact text.
- Retention Map references resolve against the exact screenplay revision.
- Packaging alternatives reflect the actual story promise.
- Creative review findings cite evidence and separate evidence from interpretation.
- Numeric scoring remains advisory until calibration and explicit approval.
- Runtime estimates are distinguished from animatic/final measured duration.
- Deterministic QC, creative critique, and human approval remain separate.
- Approved revisions and canon remain immutable.
- Existing CR_006 behavior and data remain compatible.
- Provider failure or mock output cannot be represented as live successful generation.
- All changed schemas, migrations, routes, UI, and agent instructions have regression tests.
- No unrun tests are reported as passed.

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Duplicate schema ownership | Decide canonical contract and compatibility before edits |
| Creative formula replaces genre judgement | Keep guidance flexible and genre-scoped |
| Retention heuristics become rigid rules | Label as hypotheses; no universal timing gates |
| Scores create false precision | No pass/fail score threshold before calibration |
| Audience metadata diverges from screenplay | Validate exact revision and scene references |
| Protected architecture changed without approval | Register and approve through Architecture Mode first |
| Existing project data breaks | Additive migrations, copies/hashes, migration tests and rollback |
| Mock/provider limitations hidden | Preserve explicit provider and capability status |

## 8. Rollback

Follow CORE/CHANGE_CONTROL.md. Before any protected or non-core implementation change:
- Preserve exact pre-change copies and hashes for every file outside the built-in CORE/MODES snapshot.
- Record the base commit and architecture version.
- Use small commits limited to approved files.
- Use additive database migrations and test on a copy.
- Preserve logs and test evidence.
- Never restore an old database over newer user work.
- Verify repository, database, and workflow state after rollback.

## 9. Out of scope

- Automatic YouTube publication or analytics account access.
- Automatic canon or screenplay approval.
- Rights clearance or legal conclusions.
- A universal three-act structure, hook deadline, beat interval, or retention threshold.
- Full animation/rendering, TTS, or video-editing implementation.
- Replacing CR_006 or changing its historical record.

## 10. Registration and approval checklist

- [ ] Verify the active architecture version in the application/database.
- [ ] Enter Architecture Mode.
- [ ] Register CR_007 through the implemented GovernanceEngine.
- [ ] Record exact file scope, test plan, rollback plan, and base revision.
- [ ] Present the request for authenticated human review.
- [ ] Wait for explicit approval.
- [ ] Apply only approved changes.
- [ ] Record test evidence and implementation result.

Until these steps are completed, CR_007 remains a draft proposal and no protected implementation work is authorized by this document.
