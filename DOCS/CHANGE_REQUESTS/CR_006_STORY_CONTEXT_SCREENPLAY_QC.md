---
change_request_id: CR_006
version: 0.1.0
modified_date: 2026-11-09
status: DRAFT_PROPOSAL_NOT_SUBMITTED
description: Proposed Story Bible, episode context, real screenplay generation, and evidence-based script quality workflow
dependencies:
  - CORE/CHANGE_CONTROL.md
  - CORE/RULE_HIERARCHY.md
  - CORE/HUMAN_APPROVAL_POLICY.md
  - DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md
---

# CR_006 — Story Context, Screenplay Generation and Script Quality

## 1. Governance status

**Status: DRAFT_PROPOSAL_NOT_SUBMITTED.**

This document records the proposed architecture and implementation sequence. It has
not been submitted through the local GovernanceEngine, has no verified
change_requests database record, and is not approved. The current architecture
version and proposed next version must be read from the active local database
when the request is formally submitted; they are intentionally not guessed here.

The direct-main update associated with this draft is documentation-only:
- It adds this proposal.
- It reconciles the screenplay context contract and capability map with the
  current source implementation.
- It does not edit CORE/, MODES/, SCHEMAS/, AGENTS/ definitions, database
  migrations, backend runtime code, frontend runtime code, or global workflow
  policy.

Per CORE/CHANGE_CONTROL.md, no protected architecture/schema/agent changes may
be applied while the request is pending or rejected. Approval must be recorded
through the required human review path, not inferred from this document or a
Git commit.

## 2. Objective

Make Animation Forge capable of taking a user's story idea and producing a
traceable, revisable, quality-checked screenplay that respects an approved
series world and episode brief.

The end-to-end target is:

1. Define and maintain the series world and approved canon.
2. Create an episode-specific Story Brief.
3. Assemble the exact relevant story, genre, channel and instruction context.
4. Generate and review story alternatives and a structured outline.
5. Develop scene cards and a full screenplay.
6. Produce a scene-linked audience Retention Map.
7. Run deterministic screenplay validation and independent creative critique.
8. Revise without overwriting previous versions.
9. Submit the selected revision for human creative approval.
10. Make only an approved screenplay eligible for downstream production breakdown.

This is a human-directed creative system. AI proposals never become canon or
approval automatically.

## 3. Verified starting state

The following observations were made from source on main at
0dcebb3e4b999c30cae96b210cc186c38edc5feb:

- SQLite has a series table with bible_json and an episodes table. These are
  existing storage foundations, not a versioned Story Bible service.
- SCHEMAS/PROJECT.schema.json defines primary_genre_id,
  secondary_genre_ids and channel_style_id. The current projects table and
  CreateProjectPayload do not persist or expose those selectors end to end.
- GENRES/REGISTRY.json currently registers Fantasy and Comedy. STYLES/CHANNELS.json
  has an empty channel list.
- DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md defines the intended modular context
  contract, but no runtime context assembler implements it.
- StoryAndScreenplayPipeline.develop_screenplay_revision creates a
  premise-specific editable scaffold. It does not call a provider, create
  screenplay scenes/dialogue, execute screenplay passes, or calculate creative
  scores.
- ProviderManager.invoke_llm returns SIMULATED and does not send a provider
  request or write actual usage/cost records. SecureCredentialVault is an
  in-memory test stub.
- SCRIPT_CRITIC has an instruction contract, but no independent
  evidence-backed screenplay critique service is wired.
- QualityControlEngine has predetermined demo checks; it does not inspect the
  actual screenplay or media.
- The approval engine exists. The current human review implementation depends
  on a native Windows confirmation flow and is not a cross-platform identity
  solution.
- generate_production_breakdown is deliberately unavailable until a real
  approved-script-to-scene implementation exists.

These limitations must remain visible until the relevant acceptance tests pass.

## 4. Proposed architecture

### 4.1 Series Bible

A Series Bible is the long-lived, versioned source of approved series canon.
It should cover:

- Series premise, format, themes and audience promise.
- World overview, geography, factions, cultures and historical timeline.
- Explicit supernatural, technological or magic rules and their limits.
- Recurring characters, motivations, goals, flaws, fears and relationships.
- Character voice, visual identity and continuity constraints.
- Recurring locations, objects, symbols and visual motifs.
- Series-level mysteries, season arcs and deliberately unresolved questions.
- Canon exceptions and approved changes.
- Source/provenance records and rights-review state where material is adapted.

Separate approved canon from proposals, drafts, assumptions and unresolved
questions. A proposed AI fact must not silently become an established world rule.

### 4.2 Episode Brief

Each episode must have an independent brief linked to its project and, where
applicable, its series. It should contain:

- Episode ID, title, premise and synopsis.
- Primary genre, optional secondary genres and optional channel style.
- Audience, language, target runtime and format.
- Tone, visual direction and production constraints.
- Protagonist, objective, opposition, stakes and central story question.
- Required characters and locations.
- Required beats, clues, reveals, emotional turns and ending direction.
- Relationship to series canon and previous episodes.
- Source provenance, adaptation notes and unresolved rights questions.

The Episode Brief is not itself an approved screenplay. Creative decisions
that affect canon must be separately accepted by the human owner.

### 4.3 Context assembly

Implement DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md as a deterministic runtime
service. Resolve exact profile versions and content hashes. Load only context
that is relevant to the requested episode.

Precedence:
1. System/security and global governance.
2. Project restrictions and approved series/episode canon.
3. Primary genre profile.
4. Compatible secondary genre profiles.
5. Channel style as presentation and publishing guidance.
6. Relevant department and agent instructions.
7. Current task request and output contract.

Genre, series format and channel style are independent dimensions. A channel
style cannot override canon or genre rules. Do not infer a genre or channel
style from the title.

### 4.4 Staged screenplay generation

Generation must be staged and inspectable:

1. Story analysis: dramatic engine, protagonist goal, stakes, opposition,
   theme, audience promise and constraints.
2. Hook alternatives: multiple opening approaches with the viewer question
   each creates and the story information each promises.
3. Outline: beginning, escalation, turning points, climax and resolution.
4. Scene cards: scene purpose, location, characters, objective, conflict,
   turn, clue/reveal, emotional function and estimated runtime contribution.
5. Treatment: optional intermediate prose treatment for stories that need it.
6. Screenplay: scene headings, filmable action, dialogue, transitions and
   relevant visual/audio direction.
7. Focused revisions: structure, motivation, dialogue, emotion, pacing,
   visual storytelling, continuity and production feasibility as applicable.
8. Retention Map: map viewer questions, information, tension, emotional shifts
   and payoffs to actual beats/scenes. Do not invent universal hook intervals
   or treat unsupported retention benchmarks as rules.
9. Versioning: persist each output as a new immutable revision lineage with
   generation provenance and the source revision it revises.

A 13-pass checklist is a set of review considerations, not a claim that every
pass has run or that every genre needs every pass.

### 4.5 Independent quality control

Keep three result types separate:

**Schema and deterministic validation**
- Required fields and screenplay structure.
- Stable and unique scene/character/location identifiers.
- References resolve to actual records or are explicitly marked as new proposals.
- No unresolved placeholders in a submission candidate.
- Character/location names agree with approved canon where required.
- Continuity checks are limited to facts actually recorded in the approved Bible.
- Required clues/payoffs and requested story beats are present where the brief
  declares them mandatory.
- Runtime estimate includes a documented method and uncertainty; it is not
  presented as measured playback duration.

**Creative critique**
- Story causality, character agency, motivation and consistency.
- Genre and channel fit.
- Hook/promise fulfillment.
- Suspense, mystery clue fairness and reveal setup where relevant.
- Dialogue, emotional impact, pacing and visual storytelling.
- Production feasibility and likely animation complexity.

Every creative finding must identify a specific beat, scene or passage,
explain its impact and offer a practical revision direction. Findings must
separate evidence, interpretation and subjective preference.

**Human approval**
- A technical pass is not creative approval.
- A creative critique cannot approve or rewrite the submitted draft.
- Only the configured human decision path can approve, request revision or
  reject a screenplay.
- An approved revision is immutable. A revision request creates a new draft.

### 4.6 Provider boundary

Implement at least one real LLM adapter before labelling generation operational.
The adapter must use securely supplied credentials, configurable provider/model
settings, timeouts, structured response validation and useful failure states.
Persist provider/model/request metadata and actual usage only when returned by
the provider. Never put API keys in Git, prompts, logs or generation manifests.

A mock adapter is required for deterministic tests. A mock response must be
labelled as test/simulated output and must not be presented as live generation.

## 5. Proposed implementation milestones

| Milestone | Scope | Exit condition |
|---|---|---|
| M0 — Contract and governance baseline | Approve this architecture; finalize data contracts, persistence mapping, API contracts, security and rollback design. | Approved request and reviewed schemas/migration design. |
| M1 — Story Context and Creative Bible | Versioned Series Bible, Episode Brief, canon/proposal separation, genre/style selection, persistence, APIs and UI. | Create, revise, retrieve and hash approved story context without data loss. |
| M2 — Real provider infrastructure | One live provider adapter, secure credential storage, model config, response/error handling and usage accounting. | Real configured request succeeds; failure and mock tests behave honestly. |
| M3 — Screenplay generation | Runtime context assembly, story analysis, hooks, outline, scene cards, screenplay, revisions and Retention Map. | A user premise produces a persisted, premise-specific screenplay through staged review. |
| M4 — Quality and approval | Deterministic validation, independent creative critique, revision loop and human approval integration. | Defects are detected with evidence; only human approval can approve the exact revision. |
| M5 — Integrated pilot | Run one original pilot through the entire workflow. | One complete episode has traceable source context, screenplay revisions, QC evidence and human decision. |

M1 and M2 can proceed independently after M0 is approved. M3 depends on both.
M4 depends on a persisted screenplay output from M3. M5 depends on M1–M4.

## 6. Proposed data and API scope

The exact normalized database design must be reviewed against current tables
before migration. Existing series.bible_json, episodes, characters,
environments, creative_decisions and scripts must be preserved and mapped;
do not create duplicate character/location sources without an explicit
ownership decision.

Expected contract areas:

- Series Bible document and immutable revision metadata.
- Episode Brief document and revision metadata.
- Canon fact/proposal status and accepted decision provenance.
- Story context assembly manifest with selected profile/version/hash references.
- Story analysis and outline output.
- Scene card and screenplay structure.
- Retention Map linked to outline/scene identifiers.
- Creative review findings and deterministic validation results.
- Generation manifest with provider/model/request metadata and actual usage
  when available.

Expected API groups, subject to route design:

- Read/create/update Series Bible drafts and revisions.
- Read/create/update Episode Brief drafts and revisions.
- Retrieve approved canon and selected context for an episode.
- Generate and retrieve story analysis, hooks and outlines.
- Generate and retrieve scene cards and screenplay revisions.
- Submit a screenplay revision for critique/validation.
- Retrieve findings and create a new revision after requested changes.
- Submit the exact revision for human approval and retrieve its decision.

All mutating/read API routes must preserve the local IPC-token security
requirements. Do not expose a generic route that lets the model edit approved
canon or approve a creative deliverable.

## 7. Proposed repository scope

Expected files to design/change only after the request is approved:

- SCHEMAS/STORY_BIBLE.schema.json
- SCHEMAS/EPISODE_BRIEF.schema.json
- SCHEMAS/STORY_ANALYSIS.schema.json
- SCHEMAS/SCREENPLAY_OUTLINE.schema.json
- SCHEMAS/SCENE_CARD.schema.json
- SCHEMAS/RETENTION_MAP.schema.json
- SCHEMAS/CREATIVE_REVIEW.schema.json
- SCHEMAS/SCREENPLAY_GENERATION_MANIFEST.schema.json
- backend/database.py and additive migration definitions.
- backend/departments/story_context.py (or a reviewed equivalent).
- backend/departments/story_pipeline.py.
- backend/providers/manager.py and a real provider adapter.
- backend/main.py API contracts/routes.
- frontend story context, outline, screenplay and review components.
- TESTS for schemas, migrations, provider behavior, context isolation,
  generation, versioning, QC findings and approval gates.
- Relevant DOCS, capability map, developer guide and root AGENTS.md.

The final file list must be narrowed before approval and updated if the design
changes. The list is a proposal, not permission to edit these files now.

## 8. Compatibility and risk controls

- Use additive SQLite migrations. Do not replace the tracked database or drop
  existing fields/tables.
- Preserve existing project records and the human-readable legacy genre field
  while stable profile IDs are migrated.
- Existing series.bible_json must remain readable during migration.
- Missing or retired genre/style profiles must fail clearly or use an
  explicitly reviewed migration path.
- A provider failure must not silently produce a canned draft or mark a stage
  complete.
- Context must be project/series/episode scoped; never leak another project's
  private story material.
- Draft canon, approved canon, creative decisions and screenplay approval are
  distinct state dimensions.
- File/database disagreement must be surfaced, not silently reconciled.
- Rights/source uncertainty must remain visible and must not be automatically
  declared cleared.
- Cost, usage, score, runtime and QC results must be based on actual measured
  or provider-returned evidence, with estimates labelled as estimates.

## 9. Testing requirements

Before any milestone is called complete:

1. Validate every new/changed JSON Schema against valid and invalid fixtures.
2. Test additive migrations on a copy of the current database and verify
   SQLite integrity and preservation of pre-existing records.
3. Test Bible and Episode Brief versioning, hashes, approval state and
   project/series isolation.
4. Test exact genre/style resolution, unknown/retired IDs, profile hashes and
   context invalidation.
5. Test real provider success, malformed response, timeout, authentication
   failure and rate-limit/error handling without leaking credentials.
6. Test deterministic mock provider behavior separately from live provider use.
7. Test outline/scene/screenplay structure, revision lineage and immutability.
8. Test QC findings against deliberately defective screenplay fixtures.
9. Test that creative critique and technical QC cannot approve.
10. Test that only the authenticated human approval path can approve the exact
    submitted revision.
11. Run the Python test suite, instruction repository validator, frontend
    production build and Rust check where affected.
12. Run one end-to-end pilot and preserve the evidence/reports.

Do not claim unrun checks passed. The demo runner's known tracked-file side
effects must be inspected and restored after tests.

## 10. Rollback plan

- Before database work, preserve a timestamped copy of the local SQLite
  database and record its SHA-256 and SQLite integrity result.
- Preserve exact pre-change copies and hashes for every in-scope file outside
  CORE/MODES because the built-in architecture snapshot does not cover them.
- Keep implementation in small, reviewable commits within the approved scope.
- Prefer forward corrective migrations over deleting records or replacing the
  database after user data has been written.
- On a failed code milestone, revert only its approved source-file changes and
  retain diagnostic logs/test evidence.
- If a migration has run against user data, stop and reconcile the database
  state before attempting rollback. Never blindly restore an old database over
  newer user work.
- Verify repository state, database integrity, and the affected workflow after
  rollback.

## 11. Out of scope

- Automatic rights clearance or legal conclusions.
- Automatic publication to YouTube or access to creator analytics accounts.
- Automatic canon approval or screenplay approval by an AI agent.
- Full animation/rendering, asset generation, TTS or video editing implementation.
- Forcing a channel style when the project is channel-neutral.
- Applying unverified retention formulas or fixed hook/cut intervals.
- Replacing the existing tracked SQLite database or rewriting Git history.

## 12. Definition of done

CR_006's target is not met by a prompt template, a new screen, a schema file,
a mock response or an isolated demo. The target is one end-to-end episode with:

- Persisted and versioned approved story context.
- Traceable genre/style and instruction provenance.
- A real configured provider response.
- A premise-specific outline, scene cards and screenplay.
- A scene-linked Retention Map.
- Evidence-based deterministic checks and independent creative critique.
- Revision history with approved versions immutable.
- A human decision for the exact final screenplay revision.
- Reproducible tests and a recorded integrated pilot result.
