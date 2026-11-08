---
prompt_id: DOCS_CHANGE_REQUEST_003
version: 1.0.0
modified_date: 2026-11-09
description: Architecture change record for genre-specific writing, channel style guides, tool knowledge, asset library indexing, and task-based tool discovery
dependencies: ["CORE_CHANGE_CONTROL", "CORE_SYSTEM_CONSTITUTION", "CORE_GLOBAL_WORKFLOW"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Define separated genre, channel style, tool, asset library, and capability catalogue architecture
---
# CR_003 — Genre, Channel Style, Tool and Asset Library Architecture

## Decision and scope

**Status:** APPROVED FOR DOCUMENTATION AND DATA-CONTRACT IMPLEMENTATION  
**Authorization:** Explicit user instruction in the current architecture task  
**Repository branch:** `feature/genre-channel-tool-library-architecture`

This change establishes five independent knowledge domains:

1. `GENRES/` — reusable genre-specific story and screenplay instructions.
2. `STYLES/` — one independently versioned creative/channel guide per YouTube channel or publishing brand.
3. `TOOLS/` — tool-specific setup, connection, usage, configuration, troubleshooting and debugging manuals.
4. `LIBRARY/` — searchable metadata index for project, series, channel and reusable assets. Binary media remains in configured storage locations, not Git.
5. `TOOLS/CATALOG.json` — structured catalogue of tools grouped by production task and searchable tags.

The screenplay context assembler must load the selected primary genre, selected secondary genres, and selected channel style guide. Genre and channel style are separate inputs and must never be collapsed into one free-text genre field.

## Required project context

A project should carry:

- `primary_genre_id`: exactly one selected primary genre.
- `secondary_genre_ids`: zero or more complementary genres.
- `channel_style_id`: selected channel guide; optional for channel-neutral/internal work.
- Existing title, premise, audience, runtime, language, tone and creative constraints.

The existing human-readable `genre` field remains for display and backward compatibility. Stable IDs and profile versions are the machine references.

## Precedence and context assembly

Apply governing constitution, project restrictions and approved canon first. Then load:

1. Primary genre instructions.
2. Secondary genre instructions, without allowing them to contradict the primary genre's core contract.
3. The selected channel style guide, for audience promise, pacing, tone, presentation, recurring format and packaging.
4. Department and screenwriter instructions.
5. Task-specific user direction.

A channel style guide may shape presentation but cannot rewrite story canon or silently replace genre rules. Explicit project direction wins over a profile default. Record profile IDs and versions in each screenplay generation record.

## Tool and capability model

- A tool manual describes how a specific tool is installed, located, connected, configured, used and debugged.
- The tool catalogue describes which task tags and capability tags each tool may support.
- The asset library describes where approved, draft and reference media live, plus their metadata and tags.
- A catalogue entry is not proof that software is installed, connected, licensed or executable. Those states require local verification.
- Credentials and machine-specific paths must not be committed in manuals or catalogue data.

## Asset library model

Use logical groups such as project assets, series assets, reusable library assets, channel-brand assets, references and exports. Every indexed item should have a stable asset ID, type, group, tags, location URI, project/series/channel association where applicable, revision, approval state, licence and provenance.

Do not copy all media into the repository. Store storage-root IDs and root-relative paths plus metadata; the actual files remain in configured storage roots. For the eventual runtime, use SQLite as the queryable source of truth and keep JSON as a portable bootstrap/import-export representation.

## Implementation boundary

This change adds architecture documentation, initial genre instructions, templates, catalogue/index files and JSON data contracts. It does **not** yet implement database migrations, API endpoints, runtime profile loading, AI prompt assembly, local tool discovery, asset scanning, ComfyUI dispatch, or production generation. Those are implementation tasks for the first working screenplay pipeline and subsequent production milestones.

## Acceptance criteria

- Genre and channel style are separately selectable and versioned.
- A screenplay task can identify the exact genre/style profile versions it used.
- Genre instructions are reusable across channels; channel style guides are reusable across genres.
- Tool manuals have consistent setup, connection, usage and debugging sections.
- Tool catalogue entries are grouped by task and searchable by tags, with unverified states explicit.
- Asset index records metadata and file locations without requiring binary assets in Git.
- JSON contracts validate the catalogue and asset index.
- Documentation validator includes the new governed folders and reports no missing inventory entries.
- No existing project database is rewritten by this documentation-only change.

## Out of scope

- Runtime implementation of LLM calls or screenplay generation.
- Runtime installation/discovery of Blender, Unreal Engine, ComfyUI or other tools.
- Asset file migration or bulk scanning.
- Changing the current SQLite database or live project records.
- Marking any tool as installed, connected or production-ready without local verification.
