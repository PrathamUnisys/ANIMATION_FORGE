---
prompt_id: GENRES_INDEX
version: 1.0.0
modified_date: 2026-11-09
description: Registry and operating rules for reusable genre-specific story and screenplay instructions
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE_RULE_HIERARCHY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Establish genre instruction registry and multi-genre context rules
---
# Genre Instruction Library

## Purpose

`GENRES/` stores reusable creative instructions for narrative genres. Each genre has its own slug folder and an `INSTRUCTION.md` file:

`GENRES/<GENRE_SLUG>/INSTRUCTION.md`

The registered ID includes the `GENRE_` prefix (for example, the `FANTASY` folder is registered as `GENRE_FANTASY`).

Examples included initially: `GENRES/FANTASY/INSTRUCTION.md` and `GENRES/COMEDY/INSTRUCTION.md`.

## Genre selection

Each project selects exactly one **primary genre** and may select zero or more **secondary genres**.

- The primary genre establishes the main narrative contract, audience expectation and story logic.
- Secondary genres add compatible conventions, moods or devices. They must not erase the primary genre's central promise.
- Genre is not channel style. The same fantasy project can be produced for different YouTube channels with different pacing, presentation and branding.
- Do not infer a genre from a title alone. Use the user's selection or ask for the missing decision.
- A hybrid genre is represented as primary + secondary IDs, not as a newly invented combined prompt.

## Required genre instruction structure

Every genre instruction must define its promise, audience expectations, narrative engine, structures, character patterns, conflict, pacing, visual/sensory opportunities, dialogue conventions, common failure modes, production considerations and screenplay review checklist.

Genre instructions are guidance, not rigid formula. Avoid clichés unless the project intentionally adopts or subverts them.

## Versioning and context

Each instruction uses YAML front matter with a stable `prompt_id`, semantic version and change history. A screenplay task records the selected genre IDs and exact versions used. Never silently change the profile version associated with an already approved screenplay.

Use `TEMPLATES/GENRE_INSTRUCTION_TEMPLATE.md` when adding a genre. New genre folders should use uppercase stable IDs and must be added to `REGISTRY.json`.

## Available profiles

| Genre ID | Instruction | Status |
|---|---|---|
| `GENRE_FANTASY` | `FANTASY/INSTRUCTION.md` | Initial profile |
| `GENRE_COMEDY` | `COMEDY/INSTRUCTION.md` | Initial profile |

Only create a profile when it adds reusable conventions. Do not create empty genre folders merely to inflate the list.
