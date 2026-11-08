---
prompt_id: DOCS_CAPABILITY_REGISTRY
version: 1.0.0
modified_date: 2026-11-09
description: Evidence-based index of exposed API routes and registered MCP catalog operations
dependencies: ["CORE/OUTPUT_CONTRACTS.md", "CORE/SECURITY_POLICY.md"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Record the current exposed route and MCP operation surface with implementation caveats
---
# Application Capability Registry (Observed)

This document records the current source-code surface, not a promise that every
catalog entry performs its described work. The validator compares the IDs below
with route decorators in `backend/main.py` and the built-in catalog in
`backend/integrations/mcp_gateway.py`.

## HTTP API routes

These are routes declared by FastAPI. All routes depend on the local IPC token
check. The reviewer ID accepted by the approval endpoint is a request field;
the route does not establish a logged-in human identity.

| Operation ID | Declared behavior | Important boundary |
|---|---|---|
| `GET /api/health` | Return integrity and architecture health summary. | Requires local IPC token. |
| `GET /api/dashboard` | Read project and production dashboard records. | Requires local IPC token. |
| `POST /api/projects` | Insert a project at `USER_STORY_IDEA`. | Requires local IPC token; database errors are not translated to a structured validation response. |
| `POST /api/approvals/decide` | Submit a decision through the approval engine. | Requires local IPC token; a `HUMAN_` ID prefix is not, by itself, identity authentication. |

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
