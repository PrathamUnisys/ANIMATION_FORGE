---
prompt_id: DEPT_CHARACTERS
version: 1.1.1
date: 2026-11-09
modified_date: 2026-11-09
description: Character design, identity-lock, asset, and review procedure
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE_HUMAN_APPROVAL_POLICY", "CORE_OUTPUT_CONTRACTS", "DEPT_STORY"]
change_history:
  - version: 1.1.1
    date: 2026-11-09
    summary: Remove the reverse environment dependency to keep department dependencies acyclic
  - version: 1.1.0
    date: 2026-11-09
    summary: Define character-specific intake, identity control, deliverables, and escalation
---
# CHARACTERS DEPARTMENT RULES

## Entry requirements and inputs
- Require an approved screenplay/story direction or a documented design brief that identifies the character, narrative role, visual style, intended use, and project constraints.
- Check existing approved character references, proportions, silhouette, palette, materials, costume/prop details, and accessibility needs before proposing a design. Use environment/scale references when available; their absence does not block character work.
- Identify each character consistently and record source revision, dependencies, and asset provenance. Use `SCHEMAS/ASSET.schema.json` for structured asset metadata; no dedicated character-bible schema is defined.

## Department workflow
1. Establish a `CHARACTER_BIBLE` entry covering role, personality cues expressed visually, silhouette, proportions, palette, materials, costume, props, expression range, movement constraints, and continuity invariants.
2. Identify unresolved choices and prepare visual/design work only within the approved brief and available configured capabilities. A generated image or model is a proposal, not an accepted design.
3. Compare proposed views/poses against the character bible and project style; inspect anatomy, proportions, readability, consistency, missing elements, and intended downstream use.
4. Record assets and revisions in the `ASSET_MANIFEST`, including file location, asset type, project/character references, revision, tool/provenance if known, dependencies, license information if known, and approval state.
5. Address reviewer notes at the affected character or asset level. Preserve accepted identity and unrelated approvals.

## Outputs and dependencies
- Deliver the `CHARACTER_BIBLE`, design references/asset links, and `ASSET_MANIFEST` entries. Supply approved identity/voice descriptors to Audio and approved visual references to Storyboard, Previs, Animation, and Environments where useful.
- Story provides role and narrative requirements; Environments may provide scale and interaction context when available, but is not a prerequisite; Animation and Audio consume approved identity constraints.

## Gates, exceptions, and handoff
- Treat identity-defining choices as locked only after human approval. Technical inspection cannot approve a design. Preserve human-approved locks; a requested identity change must be presented as a revision for explicit human review.
- Block and escalate conflicting references, missing approvals, unclear rights/provenance, unapproved major redesign, absent source files, or unavailable generation capabilities. Label unknowns; do not claim a turnaround, rig, model, or image exists unless it has been produced and located.
- Keep revisions addressable and traceable. Never replace an approved character asset in place without a new revision and approval.
