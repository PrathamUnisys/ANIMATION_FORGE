---
prompt_id: DOCS_CAPABILITY_REGISTRY
version: 1.1.0
modified_date: 2026-11-09
description: Evidence-based index of exposed API routes and registered MCP catalog operations
dependencies: ["CORE/OUTPUT_CONTRACTS.md", "CORE/SECURITY_POLICY.md"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Record the current exposed route and MCP operation surface with implementation caveats
  - version: 1.1.0
    date: 2026-11-09
    summary: Register CR_004 project workspace read routes (steps, detail views, sandboxed file reader) with implementation caveats
---
# Application Capability Registry (Observed)

This document records the current source-code surface, not a promise that every
catalog entry performs its described work. The validator compares the IDs below
with route decorators in `backend/main.py` and the built-in catalog in
`backend/integrations/mcp_gateway.py`.

## HTTP API routes

These are routes declared by FastAPI. All routes depend on the local IPC token
check. The approval route does not accept a caller-supplied reviewer ID. It
derives the signed-in Windows account through windows_reviewer.py and requires
a native Windows confirmation for each decision. Approval therefore fails
closed when that Windows mechanism is unavailable. This is not password or
MFA re-authentication and is not available through this route on other
operating systems.

| Operation ID | Declared behavior | Important boundary |
|---|---|---|
| `GET /api/health` | Return integrity and architecture health summary. | Requires local IPC token. |
| `GET /api/dashboard` | Read project and production dashboard records. | Requires local IPC token. |
| `POST /api/projects` | Insert a project at `USER_STORY_IDEA`. | Requires local IPC token; database errors are not translated to a structured validation response. |
| `POST /api/approvals/decide` | Submit a decision through the approval engine. | Requires local IPC token; a `HUMAN_` ID prefix is not, by itself, identity authentication. |
| `GET /api/projects` | List projects for the project selector. | Read-only; requires local IPC token. |
| `GET /api/projects/{project_id}` | Read one project record. | Read-only; 404 for unknown project. |
| `GET /api/projects/{project_id}/steps` | Aggregate the 17 workflow stages with progress/capability/evidence status derived from records and files. | Read-only; derivation never backfills DONE from `current_stage`; unavailable stages are labelled, not simulated. |
| `GET /api/projects/{project_id}/scripts` | List screenplay revisions (metadata, scores, passes) for a project. | Read-only; does not include full screenplay text. |
| `GET /api/projects/{project_id}/scripts/{script_id}` | Read one screenplay revision with DB text and on-disk file text, flagging disagreement. | Read-only; DB/file mismatch is reported as INCONSISTENT, never silently resolved. |
| `GET /api/projects/{project_id}/audio` | List dialogue audio lines with TTS payload and file references. | Read-only; WAV files are tone demos, not provider speech; model comes only from the recorded TTS payload. |
| `GET /api/projects/{project_id}/assets` | List assets with their revisions, provenance and workflow metadata. | Read-only; prompt/seed/SHA-256 are shown only where recorded in `asset_revisions`. |
| `GET /api/projects/{project_id}/scenes` | List scenes for a project. | Read-only. |
| `GET /api/projects/{project_id}/shots` | List shots with camera, placement and storyboard references. | Read-only. |
| `GET /api/projects/{project_id}/research` | Return research reports, tool candidates, evaluations and toolchain profiles. | Read-only; research data is preconfigured, not a live web search. |
| `GET /api/projects/{project_id}/tasks` | List production tasks with dependencies and generation jobs. | Read-only; tasks record no selected tool or outputs — those fields are explicitly null with a note. |
| `GET /api/projects/{project_id}/qc` | List QC reports with checks, issues and recommendations. | Read-only; checks are predetermined, no media inspection; technical QC is not creative approval. |
| `GET /api/projects/{project_id}/executions` | Return redacted agent executions, prompt metadata/hashes, and execution logs. | Read-only; server-side redaction; `agent_prompts` has no prompt bodies to return. |
| `GET /api/projects/{project_id}/files` | List servable project files under `PROJECTS/{project_id}/`. | Read-only; extension allowlist only. |
| `GET /api/projects/{project_id}/file` | Serve one project file (text, image or audio) by root-relative path. | Read-only; path is resolved and contained inside the project directory (traversal/symlink escapes rejected); size-capped. |

## Audience Experience status

The merged AUDIENCE_EXPERIENCE directory contains design documents, templates,
hook patterns and draft JSON contracts. No Audience Experience HTTP routes,
database persistence, frontend panels or agent dispatch have been implemented.
The presence of a JSON contract does not imply that the backend validates or
stores records against it.

## MCP built-in catalog

These identifiers are registered in the gateway's in-memory `exposed_server_tools`
catalog. Registration is not equivalent to an implemented handler. The current
`execute_mcp_tool` path for database-registered external servers checks
connection/permission flags and returns an acknowledgement echoing arguments;
it does not dispatch the named operation to a real tool. Treat these IDs as
catalogued interfaces, not as evidence of working end-to-end operations.

### Project

- `forge.project.get_info`
- `forge.project.get_approved_screenplay`
- `forge.project.get_character_info`
- `forge.project.get_asset_registry`
- `forge.project.get_production_status`

### Creative

- `forge.creative.submit_script_revision`
- `forge.creative.submit_character_proposal`
- `forge.creative.generate_scene_breakdown`
- `forge.creative.create_storyboard_spec`

### Production

- `forge.production.submit_generation_job`
- `forge.production.get_job_status`
- `forge.production.get_approved_workflow`
- `forge.production.register_output_asset`
- `forge.production.submit_for_review`

### Review

- `forge.review.get_status`
- `forge.review.submit_revision_request`
- `forge.review.get_approval_history`

## Implemented internal workflows are not gateway operations

Python components such as the screenplay pipeline, production studios,
technical QC, ComfyUI adapter, and Blender/Unreal adapter expose methods to
other backend code. Do not describe those methods as an HTTP route or an
executable MCP operation unless a dispatch path is added and verified.
Likewise, an agent role or Markdown instruction is not an application
capability.

## Authorization and maintenance

Use the implementation and tests as the authority for actual behavior.
Permission tiers and human approval requirements remain in force regardless of
catalog description. Update this document and its validator tests in the same
approved change whenever a route or catalog entry changes. Planned operations
must be listed separately and must not be presented as callable.
