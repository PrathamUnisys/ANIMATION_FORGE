---
prompt_id: GENRES_PROPOSED_PROFILE_ROADMAP
version: 1.0.0
modified_date: 2026-11-09
description: Proposed genre profile roadmap (not active profiles)
dependencies: ["GENRES_INDEX"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial proposed profile roadmap
---
# Proposed Genre Profile Roadmap

**Status:** Research-informed proposal. These profiles are not active and are not registered in `GENRES/REGISTRY.json`.

The initial creative strategy research recommends exploring the following profiles for Animation Forge:

| Proposed genre ID | Role | Intended reusable guidance |
|---|---|---|
| `GENRE_OCCULT_DETECTIVE` | Primary | Investigation engine, clue integrity, supernatural case logic, protagonist method and fair resolution |
| `GENRE_DARK_FOLKLORE` | Supporting | Traditional motifs, folklore variants, cultural/contextual research, atmosphere and careful adaptation |
| `GENRE_PSYCHOLOGICAL_HORROR` | Supporting | Character fear, perception, ambiguity, emotional escalation and psychological conflict |
| `GENRE_COSMIC_HORROR` | Supporting | Unknown forces, existential scale, limits of knowledge and coherent ambiguity |

## Current provisional project combination

- Primary: `GENRE_OCCULT_DETECTIVE`.
- Supporting: `GENRE_DARK_FOLKLORE`, `GENRE_PSYCHOLOGICAL_HORROR`.
- `GENRE_COSMIC_HORROR` is an optional influence, not automatically included in every story.

## Separation rules

- Do not create one combined "Occult Detective + Dark Folklore + Horror" mega-profile.
- The primary genre sets the principal narrative contract.
- Secondary genres contribute compatible conventions without erasing the primary promise.
- Series format and channel style remain independent selections.
- Exact profile content should be reviewed against the research and a pilot before activation.

## Activation checklist

- [ ] Complete the genre research and source audit.
- [ ] Draft each profile using `GENRES/TEMPLATES/GENRE_INSTRUCTION_TEMPLATE.md`.
- [ ] Include narrative engine, structures, character patterns, world/rule conventions, dialogue, visual/audio opportunities, production implications and failure modes.
- [ ] Include genre-specific screenplay review criteria.
- [ ] Check compatibility and conflicts between profiles.
- [ ] Validate front matter and registry references.
- [ ] Run instruction repository validation and tests.
- [ ] Obtain human approval through the change-control process before registering profiles as active.
