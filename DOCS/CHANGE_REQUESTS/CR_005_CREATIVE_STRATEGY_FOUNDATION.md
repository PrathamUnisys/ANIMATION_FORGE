---
change_request_id: CR_005
version: 0.1.0
modified_date: 2026-11-09
status: DRAFT_PROPOSAL_NOT_SUBMITTED
description: Preparatory architecture for story acquisition, series formats and audience-experience research
dependencies:
  - CORE/CHANGE_CONTROL.md
  - DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md
---

# CR_005 — Creative Strategy Foundation

## Governance status

**Draft proposal only. Not submitted to the GovernanceEngine and not approved.**

This branch contains preparatory documentation and empty registries/templates only. It does not change active application behaviour, database structure, API contracts, frontend screens, agent permissions, global workflow rules or existing genre/channel selections. Do not merge this branch as an approved architecture change without following `CORE/CHANGE_CONTROL.md`.

## Objective

Prepare Animation Forge to incorporate two bodies of work that are being researched:

1. Story acquisition and source governance: how a story enters the production system, how its provenance is recorded, and how rights/originality questions are routed for review.
2. Audience experience: how screenplay craft, video packaging, animation, audio and post-publication analytics may support viewer appeal, engagement, satisfaction and returning audiences.

Also establish a separate series-format domain so format conventions are not confused with genre or channel style.

## Creative direction currently available

The provisional creative direction from the user's strategy research is:

- Primary: Occult Detective / Supernatural Mystery.
- Supporting influences: Dark Folklore, Psychological Horror and Cosmic Horror.
- Series format: Shared-Universe Thematic Anthology.
- Initial episode target: approximately 6–10 minutes.
- Initial companion Shorts target: approximately 45 seconds.

These are editorial starting points, not validated platform rules, universal retention requirements or permanent production constraints. The exact genre profiles and script-format rules remain subject to review and further research.

## Proposed domains

### A. Story acquisition

Create a source workflow that distinguishes:
- Original user ideas.
- Original AI-assisted concepts with human creative direction.
- Public-domain works.
- Traditional folklore and oral traditions.
- Historical events and documented mysteries.
- Openly licensed works.
- Licensed works.
- Commissioned works.
- Inspiration-only references.

Record source provenance, editions/translations, intended use, territories, rights evidence, originality review and unresolved questions. A source record is not a legal opinion. Unclear rights must block adaptation/publication until appropriate human/legal review.

### B. Series formats

Create versioned format profiles independently from genre profiles and channel styles. The initial draft format is Shared-Universe Thematic Anthology. It should describe episode relationships, continuity, recurring elements and optional season arcs without imposing fixed episode timings.

### C. Audience experience

Create a research and evidence workspace covering:
- YouTube storytelling and screenplay formats.
- Hooks and opening sequences.
- Retention, suspense, pacing and narrative comprehension.
- Mystery, horror and emotional storytelling.
- Visual storytelling and animation effort.
- Voice, music and sound design.
- Audience engagement and community.
- Titles, thumbnails and packaging.
- Analytics and performance interpretation.
- Shorts and long-form relationships.
- Channel and creator benchmarks.
- Academic foundations and research limitations.

No fixed hook interval, retention target, cut frequency, dialogue ratio, title formula or engagement tactic is made operational until the research is reviewed and approved.

## Proposed file scope in this draft branch

- `STORY_ACQUISITION/**`
- `AUDIENCE_EXPERIENCE/**`
- `FORMATS/**`
- `GENRES/PROPOSED_PROFILE_ROADMAP.md`

The exact inventory is recorded in the branch. Additional governed changes may be proposed after the research is complete.

## Explicitly out of scope for this preparatory branch

- Changes to `CORE/`, `MODES/`, active agent instructions or global workflow.
- Changes to existing JSON Schemas or SQLite migrations.
- New API endpoints, frontend selectors or runtime behaviour.
- Live LLM prompt assembly or screenplay generation.
- Automatic copyright determinations or legal advice.
- Adoption of unverified retention benchmarks or algorithm claims.
- Activation of new genre profiles in `GENRES/REGISTRY.json`.
- Automatic access to YouTube Analytics or external accounts.

## Design invariants

1. Genre controls narrative conventions.
2. Series format controls how episodes relate to one another.
3. Channel style controls the channel's audience promise and presentation identity.
4. Story-source records describe provenance and intended use; they do not prove permission.
5. Audience-experience findings must retain evidence, publication date, context, limits and confidence.
6. Platform metrics must be interpreted using their official definitions and the relevant video format.
7. Creative quality, rights clearance, technical QC and human approval remain distinct.
8. Research findings may become defaults only through a reviewed change, with versioning and a way to revise them.
9. Keep the initial workflow practical for a solo creator or small team.
10. Never claim a documented component is executable until its runtime implementation is verified.

## Acceptance criteria for the preparatory work

- Story-source categories and record templates exist.
- Rights and originality review requirements are documented without claiming automated legal clearance.
- Audience research backlog covers the agreed research areas.
- Research-finding and experiment templates preserve evidence and limitations.
- A provisional anthology format is documented separately from genres and channel style.
- Proposed genre additions are recorded without silently activating them.
- The existing application and existing projects remain unchanged.

## Next decision after research

Once the audience-experience research is complete, review its findings alongside the genre and story-source strategy. Then submit a scoped, versioned implementation request covering the required schemas, agent instructions, context assembly, backend persistence, frontend workflows and tests. Only implement the approved scope.
