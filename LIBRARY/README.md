---
prompt_id: LIBRARY_ASSET_INDEX
version: 1.0.0
modified_date: 2026-11-09
description: Asset library index policy for locating, grouping, tagging and tracing animation production files
dependencies: ["CORE_ASSET_VERSIONING", "CORE_SYSTEM_CONSTITUTION", "SCHEMAS/LIBRARY_INDEX.schema.json", "SCHEMAS/STORAGE_ROOTS.schema.json"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Establish searchable metadata index and external storage-root model for assets
---
# Asset Library

## Purpose

`LIBRARY/` manages metadata and locations for project and reusable media. It is an index, not a folder that must contain every large binary file.

The portable index contract lives in `LIBRARY/ASSET_INDEX.json`, validated by `SCHEMAS/LIBRARY_INDEX.schema.json`. In the first runtime implementation, SQLite should be the searchable source of truth; this JSON file should remain a bootstrap/import-export snapshot rather than a giant live catalogue. Copy `STORAGE_ROOTS.example.json` to the ignored local file `STORAGE_ROOTS.json`, configure verified storage URIs, and validate it with `SCHEMAS/STORAGE_ROOTS.schema.json`.

## Logical groups

Use these stable groups:
- `PROJECT_ASSET` — created for one project or episode.
- `SERIES_ASSET` — approved assets reused across episodes in one series.
- `SHARED_LIBRARY` — reusable assets intentionally shared across projects.
- `CHANNEL_BRAND` — logos, fonts, title cards, overlays, sound marks and other channel identity material.
- `REFERENCE` — reference media with source and usage rights recorded.
- `EXPORT` — generated delivery or render outputs.

Each asset also has a media type such as character, environment, prop, texture, model, rig, animation, storyboard, image, audio, video, subtitle, project file or document.

## Location model

Each asset record stores a `storage_root_id` plus a `relative_path` inside that root. The local configuration resolves the root ID to a URI. This keeps records portable when a project moves between machines. Roots may be local folders, network shares or approved object storage. Example logical roots:

- `PROJECTS_ROOT`
- `SHARED_LIBRARY_ROOT`
- `CHANNEL_BRAND_ROOT`
- `RENDER_OUTPUT_ROOT`

Actual machine paths must be registered in local configuration and verified. Do not commit user-specific absolute paths. Never infer a location from an asset name.

## Tags and search

Every controlled tag uses the canonical `dimension:value` form. Allowed dimension values are defined in `LIBRARY/TAG_TAXONOMY.json`; project, series and channel identifiers use their stable IDs. Optional freeform tags must use a clearly namespaced `custom:` prefix. Suggested dimensions:

- `type:character`, `type:environment`, `type:prop`, `type:audio`
- `project:PROJECT_ID`, `series:SERIES_ID`, `channel:STYLE_ID`
- `style:dark_fantasy`, `mood:ominous`, `palette:amber`
- `use:thumbnail`, `use:background`, `use:turnaround`, `use:voice`
- `status:draft`, `status:approved`, `status:archived`
- `licence:commercial_ok`, `licence:review_required`

Tags are descriptive metadata, not permission. Search results must still check project association, approval state, licence, revision and compatibility.

## Asset record minimum

Every indexed asset requires a stable ID, display name, media type, group, storage-root ID, relative path, project/series/channel association where relevant, revision, approval state, tags, licence summary and provenance. Optional technical metadata can hold dimensions, duration, frame rate, codec, sample rate and color space. Relationships can link derived assets, variants, dependencies and references. For generated files capture the creating tool/model/version, workflow/prompt reference, seed where applicable and SHA-256 hash.

## Interoperability direction

Use stable asset references and resolvable locations so a future adapter can bridge the library to DCC tools. OpenAssetIO is useful as an interoperability boundary between a host application and an asset-management system; it is not itself the asset database or storage manager. OpenTimelineIO is useful for editorial timing and track interchange; it references external media instead of embedding the media files. Do not implement either standard wholesale until a concrete integration requires it.

For embedded image metadata, map useful descriptive, rights and AI-generation provenance fields to established metadata where practical. IPTC Photo Metadata 2025.1 includes AI prompt/system-related properties; do not replace the library's stable IDs and database metadata with free-form tags.

## Current state

The index and storage-root example contain no real machine paths or asset records. The actual local `STORAGE_ROOTS.json` is ignored by Git. Populate it only after the relevant directories have been inspected and the storage roots configured.
