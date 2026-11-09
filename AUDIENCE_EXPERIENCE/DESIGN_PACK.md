# Audience Experience & Screenplay Engineering — Design Pack
**Status:** DRAFT_FOR_HUMAN_REVIEW. Documentation and contracts only; not active runtime behaviour.

## 1. Goal
Help Animation Forge make stories understandable, visually producible and emotionally engaging while preserving the selected genre, series format and human creative authority. Audience Experience is cross-cutting; it does not replace genre, format, channel style, rights governance or technical QC.

## 2. Source report recommendations
The Deep Research report recommends genre-tailored screenplay templates; a library of 30+ opening hooks; a beat-by-beat Retention Map; playbooks for mystery/horror, visual storytelling and audio; title/thumbnail packaging; analytics interpretation; an advisory QA rubric; and integration across Story Architect, Screenwriter and Script Critic.

The implementation artifacts live in `PLAYBOOKS/`, `HOOK_LIBRARY/`, `SCRIPT_FORMATS/`, `SCHEMAS/`, `QUALITY_CHECKS/` and `EXAMPLES/`.

## 3. Screenplay format specification

### Animated long-form episode
Initial project target: 6–10 minutes. The source report proposes this starting structure:

| Section | Suggested starting window | Purpose |
|---|---:|---|
| Cold open / hook | 0:00–0:30 | Present a mystery, visual anomaly, urgent reaction or striking question. |
| Setup | 0:30–1:30 | Establish protagonist, setting, case and stakes. |
| Investigation / development | 1:30–4:00 | Reveal clues progressively through action and concise dialogue. |
| Midpoint development | Around 4:00 | Reverse an assumption or alter the interpretation of evidence. |
| Climax | Later act | Bring clues and supernatural rules together under pressure. |
| Resolution | Final section | Deliver payoff and optionally hint at wider series mythology. |

Windows are illustrative, not immutable scene lengths. Compress or expand for the actual runtime.

Required outline fields: title, primary/secondary genre, series format, audience promise, protagonist, objective, stakes, central question, opposition, supernatural rule where relevant, clues/red herrings, main beats, emotional progression, production risks and unresolved decisions.

Use scene headings (INT./EXT. + location + time). Separate visible action, dialogue/narration, audio cues, relevant visual/camera direction, scene/beat IDs and Retention Map references.

### YouTube Short
Initial target: 30–60 seconds; the source report gives a 45–60 second example.
1. Immediate hook (example starting target: first 3 seconds).
2. Core development: one clear context item, escalation or evidence.
3. Payoff/tag: answer, twist or deliberate open question.
A Short should deliver its own promise and work for a viewer without prior episode knowledge.

The source report also mentions 3–6 minute short episodes. Do not confuse these with vertical 30–60 second YouTube Shorts; a short episode needs a more complete dramatic arc.

## 4. Hook library
The 30-entry library contains six patterns each for Mystery, Visual Anomaly, Emotional, Supernatural and Suspense hooks. Select by premise, genre and audience; attach the question raised and the later beat that fulfils it. No hook should imply a reveal the story does not deliver.

## 5. Retention Map
For each major beat record:
- What the viewer knows now.
- What they may be wondering.
- What new information is revealed.
- Intended emotional tone.
- Pacing note / estimated duration where helpful.
- Visual focus and audio focus.
- Payoff references to earlier beats.
- Linked scene ID.

The map is an editorial model of intended viewer experience, not measured analytics and not a prediction of what every viewer will feel. Estimate timecodes during writing and replace them with measured values only after animatic/video review.

## 6. Mystery and horror integrity
Use genre-specific review prompts:
- **Occult Detective:** case clarity, clue-before-reveal, fair deductions, consistent supernatural rules, no deus ex machina.
- **Dark Folklore:** source/context research, variants, adaptation choices, respectful treatment and human rights review.
- **Psychological Horror:** motivation, clear unreliable narration signals where used, escalating fear and an earned ending.
- **Cosmic Horror:** scale, restraint, consistent local facts, believable consequences and atmosphere serving story logic.

See `PLAYBOOKS/GENRE_MYSTERY_HORROR_CHECKLISTS.md`.

## 7. Visual and audio playbooks
Prioritise narrative-critical shots and readable clues; use camera, lighting and motion to guide attention. Use voice, ambience, music, silence and Foley to support comprehension and emotion. See the dedicated visual/audio playbooks.

## 8. Packaging
Generate several title and thumbnail candidates. Check that each candidate's promise is fulfilled by the opening and the complete episode. Prefer one clear subject, readable contrast and imagery specific to the story. Text length and keyword formulas are optional design choices, not rules.

## 9. Analytics feedback
Record available creator-side metrics with definition, collection date, reporting window, video format and context: impressions, CTR, views, average view duration, average percentage viewed, watch time, intro retention, retention spikes/dips, returning viewers and Shorts viewed-vs-swiped where applicable.

Treat metrics as investigation signals. Low CTR does not prove a thumbnail defect; an early drop does not prove a hook failure; a spike can mean rewatching, confusion or a memorable moment. Compare similar formats and multiple videos. Never infer private retention from public view counts.

## 10. Creative review
Review hook strength, premise clarity, plot structure, clue logic, character depth, visual storytelling, audio design, engagement potential and production feasibility. Use cited scene evidence and recommendations. Rights/policy, story integrity and production blockers remain separate mandatory checks.

The report proposes 0–10 scores and an example average gate around 7. This branch does not activate a numeric gate. Calibration and human review are required before any threshold can block progression.

## 11. Integration boundaries
Proposed future responsibilities:
- Story Architect: audience promise, hook alternatives, story beats and packaging candidates.
- Screenwriter: screenplay plus structured Retention Map.
- Script Critic: evidence-based creative review and genre-integrity findings.
- Storyboard/Camera/Audio agents: consume relevant visual/audio annotations.
- Quality Controller: objective technical checks only, not a prediction of audience response.

No agent instruction, database, API, frontend, project schema, global output contract or workflow has been modified by this design pack. The screenplay pipeline's existing demonstration-only limitation must be addressed before claiming these features work end-to-end.

## 12. Pilot acceptance exercise
Use **The Lantern Ledger — Case 01: The Thirteenth Bell of St. Jude**. Produce an audience promise, three candidate hooks, title/thumbnail options, beat outline, screenplay, Retention Map and creative review. Verify:
- The selected hook is fulfilled.
- The clues precede the solution.
- The viewer can understand the central question.
- The map accurately references real scenes.
- Visual/audio handoffs identify what must be seen/heard.
- The story can be produced at the target scale.
- Human decisions are recorded separately from agent suggestions.

## 13. Implementation next step
Submit a governed change request for schemas, agent instructions, context assembly, persistence, APIs, frontend panels, migrations, tests and rollback. Only implement after human approval under `CORE/CHANGE_CONTROL.md`.
