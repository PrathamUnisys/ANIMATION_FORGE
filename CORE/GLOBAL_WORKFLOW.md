---
prompt_id: CORE_GLOBAL_WORKFLOW
version: 1.1.0
modified_date: 2026-11-09
description: Policy sequence for the 17-stage production journey and its human gates
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Define mandatory 17-stage production pipeline
  - version: 1.1.0
    date: 2026-11-09
    summary: Separate workflow policy from verified application stage enforcement
---
# GLOBAL PRODUCTION WORKFLOW

## Purpose and implementation status

The sequence below is the intended production policy. It is not, by itself, a
claim that the application currently exposes a command, agent, or automatic
state transition for every stage. `projects.current_stage` records a stage;
only use a stage-transition capability when it is implemented and verified.
The inventory and `DOCS/INSTRUCTION_REPOSITORY_AUDIT.md` record gaps.

## Stage sequence

1. `USER_STORY_IDEA` - capture the user's premise and constraints.
2. `STORY_ANALYSIS` - analyze dramatic engine, audience, tone, feasibility,
   and open creative decisions.
3. `SCRIPT_DEVELOPMENT` - develop and revise a screenplay through the
   implemented screenplay workflow. Any stated pass count is a requirement
   only where the current workflow implements it.
4. `SCREENPLAY_APPROVAL` - submit the screenplay draft for authenticated human
   creative approval. Do not start downstream work that requires an approved
   screenplay until approval exists.
5. `PRODUCTION_REQUIREMENT_ANALYSIS` - derive deliverables, skills, constraints,
   and technical requirements from the approved script.
6. `ONLINE_TOOL_RESEARCH_AND_RND` - conduct project-specific, dated research
   for requirements not already met by an approved toolchain.
7. `TOOL_COMPARISON` - compare candidates with sourced evidence, limitations,
   cost, licensing, hardware, and compatibility.
8. `PROOF_OF_CONCEPT` - perform only a specifically authorized test. Obtain
   explicit human authorization before downloads, installation, paid usage, or
   other consequential operations.
9. `HUMAN_TOOLCHAIN_APPROVAL` - present a documented recommendation for human
   selection. Record approval before treating a toolchain as locked. Generate
   an approved manifest only if the implementation supports it.
10. `PRODUCTION_PLANNING` - sequence work with prerequisites, owners, estimates,
    and review points.
11. `AUDIO_AND_VISUAL_PRODUCTION` - create draft character, environment, voice,
    and other required assets; preserve provenance and separate technical QC
    from creative review.
12. `STORYBOARD_AND_ANIMATIC` - prepare the shot plan and animatic. Obtain
    human review at the designated gate before downstream animation.
13. `ANIMATION` - execute approved production work with approved assets and
    tools; preserve non-destructive revisions.
14. `POST_PRODUCTION` - edit, composite, mix, subtitle, and package the work
    with traceable revisions.
15. `QUALITY_CONTROL` - run available technical checks and report both results
    and untested requirements.
16. `HUMAN_FINAL_APPROVAL` - present the final package to an authenticated
    human reviewer. Technical QC cannot approve it.
17. `COMPLETED_PRODUCTION_PACKAGE` - mark complete only after required
    approvals and deliverables are verifiably present.

## Gate invariants

- A failed prerequisite blocks only the dependent operation; preserve its
  upstream inputs and report the specific blocker.
- Do not infer approval from a stage label, successful build, passing QC, or
  an empty review queue.
- Human gates require the approval workflow described in
  `CORE/HUMAN_APPROVAL_POLICY.md`.
- The proof-of-concept gate authorizes only the described test and cost
  envelope; it does not authorize an entire production run.
- When a planned stage has no implemented capability, provide a status report
  and identify the gap instead of simulating completion.
