---
prompt_id: DOCS_SCREENPLAY_CONTEXT_ASSEMBLY
version: 1.0.0
modified_date: 2026-11-09
description: Runtime contract for assembling modular genre, channel-style, project and screenplay instructions
dependencies: ["GENRES_INDEX", "STYLES_INDEX", "AGENT_SCREENWRITER", "CORE_RULE_HIERARCHY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Specify deterministic profile selection and provenance for screenplay generation
---
# Screenplay Context Assembly Contract

## Purpose

Build the screenwriter's context from reusable modules rather than one giant prompt. Keep genre conventions, channel identity, project canon, task instructions and provider configuration separate so they can be reused and versioned independently.

This is a target runtime contract. The current `StoryAndScreenplayPipeline` still creates a fixed demonstration screenplay and does not yet implement this assembler. The current provider manager also records usage estimates and metadata without making a real LLM request. The first executable screenplay milestone must implement and test at least one actual provider call before this flow is labelled operational.

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
- Approved Story Bible, series bible and previous screenplay revision.
- Requested screenplay format and creative constraints.

## Selection validation

1. Resolve the primary genre ID against `GENRES/REGISTRY.json`.
2. Resolve each secondary genre ID; reject duplicates and unknown IDs.
3. Resolve the channel style ID against `STYLES/CHANNELS.json`, if selected.
4. Load the exact registered profile version, not whichever file happens to be newest on disk.
5. Reject missing/retired profiles unless the task explicitly requests migration or analysis.
6. Record profile IDs, versions and source content hashes in the generation manifest.

## Context layers and precedence

Construct the model context in this order:

1. System and global creative authority rules.
2. Project restrictions and approved canon.
3. Primary genre instruction.
4. Secondary genre instructions, labelled as complementary influences.
5. Channel style guide, labelled as presentation and publishing direction.
6. Screenwriter and relevant department instructions.
7. Current task input, required schema and acceptance checklist.

The ordering of prompt text does not let lower-priority material override higher-priority rules. Contradictions must be resolved explicitly. Project-specific instruction beats profile defaults where the project's owner has deliberately made an exception. A channel guide cannot silently alter world rules or genre logic.

## Generation procedure

1. Normalize title, premise, audience, runtime, language, genre selections and channel selection.
2. Build a short creative brief from explicit user inputs. Label assumptions separately.
3. Analyze the story engine, protagonist goal, stakes, opposition, theme and ending requirements.
4. Produce a beat/act outline before full screenplay prose.
5. Generate scenes with clear sluglines, playable visual action, character objectives, conflict, turns and dialogue.
6. Run focused reviews: genre fit, channel format fit, structure, character motivation, dialogue, pacing, continuity, visual storytelling and production feasibility.
7. Return the screenplay, a concise review report, open decisions and a production-breakdown preview.
8. Persist a new draft revision only through a real implemented persistence method. Never report success if only an in-memory response was produced.

## Provenance manifest

Every generation should capture:
- Project ID and script revision.
- Primary genre ID, version and SHA-256 content hash.
- Secondary genre IDs, versions and hashes.
- Channel style ID, version and hash, or explicit `NONE`.
- Project brief and Story Bible revisions/hashes used.
- Screenwriter instruction version/hash.
- Provider ID, actual model ID, request ID and provider response metadata where available.
- Prompt assembly version, generation parameters, timestamps and validation results.

Do not store API keys or other secrets in the manifest. Do not fabricate token counts, provider costs or model identity.

## Context sizing and caching

- Load only selected profiles and directly relevant canon. Do not inject the entire genre library or every channel guide into every request.
- Keep reusable profile text as separate blocks and calculate a content hash for each block.
- Cache only immutable profile content by profile ID, version and content hash.
- Invalidate assembled context when any selected profile, project canon, screenwriter instruction or task input changes.
- Never reuse one project's private story context in another project.

## Acceptance tests for the eventual implementation

- Fantasy + Comedy + Channel A resolves exactly those three profile blocks.
- The same Fantasy project with Channel B changes only the channel-style block, not the primary genre block or canon.
- Unknown, duplicate and retired IDs are rejected or explicitly migrated.
- Every generated screenplay record can reproduce the exact profile versions and content hashes used.
- No fixed demonstration screenplay is returned as though it was generated from the user's premise.
- Provider failure leaves the draft task failed/blocked with diagnostic evidence; it does not silently return a canned screenplay.
