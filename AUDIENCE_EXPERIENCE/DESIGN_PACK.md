# Audience Experience & Screenplay Engineering — Design Pack

**Status:** DRAFT_FOR_HUMAN_REVIEW. Documentation and contracts only; not active runtime behaviour.

## 1. Goal

Help Animation Forge make stories understandable, distinctive, emotionally engaging, visually producible, and honest about the experience promised to viewers. Preserve selected genre, series format, channel style, canon, rights constraints, and human creative authority.

Audience Experience is cross-cutting. It does not replace genre, format, channel style, story-source governance, rights review, technical QC, or approval policy.

## 2. Screenwriting workflow

The practical process is defined in PLAYBOOKS/SCREENPLAY_ENGINEERING.md:

1. Intake the idea, brief, approved canon, format, audience, and production constraints.
2. Find the dramatic engine: protagonist, objective, stakes, opposition, obstacle, and consequential choice.
3. Define the audience promise and the ending that fulfils it.
4. Build character pressure and motivation.
5. Design the causal story spine before writing dialogue.
6. Track rules, clues, setups, and payoffs where relevant.
7. Create outline and scene cards with a clear scene change/function.
8. Generate distinct hook options tied to the actual story.
9. Draft filmable screenplay pages with purposeful dialogue and visual/audio storytelling.
10. Create the Retention Map from the exact screenplay revision.
11. Conduct independent evidence-led creative review.
12. Revise in priority order, preserve revision lineage, and submit for human review.

This is a flexible working sequence, not a fixed act structure, scene count, or universal timing formula. Combine stages for simple formats; expand them when story complexity requires it.

## 3. Research-derived design components

The Deep Research report recommends genre-tailored screenplay templates; opening hooks; a beat-by-beat Retention Map; mystery/horror checklists; visual/audio playbooks; title/thumbnail packaging; analytics interpretation; an advisory QA rubric; and later integration across Story Architect, Screenwriter, and Script Critic.

Existing artifacts live in PLAYBOOKS/, HOOK_LIBRARY/, SCRIPT_FORMATS/, SCHEMAS/, QUALITY_CHECKS/, and EXAMPLES/. Timing and retention suggestions remain hypotheses, not platform guarantees.

## 4. Screenplay formats

### Animated long-form episode

Initial project option: 6–10 minutes. The format template includes identity/source, audience promise, dramatic engine, character pressure, story spine, logic ledger where relevant, scene cards, screenplay pages, production-critical notes, Retention Map, review, and runtime report.

Cold open/setup/development/midpoint/climax/resolution windows are optional examples, not immutable scene lengths or act requirements.

### YouTube Short

Initial option: 30–60 seconds. The Short should deliver a coherent promise of its own: legible opening, minimum necessary context, one central development, and a payoff or deliberate open question.

A 3–6 minute short episode is a different format and needs room for a more complete dramatic arc.

## 5. Hook library

The 30-entry library contains patterns across Mystery, Visual Anomaly, Emotional, Supernatural, and Suspense categories. Select based on premise, genre, audience, and format. For each candidate record the question/emotional promise and later fulfilment beat. No hook should imply a reveal the story does not deliver.

## 6. Retention Map

For each meaningful beat record what the viewer knows, active question/expectation, what changes, intended emotional tone, visual/audio carrier, setup/payoff references, exact scene/beat ID, and estimated duration only where useful.

The map must be created from and validated against the actual screenplay revision. It is an editorial model, not measured analytics or a prediction of what every viewer will feel.

## 7. Mystery and horror integrity

Use genre-specific prompts only when relevant:
- Occult Detective: case clarity, clue-before-reveal, fair deductions, consistent supernatural rules, no deus ex machina.
- Dark Folklore: source/context research, variants, adaptation choices, respectful treatment, and human review.
- Psychological Horror: motivation, fair unreliable-narration signals where used, escalating fear, and earned ending.
- Cosmic Horror: scale, restraint, consistent local facts, believable consequences, and atmosphere serving story logic.

See PLAYBOOKS/GENRE_MYSTERY_HORROR_CHECKLISTS.md.

## 8. Visual and audio storytelling

Prioritise narrative-critical shots and readable clues; use camera, lighting, composition, and motion to guide attention. Use voice, ambience, music, silence, and Foley to support comprehension and emotion. Distinguish story-critical requirements from optional embellishment.

## 9. Packaging

Generate several title and thumbnail candidates. Check that each candidate's promise is fulfilled by the opening and complete episode. Prefer clear, specific, story-consistent imagery. Text length and keyword formulas are optional. A human selects the published package.

## 10. Analytics feedback

Record available creator-side metrics with definition, collection date, reporting window, video format, traffic context, and sample limitations. Treat metrics as investigation signals. Low CTR does not prove a thumbnail defect; an early drop does not prove a hook failure; a spike can mean rewatching, confusion, or a memorable moment. Compare similar formats and multiple videos. Never infer private retention from public view counts.

## 11. Creative review and revision

Review the screenplay itself before relying on the Retention Map. Assess promise, premise, agency, motivation, stakes, causality, setup/payoff, clue integrity, scene progression, dialogue, visual/audio storytelling, emotional credibility, genre, originality, ending, production feasibility, and runtime evidence as relevant.

Every finding cites exact evidence, separates observation from interpretation, explains likely impact, states severity, and recommends a targeted action. The writer responds to major findings and rechecks affected downstream scenes. Numeric scores remain optional and advisory; no average gate is active.

## 12. Integration boundaries

Proposed future responsibilities:
- Story Architect: audience promise, dramatic engine, hook alternatives, story beats, and packaging candidates.
- Screenwriter: screenplay plus traceable Retention Map and requirement coverage.
- Script Critic: independent evidence-based review; no approval or self-rewrite.
- Storyboard/Camera/Audio agents: consume relevant visual/audio annotations.
- Quality Controller: objective technical checks only, not a prediction of audience response.

No agent instruction, database, API, frontend, project schema, global output contract, or active workflow is changed by this design pack. Verify implementation before claiming end-to-end functionality.

## 13. Pilot acceptance exercise

Use The Lantern Ledger — Case 01: The Thirteenth Bell of St. Jude, or another approved test premise. Produce audience promise, dramatic engine, hook alternatives, story spine, outline, scene cards, screenplay, Retention Map, and creative review. Verify hook fulfilment, character motivation, causal bridges, clue/rule fairness, scene purpose, map references, visual/audio handoffs, production scale, and separate human decisions.

## 14. Implementation next step

Submit and complete a governed change request for schemas, agent instructions, context assembly, persistence, APIs, frontend panels, migrations, tests, and rollback. Only implement protected changes after human approval under CORE/CHANGE_CONTROL.md.
