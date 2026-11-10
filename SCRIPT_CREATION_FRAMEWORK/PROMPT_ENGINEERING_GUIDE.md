# Prompt Engineering Guide

**Status:** Reusable prompt cards are provided in `prompts/`. No prompt runner or model-provider connection is implemented.

## Design rules

- Give each stage one responsibility and clear inputs and outputs.
- Pass relevant brief, version IDs, source excerpts and evidence locators. A title alone is not evidence.
- Keep observed fact, interpretation, uncertainty and creative suggestion distinct.
- Ask for alternative story routes only when the material supports meaningfully different choices.
- Let evidence and topic determine structure; do not force acts, a twist, fixed hook intervals or a hidden viral score.
- Write plain, spoken English an average 12-year-old can follow while preserving mature topics and conceptual depth.
- Link factual passages to claim IDs. Do not invent sources, quotes, statistics, dates, reviewer feedback or analytics.
- Creative review, fact checking, deterministic checks and human approval are separate tasks.
- A reviewer who authored or revised the script cannot be labelled independent.

## Prompt pack

1. `prompts/01_TOPIC_DISCOVERY.md`
2. `prompts/02_RESEARCH_SYNTHESIS.md`
3. `prompts/03_STORY_ARCHITECTURE.md`
4. `prompts/04_SCRIPT_DRAFTING.md`
5. `prompts/05_INDEPENDENT_CREATIVE_REVIEW.md`
6. `prompts/06_FACT_CHECK.md`
7. `prompts/07_REVISION.md`
8. `prompts/08_HANDOFF_CHECKLIST.md`

Use the original brief and exact version/hash at each stage. Preserve model inputs and outputs if a model is used. Record model/provider details outside the prompt text. A prompt is a reusable instruction, not evidence that a stage ran.

## Failure conditions

Stop or return an explicit gap when source evidence is missing, the output relies on an unsupported fact, a referenced revision is unavailable, a schema fails, reviewer independence is unclear, or a runtime is presented without estimate/measurement status. The human decides the creative route and approval.
