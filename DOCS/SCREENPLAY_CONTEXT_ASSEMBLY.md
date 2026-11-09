---
prompt_id: DOCS_SCREENPLAY_CONTEXT_ASSEMBLY
version: 1.0.2
modified_date: 2026-11-09
description: Runtime contract for assembling modular genre, channel-style, project and screenplay instructions
dependencies: ["GENRES_INDEX", "STYLES_INDEX", "CORE_RULE_HIERARCHY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Specify deterministic profile selection and provenance for screenplay generation
  - version: 1.0.1
    date: 2026-11-09
    summary: Remove AGENT_SCREENWRITER from dependencies to break the agent/contract dependency cycle
  - version: 1.0.2
    date: 2026-11-09
    summary: Reconcile runtime status with the scaffold-only screenplay and simulated provider; define proposed Series Bible and Episode Brief inputs
---

# Screenplay Context Assembly Contract

## Purpose and implementation status

Build the screenwriter's context from reusable modules rather than one giant
prompt. Keep genre conventions, channel identity, approved canon, episode
requirements, task instructions and provider configuration separate so they can
be reused and versioned independently.

This is a target runtime contract, not an implemented assembler. The current
StoryAndScreenplayPipeline creates a premise-specific editable scaffold only;
it does not call an LLM or generate scene prose. ProviderManager returns
SIMULATED, estimates prompt length for display, and does not make a provider
request or persist actual usage/cost records. CR_006 proposes the implementation
sequence; it is a draft and has not been submitted to GovernanceEngine or approved.

## Inputs

Required:
- Project ID and project brief.
- One primary genre ID.
- User's short story idea or premise.
- Target audience, language and runtime.
- Screenwriter task and expected output contract.

Optional:
- Secondary genre IDs.
- Channel style ID.
- Approved, versioned Series Bible and episode-specific story decisions.
- Previous screenplay revision and accepted revision feedback.
- Requested screenplay format and creative constraints.

The Story Bible and Episode Brief are proposed data domains under CR_006.
Existing series.bible_json and episodes storage do not yet provide versioned,
schema-validated Bible/brief APIs or UI. Do not treat raw JSON fields or demo
character/environment rows as an approved canon service.

## Selection validation

1. Resolve the primary genre ID against GENRES/REGISTRY.json.
2. Resolve each secondary genre ID; reject duplicates and unknown IDs.
3. Resolve the channel style ID against STYLES/CHANNELS.json, if selected.
4. Load the exact registered profile version, not whichever file happens to be newest on disk.
5. Reject missing/retired profiles unless the task explicitly requests migration or analysis.
6. Record profile IDs, versions and source content hashes in the generation manifest.

The current project database/API does not yet persist and expose all of the
genre/style identifiers described in the project schema. Treat selection
validation above as a target requirement until the end-to-end wiring is implemented.

## Context layers and precedence

Construct the model context in this order:

1. System and global creative authority rules.
2. Project restrictions and approved Series Bible revision / accepted episode decisions.
3. Primary genre instruction.
4. Secondary genre instructions, labelled as complementary influences.
5. Channel style guide, labelled as presentation and publishing direction.
6. Screenwriter and relevant department instructions.
7. Current task input, required schema and acceptance checklist.

The ordering of prompt text does not let lower-priority material override
higher-priority rules. Contradictions must be resolved explicitly. A
project-specific instruction beats a profile default only where the project's
owner has deliberately approved that exception. A channel guide cannot silently
alter world rules or genre logic. Draft proposals and unresolved assumptions
must remain visibly separate from approved canon.

## Generation procedure

1. Normalize the title, premise, audience, runtime, language, genre selections
   and channel selection. Preserve missing values as unknown; do not infer
   genre or channel from the title.
2. Load the approved Series Bible revision and current Episode Brief, scoped
   to the selected project/series/episode. Label unapproved proposals and
   assumptions separately.
3. Build a normalized creative brief from explicit user inputs.
4. Analyze the story engine, protagonist goal, stakes, opposition, theme,
   audience promise and ending requirements.
5. Generate hook alternatives and a beat/act outline before full screenplay
   prose. Retain alternatives until a human or authorized workflow selects one.
6. Generate scene cards with location, characters, dramatic purpose, conflict,
   turn, clues/reveals, emotional function and intended runtime contribution.
7. Generate screenplay scenes with clear sluglines, filmable action, character
   objectives, conflict, turns, dialogue and relevant visual/audio direction.
8. Run focused reviews: genre fit, channel format fit, structure, character
   motivation, dialogue, pacing, continuity, mystery/clue fairness where
   applicable, visual storytelling and production feasibility.
9. Produce a Retention Map linked to actual outline beats/scenes. Do not insert
   arbitrary hook intervals or unsupported retention claims.
10. Return the screenplay, validation and creative-review reports, open
    decisions and a production-breakdown preview.
11. Persist each draft/revision with provenance through a real persistence
    method. Never report success if only an in-memory response was produced.

A documented 13-pass checklist is a set of review considerations, not a claim
that all passes execute for every screenplay or that every genre requires each
pass.

## Provenance manifest

Every generation should capture:
- Project ID, episode ID and script revision.
- Primary genre ID, exact version and SHA-256 content hash.
- Secondary genre IDs, versions and hashes.
- Channel style ID, version and hash, or explicit NONE.
- Project brief and Episode Brief revisions/hashes used.
- Series Bible revision/hash and the approved canon facts included in context.
- Story outline, scene-card and Retention Map revision IDs/hashes where generated.
- Screenwriter instruction version/hash.
- Provider ID, actual model ID, request ID and provider response metadata where available.
- Prompt assembly version, generation parameters, timestamps and validation results.

Do not store API keys or other secrets in the manifest. Do not fabricate token
counts, provider costs, model identity or usage. Mock/simulated provider output
must carry an explicit test/simulation label.

## Review and approval boundary

Creative critique and deterministic technical validation are separate outputs.

**Creative critique** evaluates story causality, character motivation and
consistency, dialogue, pacing, audience promise, visual storytelling, genre fit
and production feasibility. Findings must point to a scene, beat or passage
and distinguish evidence from interpretation and subjective preference.

**Deterministic validation** checks the actual stored screenplay: required
fields, identifiers, scene references, unresolved placeholders, continuity
facts explicitly recorded in approved canon, declared mandatory beats/clues
and a documented runtime estimate. Runtime is an estimate unless actual
playback has been measured.

A check that was not run must be reported as NOT_TESTED. No fabricated score,
pass, token usage, provider identity or cost is allowed. Technical QC does not
grant creative approval. Only the configured human approval flow can approve
a screenplay revision. Approved revisions remain immutable; requested
changes create a new revision.

## Context sizing and caching

- Load only selected profiles and directly relevant canon. Do not inject the
  entire genre library or every channel guide into every request.
- Keep reusable profile text as separate blocks and calculate a content hash
  for each block.
- Cache only immutable profile content by profile ID, version and content hash.
- Invalidate assembled context when any selected profile, approved project
  canon, episode brief, screenwriter instruction or task input changes.
- Never reuse one project's private story context in another project.

## Acceptance tests for the eventual implementation

- Fantasy + Comedy + Channel A resolves exactly those three profile blocks.
- The same Fantasy project with Channel B changes only the channel-style block,
  not the primary genre block or approved canon.
- Unknown, duplicate and retired IDs are rejected or explicitly migrated.
- Context assembly uses the exact approved Bible/brief revisions and hashes;
  draft canon is not silently included as fact.
- Every generated screenplay record can reproduce the exact profile versions
  and content hashes used.
- A premise-specific generation creates a persisted outline, scene cards and
  screenplay, not a canned demonstration or scaffold reported as finished.
- Provider failure leaves the task failed/blocked with diagnostic evidence; it
  does not silently return a canned screenplay.
- Creative critique and technical validation return separate, evidence-backed
  results; neither can approve the screenplay.
