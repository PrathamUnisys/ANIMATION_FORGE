---
prompt_id: DEPT_ANIMATION
version: 1.1.0
date: 2026-11-09
modified_date: 2026-11-09
description: Entry requirements, deliverables, workflow, and review rules for the animation department
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE_HUMAN_APPROVAL_POLICY", "CORE_OUTPUT_CONTRACTS", "DEPT_STORYBOARD", "DEPT_CHARACTERS", "DEPT_ENVIRONMENTS"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Replace generic loop with animation-specific operating procedure
---
# ANIMATION DEPARTMENT RULES

## Entry requirements and inputs
- Start only from an approved screenplay and the approved scene/shot plan or storyboard revision. Resolve editorial notes against the approved source rather than inventing story changes.
- Confirm required character and environment assets, their revisions and approval states, the intended runtime, frame rate, resolution, animation technique, and any approved toolchain profile. If any prerequisite is missing or ambiguous, mark the work blocked and ask the production owner for resolution.
- Record shot/scene identifiers, dependencies, references, and revision provenance. Follow `SCHEMAS/SHOT.schema.json` for structured shot and animation-specification data and `SCHEMAS/ASSET.schema.json` for asset records.

## Department workflow
1. Break work into the smallest addressable shot or asset task; retain the approved staging, screen direction, character identity, design locks, and timing.
2. Prepare or update the animation specification before execution. State camera, placement/action, lighting, duration, frame rate, resolution, required assets, audio cues, and any assumptions. Do not claim a render, simulation, or external-tool operation occurred unless it actually did.
3. Execute only through a configured and available capability. Capture the tool/workflow/version and source revisions where known; otherwise report that information as unavailable.
4. Inspect the result against shot intent, continuity, asset completeness, timing, image integrity, and technical delivery requirements. Record specific defects and affected frames/shot IDs.
5. Correct only the affected task(s), preserve unaffected approved work, and resubmit for technical checks and human review.

## Outputs and dependencies
- Deliver an `ANIMATION_SPECIFICATION`, shot-level result references, and the relevant `ASSET_MANIFEST` entries; use `PRODUCTION_REPORT` for completion, blockers, and provenance.
- Dependencies: Storyboard and Previs provide approved shot intent; Characters and Environments provide approved visual assets; Audio provides synchronized cues where applicable. Tool R&D and the approved toolchain are prerequisites only when their outputs are required by the chosen method.

## Gates, exceptions, and handoff
- Technical validation is not creative approval. Route creative deliverables to `AWAITING_HUMAN_REVIEW`; only an authorized human may approve, request revision, or reject. Never mark work approved based on generation or QC alone.
- Stop and escalate for identity/style-lock conflicts, missing approvals, unavailable tools, unsupported formats, cost/download authorization needs, or repeated failures. Record impact and alternatives; do not silently substitute tools or expand scope.
- For requested revisions, create a traceable new revision and keep the prior approved version immutable. Never regenerate the whole project for a targeted correction.
