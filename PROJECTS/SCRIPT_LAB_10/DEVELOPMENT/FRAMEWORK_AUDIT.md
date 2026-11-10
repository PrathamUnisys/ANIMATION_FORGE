# SCRIPT_LAB_10 — Framework Audit Baseline

**Audit date:** 2026-11-10  
**Repository ref reviewed:** main  
**Purpose:** Preserve a factual baseline for the proposed Audience Experience and screenwriting-standard work.

## 1. Existing foundation

The repository already contains a substantial Audience Experience design pack:
- 30-pattern hook library.
- Animated episode and YouTube Short templates.
- Audience Plan, Packaging Options, Retention Map, and Creative Review design schemas.
- Retention, analytics, packaging, visual storytelling, audio storytelling, and mystery/horror playbooks.
- Creative review checklist and illustrative Thirteenth Bell example.
- Research synthesis and experiment templates.

The Audience Experience README explicitly labels this package a draft design workspace, not an active runtime feature. It states that no database, API, frontend, production agent, global output contract, or active workflow has been changed by that design pack. Preserve this distinction until implementation is verified.

The existing CR_006 implementation record describes versioned story context, staged screenplay workflow, QC separation, and approval boundaries. It also records limitations, including live Ollama smoke test blocked, production breakdown not implemented, and an empty channel-style registry at the time of that report. Re-verify implementation state before relying on these as current runtime facts.

## 2. Ten-screenplay experiment

The portfolio records ten complete screenplay exports, each targeting approximately 600 seconds, with five scene cards per episode. The scripts remain awaiting human review; none is marked approved.

| Episode | Final screenplay revision | Primary benchmark focus |
|---|---|---|
| EP01 — The Dancing Chimney Code | SCR_SCRIPT_LAB_10_V08 | Visual cipher and deduction |
| EP02 — The Salted Lighthouse Log | SCR_SCRIPT_LAB_10_V03 | Memory, evidence, and reveal causality |
| EP03 — Nine Hours on Redbank Ferry | SCR_SCRIPT_LAB_10_V05 | Living-map story engine and procedural clarity |
| EP04 — The Cartographer of Small Years | SCR_SCRIPT_LAB_10_V07 | Emotional storytelling and visual metaphor |
| EP05 — The River's Two Friends | SCR_SCRIPT_LAB_10_V09 | Folklore adaptation and moral conflict |
| EP06 — The Confession Booth at All Saints | SCR_SCRIPT_LAB_10_V10 | Locked-room mechanics and supernatural evidence |
| EP07 — The Echo Census | SCR_SCRIPT_LAB_10_V11 | Mystery, information sequencing, and motivation |
| EP08 — The Tenant Above | SCR_SCRIPT_LAB_10_V12 | Psychological reveal and clue chronology |
| EP09 — The Seventh Bell of Kestrel Hollow | SCR_SCRIPT_LAB_10_V13 | Fantasy rule consistency and payoff |
| EP10 — The Ministry of Small Apologies | SCR_SCRIPT_LAB_10_V14 | Satire, escalation, dialogue, and emotional payoff |

These are benchmark candidates, not approved scripts or production-ready assets.

## 3. QC reporting discrepancy to resolve

The QC summary table labels the aggregate deterministic QC field NOT_TESTED for all ten scripts. Its notes separately state that scene structure, placeholders, headings/dialogue patterns, required beats/clues, and scene correspondence checks ran, while canon continuity was not tested because no approved canon existed.

This is an ambiguous aggregate status, not proof that every deterministic check was unrun. Future reporting should expose each check separately and preserve NOT_TESTED for canon continuity where no approved canon is available. Do not retrospectively claim a new validation run based on the historical notes.

The QC summary also distinguishes provider critiques from manual autonomous critiques. Preserve reviewer/method provenance; do not present them as equivalent live-provider executions.

## 4. Runtime baseline

The experiment targets 9:30–10:30 and uses a per-scene estimate based on dialogue words divided by assumed WPM plus estimated action, silence, pauses, and transitions. The method explicitly states that estimates are not measured playback and that animatic timing is the final authority.

Keep planning estimates, animatic measurements, and final-video measurements as distinct evidence levels.

## 5. Proposed creative audit themes

The previous review identified the following hypotheses for deeper benchmark inspection:
- EP02: clarify the causal relationship among the lighthouse lamp, rock light, missed days, and the supposed rescue.
- EP04: seed the short-lived character's urgency earlier so the emotional premise is felt before the late reveal.
- EP05: strengthen the moral conflict and the consequence/resolution of the astrologer's false cure.
- EP06: make the freezing/fatal mechanism physically understandable and fairly established.
- EP07: strengthen the motivation for erasing Amara and the mayor's complicity.
- EP08: clarify sleepwalking/upstairs access and photo chronology.
- EP09: establish the relationship between the bell, water restoration, and blight.
- EP10: make the auditor's discretionary exception credible.
- EP01 and EP03: inspect deduction fairness and the operational explanation of the fare/record mystery.

These are preliminary critique leads, not verified defects. Each must be checked against the exact screenplay revision and cited before a revision is recommended.

## 6. Recommended benchmark set

Use three contrasting episodes for the first controlled comparison:
- EP10: dialogue, satire, escalation, character, and payoff.
- EP07: mystery construction, information sequencing, and motivation.
- EP04: emotional progression, slow pacing, visual metaphor, and restraint.

Freeze originals, record exact revisions/hashes, apply the approved standard only after activation, and compare evidence-backed findings. A revised draft is not automatically better because it contains more audience metadata.

## 7. Audit limits

This document records repository documentation and the prior screenplay review summary. It does not claim a fresh execution of validators, provider calls, test suites, or a full line-by-line re-review of all ten scripts. Re-run relevant checks from the current main commit before implementation acceptance.
