# Existing Script Framework Audit

**Audit date:** 2026-11-10  
**Scope:** Existing script creation, source research, review, QC, runtime, governance, and the ten-script YouTube experiment.  
**Status:** Repository evidence audit; no framework behavior changed by this document.

## Current framework: what exists

| Area | Existing assets | Actual boundary |
|---|---|---|
| Script lifecycle | `backend/departments/story_pipeline.py`; Story Workspace routes in `backend/main.py` | CR_006 includes live-provider stages for analysis, hooks, outline, scene cards, screenplay and a retention map, with a human approval gate for the latest outline. The deterministic mock is labelled. The older `develop_screenplay_revision()` creates a scaffold only. Neither route constitutes open-ended source research or factual clearance. |
| Context and versioning | `backend/departments/story_context.py`; Story Bible, Episode Brief, context manifest schemas | Versioned context and immutable approved canon are assembled with source refs and hashes. This is strong groundwork for traceable creative constraints. |
| Writing guidance | `AGENTS/SCREENWRITER/INSTRUCTION.md`; `AUDIENCE_EXPERIENCE/SCREENWRITING_CONSTITUTION.md`; `AUDIENCE_EXPERIENCE/PLAYBOOKS/SCREENPLAY_ENGINEERING.md` | The constitution and playbook are draft/advisory. The screenwriter contract distinguishes the scaffold from staged generation. The playbook is animation/script oriented and does not yet describe the full researched YouTube documentary lifecycle. |
| Story acquisition | `STORY_ACQUISITION/RESEARCH_WORKFLOW.md`, source dossier and concept templates | This is a manual, source-aware process. There is no automatic source discovery or rights-clearance engine. It correctly separates documented fact, interpretation, rights questions and concept selection. |
| Research agent | `AGENTS/RESEARCH_ANALYST/INSTRUCTION.md` | Technical R&D role; not a general live-web research service and not a documentary fact-checking engine. Its instruction explicitly warns against treating fixed samples as measurements. |
| Creative critique | `backend/qc/screenplay_qc.py`; `AGENTS/SCRIPT_CRITIC/INSTRUCTION.md`; creative review schemas/checklists | The staged critique can call a provider and requires evidence fields. The deterministic mock cannot judge quality. The checklist/rubric are advisory drafts; a separate Audience Experience review schema requires scores, which conflicts with the no-score/no-average guidance elsewhere. This needs governance review before integration, not an unapproved schema edit. |
| Deterministic QC | `DeterministicValidator` in `backend/qc/screenplay_qc.py` | Checks selected structural conditions against stored screenplay/scene-card/brief data, with `NOT_TESTED` for missing canon. It does not verify historical or scientific claims, guarantee scene logic, or validate general Markdown against a complete documentary schema. |
| Runtime | `AUDIENCE_EXPERIENCE/SCRIPT_FORMATS/RUNTIME_ESTIMATION_STANDARD.md` and experiment counter | Standard distinguishes estimates from measurements. Experiment uses narration-only words, a stated pace, and planned hold ranges. Runtime remains `SCRIPT_ESTIMATE` until timed recording/animatic/final export. Existing sample scene-card runtime sums are estimates, not playback. |
| Format and retention | `AUDIENCE_EXPERIENCE/SCRIPT_FORMATS/`, playbooks, hook library, Retention Map schema | Guidance discourages fixed beat intervals and treats a map as editorial intent, not viewer data. Existing formats skew toward animation/short screenplay rather than narrated long-form documentary. |
| Governance | `CORE/CHANGE_CONTROL.md`; `AGENTS.md` | Changes to `CORE/`, `MODES/`, `SCHEMAS/`, agent instructions, or global workflow structures require a formal change request and authenticated approval. The new framework must first be isolated; proposals do not grant approval. |

## Ten-script experiment: source files read

All ten original and ten revised scripts were read, along with all first and second independent reviews, per-script change reports, the cross-script experiment report, research notes, progress tracker, concept selection and the framework-change proposal. Original scripts are under `PROJECTS/YOUTUBE_SCRIPT_EXPERIMENT/SCRIPTS/ORIGINAL/`; revisions are under `SCRIPTS/REVISED/`; reviews and reports are preserved in their existing directories.

The experiment has no published videos, audience interviews, timed narration, animatics, or YouTube Analytics. Its reviewer conclusions are editorial judgments, not measured retention or click results. Every final runtime remains `SCRIPT_ESTIMATE`.

## Cross-script findings from the actual revisions

| Script | Story engine and review lesson | Residual/limit recorded in its review history |
|---|---|---|
| YS01, Great Smog | Historical cause → public-health consequence → policy response. Review prompted narrower title, sourced mortality wording, less repetition, and a concrete post-Act consequence. | The mortality passage still needs simple visual treatment; confirm legal wording on smoke-control areas before recording. |
| YS02, Petrov warning | High-stakes decision under uncertainty. Establish the event before correcting the “saved the world” legend; attribute evidence and keep command authority/counterfactual bounded. | Career consequences must not be over-attributed to one night; make schematic visuals clear. |
| YS03, Lake Natron | Image mystery → context correction → chemistry → ecological reversal. Keep “some remains” in the opening; trim repeated correction and ending recap. | The reviewed final runtime is an estimate; the source record does not establish each photographed animal's cause of death. |
| YS04, memory reports | Familiar thought experiment → controlled study → implications and limits. Title was narrowed to reported remembering; source attribution, trauma-memory scope, and witness-practice source were corrected. | Generalize from a lab study cautiously; individual memories require independent evidence. |
| YS05, Tacoma Narrows | Engineering failure investigation. Correct chronology at event-level precision; distinguish first damage from final collapse; explain feedback as a visible causal sequence. | Exact trigger remains disputed; preserve that uncertainty. |
| YS06, Endurance | Staged survival with successive failed plans. Add named rescue attempts and the final rescue; remove duplicate payoff; define terms and stabilize map geography. | Historic details depend on source verification; do not conflate the Weddell Sea crew with the entire expedition. |
| YS07, identity copies | Philosophical thought experiment. Remove an unexplained constraint; clarify who the viewer is in the scenario; give abstract claims an ordinary sleep example and a promise with relational stakes. | One final orientation sentence was changed after second review and did not receive a third independent review. The premise remains explicitly fictional. |
| YS08, Tambora | Climate mechanism → regional weather → crop/price consequences. Name the regional comparison baseline, explain aerosol terms, use sourced local examples, and pace the dense mechanism. | Reviewer retained an information-density note for the 02:50 section; no audience comprehension test exists. |
| YS09, submarine cables | Network journey plus documented 2024 outage. Replace hypothetical failure with a real case; qualify variation by country; distinguish backup routes from usable capacity. | Current outage causes and scope need date-aware verification before recording; no universal continuity claim. |
| YS10, traffic waves | Everyday contradiction → controlled experiment → mechanism and limits. Bound “no cause,” qualify the ring-road setup, distinguish roadblocks and waves, and remove blame-oriented advice/repetition. | The lab setup is not a highway; safe spacing is not presented as a congestion cure. |

## Portfolio strengths to preserve

- Distinct story engines fit the subject: investigation, event chronology, visual mystery, controlled experiment, infrastructure journey, survival chain, or bounded thought experiment.
- Stronger openings name the actual subject and set up a question that the script later answers.
- Technical ideas become clearer when a concrete visual model is linked to the real evidence, and when the narrator marks the model's limits.
- Real-world examples improve specificity when their source and scope are secure (YS09); counterfactuals and disputed mechanisms remain explicitly bounded (YS02, YS05).
- Revisions protect mature subject matter while using plain, spoken English. The language goal is accessibility for an average 12-year-old, not restricting topic depth.
- Review findings that pointed to a particular phrase, timecode, source, visual or map reference were actionable. Targeted edits could preserve strong material.
- Retention Maps, title metadata, source notes and narration counts are useful only when they match the exact script revision.

## Problems to address in the new framework

1. No single handoff currently connects an idea, source dossier, fact ledger, concept decision, architecture, script, review, revision, verification and production package.
2. The existing `StoryAnalysis` fields are dramatic-fiction centric (protagonist/objective/opposition); documentary/explainer paths need questions, evidence, competing explanations, chronology, mechanisms and uncertainty as first-class options.
3. Source lists are not enough to verify a script. Each factual sentence/claim needs a stable claim ID, source locator, source type, scope, confidence/qualification, and a recorded verification state.
4. Creative critique, fact verification, deterministic checks and human approval need distinct roles and outputs. A writer cannot count its own critique as independent review.
5. Deterministic checks are valuable for counts, IDs, source links, headings, maps, revision references and status consistency, but cannot decide whether a story is moving, true, fair or complete.
6. The current score-oriented review schema/checklist conflicts with the repository's no-score critique contract and no-average guidance. Do not integrate scores or modify protected schemas without an approved CR.
7. Runtime counts and pace assumptions can become stale during revision. Recalculate them from the exact narrated text; keep verbal narration, visual-only holds and any measured duration separate.
8. Companion artifacts can drift after edits (e.g. headings, map rows, source-note “to be recalculated” text). A revision must trigger targeted regeneration/reconciliation of affected metadata.

## Capability classification at audit time

- **Implemented and tested in repository:** staged story analysis/hooks/outline/cards/screenplay/retention pipeline under CR_006; provider provenance; context/revision gates; selected deterministic screenplay checks; provider-backed creative critique path and mock path labels.
- **Implemented but limited:** episode briefs, context assembly, current schema checks, runtime-by-card estimate, creative review contracts.
- **Manual/documentation only:** general documentary source research, claim-to-source dossier, concept comparison, factual verification, rights review, independent second review, audience-performance learning.
- **Unsupported:** automatic claim verification, citation locator checking across arbitrary sources, audience retention prediction, measured playback absent recording/animatic, and approval by an agent.

## Audit conclusion

Reuse context/version lineage, stage gates, provider provenance, evidence-led findings and explicit statuses. Add an isolated documentary/explainer workflow around those pieces. Do not turn the ten-script sample into fixed hooks, lengths, act counts, beat intervals, scores, or a claimed retention formula. Any changes to existing agents, shared schemas, CORE/MODES or global workflow remain governed and are outside this initial module proposal.
