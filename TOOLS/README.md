---
prompt_id: TOOLS_INDEX
version: 1.0.0
modified_date: 2026-11-09
description: Index and operating standard for tool manuals, local connection profiles and task-based capability discovery
dependencies: ["CORE_TOOL_SELECTION_POLICY", "CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Establish per-tool manuals and a separate task-tagged tool catalogue
---
# Tool Operations Library

## Purpose and layout

`TOOLS/` is the operational knowledge base for desktop applications, local servers and execution tools used in production. Hosted LLM and TTS provider profiles remain under `PROVIDERS/` to avoid duplicating API/model configuration. The task catalogue may reference provider capability groups later, but provider credentials and model settings belong in `PROVIDERS/`.

- `TOOLS/<TOOL_ID>/TOOL.md` — how to locate, install, connect, configure, use, validate and debug one tool.
- `TOOLS/CATALOG.json` — machine-readable tools grouped by production task and searchable capability tags.
- `TOOLS/TEMPLATES/TOOL_MANUAL_TEMPLATE.md` — standard manual for adding another tool.

Initial manuals:
- `BLENDER/TOOL.md`
- `UNREAL_ENGINE/TOOL.md`
- `COMFYUI/TOOL.md`

## Manual requirements

Every manual must record supported operating systems, official documentation, executable/application discovery, expected install locations, version detection, launch method, connection/API details, prerequisites, inputs and outputs, normal workflow, health checks, logs, common failures, recovery steps, known limits and last-verified date.

Never guess a local executable path, installed version, endpoint or credential state. Use `UNKNOWN`, `NOT_INSTALLED`, `UNCONFIGURED` or `NOT_VERIFIED` until the current machine is checked. Keep machine-specific paths and credentials in local configuration, not committed manuals.

## Task-based catalogue

The catalogue answers: **Which desktop tools and AI providers are candidates for this task, and what evidence do we have about their availability and implementation?** Desktop tools are defined under `tools`; hosted/local model providers are referenced under `providers` and retain their configuration profiles in `PROVIDERS/`.

Select by task group and tags such as `screenplay_generation`, `image_generation`, `character_consistency`, `3d_modeling`, `animation`, `rendering`, `tts`, `video_encoding` and `subtitle_burning`. A task group with no candidate tools explicitly records a capability gap; do not fill it with a fictional or unverified integration.

A provider candidate is not a live provider connection, and a desktop tool candidate is not an available application. Before dispatch, verify:
1. The tool is installed or its service is reachable.
2. The required version and capability are present.
3. Inputs/outputs and hardware requirements are compatible.
4. The task is within the approved project toolchain and its constraints.
5. The invocation method has an actual tested implementation.

Do not equate a catalogue entry, a manual, a health-check placeholder or a sample workflow with successful execution.

## Status vocabulary

- `NOT_VERIFIED`: no current machine check has been recorded.
- `NOT_INSTALLED`: verified absent.
- `INSTALLED`: executable/version verified locally.
- `CONNECTED`: live service/API connection verified.
- `CONFIGURATION_REQUIRED`: user setup or local path is needed.
- `BLOCKED`: a known incompatibility or explicit restriction prevents use.

Keep availability separate from adapter maturity. For example, an installed application may still have only a simulated Animation Forge adapter.

## Related systems

- Tool manuals: this folder.
- Task/capability catalogue: `TOOLS/CATALOG.json`.
- Project-approved toolchain: existing `TOOLCHAIN` records and `SCHEMAS/TOOLCHAIN.schema.json`.
- Asset locations and tags: `LIBRARY/ASSET_INDEX.json`.
