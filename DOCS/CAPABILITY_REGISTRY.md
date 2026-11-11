---
prompt_id: DOCS_CAPABILITY_REGISTRY
version: 1.3.0
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
  - version: 1.2.0
    date: 2026-11-09
    summary: Record CR_006 proposed story-context and screenplay capabilities separately from implemented routes
  - version: 1.3.0
    date: 2026-11-09
    summary: Register CR_006 implemented routes (Story Bible, Episode Brief, staged screenplay, QC, provider) with honest boundaries
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
| `POST /api/approvals/decide` | Submit a decision through the approval engine. | Requires local IPC token plus Windows-derived reviewer identity and native confirmation; unavailable on non-Windows systems. |
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
| `GET /api/visual-development/projects` | List Visual Development project packages with source-script approval status, format, counts and continuity status. | Read-only; requires IPC token; only `PROJECTS/VDEV_*` packages that contain `project.json` are listed. |
| `GET /api/visual-development/{project_id}` | Read one Visual Development project: art-direction candidates, shot breakdown, Style Bible, generation provenance and review events. | Read-only; requires IPC token; 404 for an unknown or non-`VDEV_` id. |
| `GET /api/visual-development/{project_id}/media` | Serve one real generated image or layout file from a Visual Development package. | Read-only; requires IPC token; path is contained inside the project package (traversal escapes rejected). |
| `POST /api/visual-development/{project_id}/decision` | Record a human decision (SELECT / APPROVE / REJECT / REGENERATE) in the module's append-only review event log. | Requires IPC token; the system never selects or approves a style on its own; REGENERATE writes a new image revision and never overwrites an approved image. |
| `GET /api/production/{project_id}/pipeline` | The whole production spine for one Visual Development package: the seven stages in studio order, the script link and its approval state, the shot status rollup, the candidates, the shots with their status and the saved prompt overrides. | Read-only; requires IPC token; 404 for an unknown or non-`VDEV_` id. |
| `GET /api/production/{project_id}/breakdown` | The script breakdown: every scene reduced to its tagged elements, with the taxonomy, the per-scene sheets and the summary. | Read-only; requires IPC token; reports `NOT_RUN` when no breakdown exists. |
| `GET /api/production/{project_id}/animatic` | The animatic timeline and, when it was rendered, the video. | Read-only; requires IPC token; reports `NOT_RUN` when no animatic exists. |
| `GET /api/production/{project_id}/prompts/{target_id}` | The generated prompt for one shot or art-direction candidate, the user's override and the merged result that would be sent to ComfyUI. | Read-only; requires IPC token; 404 for an unknown target. |
| `POST /api/production/{project_id}/generate` | Generate one image for a shot or an art-direction candidate, using the prompt, the settings and the workflow the user saved. | Requires IPC token; the same plan the command line uses, so the picture does not depend on where it was made; a new revision is always written and the previous one is kept. |
| `PUT /api/production/{project_id}/prompts/{target_id}` | Store the user's own prompt, negative prompt, excluded modules, generation settings and optional ComfyUI workflow for one shot or candidate. | Requires IPC token; only the overridable generation settings are accepted, anything else is rejected; the stored override is recorded in the package and reported by the pipeline. |
| `DELETE /api/production/{project_id}/prompts/{target_id}` | Remove the override on one shot or candidate and go back to the generated prompt. | Requires IPC token; reports `NOTHING_TO_RESET` when there was no override. |
| `GET /api/production/presets` | The generation presets a user can choose from, with the model, the size, the sampling and what each one costs on this machine. | Read-only; requires IPC token. |
| `GET /api/production/{project_id}/workflows` | List the ComfyUI API-format workflows stored in the package. | Read-only; requires IPC token. |
| `GET /api/production/{project_id}/script` | The script the package was built from, with its approval status and hash. | Read-only; requires IPC token; the text is the stored source, which is hashed and provenance recorded. |
| `POST /api/production/{project_id}/style-bible/approve` | Approve the current Style Bible. | Requires IPC token; a human decision recorded in the package's own event log, because the Style Bible itself is immutable. |
| `POST /api/production/{project_id}/workflow/validate` | Check a user supplied ComfyUI API-format workflow against the live server: every node class and required input, and whether the graph can take a prompt. | Requires IPC token; validation only, nothing is submitted and nothing is written. |
| `POST /api/production/{project_id}/workflow/import` | Validate a user supplied ComfyUI API-format workflow and store it in the package. | Requires IPC token; nothing is stored unless the server accepts every node class and the graph can take a prompt. |
| `POST /api/change-requests` | Create an architecture change request in ARCHITECTURE_MODE (AWAITING_HUMAN_REVIEW). | Requires IPC token; duplicate ID rejected; approval only via trusted Windows reviewer path. |
| `GET /api/story-bibles/{series_id}` | Read head revision of a Series Bible. | Requires IPC token; 404 if none. |
| `GET /api/story-bibles/{series_id}/revisions` | List Bible revisions with hashes. | Read-only. |
| `POST /api/story-bibles` | Create a Bible revision (DRAFT/PROPOSED only, never directly APPROVED). | Requires IPC token; APPROVED canon requires human-confirmed transition. |
| `POST /api/story-bibles/{bible_revision_id}/transition` | Transition Bible status (DRAFT->IN_REVIEW->APPROVED via Windows dialog). | APPROVED requires native Windows confirmation; AI cannot approve canon. |
| `GET /api/story-bibles/{series_id}/canon` | Return latest APPROVED canon revision or null. | Read-only. |
| `POST /api/projects/{project_id}/episode-briefs/{episode_id}` | Create Episode Brief revision with genre/channel validation. | Requires IPC token; unknown genre/channel IDs rejected. |
| `GET /api/projects/{project_id}/episode-briefs/{episode_id}` | Read latest Episode Brief revision. | Read-only. |
| `GET /api/projects/{project_id}/story-context` | Assemble context manifest (profiles, canon, brief, hashes). | Read-only; validates genre/channel selection. |
| `POST /api/projects/{project_id}/story/analysis` | Generate story analysis via selected provider. | Real provider request; no silent fallback; records provenance. |
| `POST /api/projects/{project_id}/story/hooks` | Generate 3 hook alternatives with payoff linkage. | Requires prior analysis. |
| `POST /api/projects/{project_id}/story/outline` | Generate act/beat outline. | Requires prior analysis. |
| `POST /api/projects/{project_id}/story/outline/approve` | Human-approve outline (Windows dialog required). | Opens native Windows confirmation; fail-closed off Windows. |
| `POST /api/projects/{project_id}/story/scene-cards` | Generate scene cards from outline+brief. | Persists revisions. |
| `POST /api/projects/{project_id}/story/screenplay` | Draft screenplay from approved outline+cards. | Blocked until outline APPROVED; new revision per generation; never overwrites APPROVED. |
| `POST /api/projects/{project_id}/story/retention-map` | Build scene-linked retention map. | No invented statistics. |
| `POST /api/projects/{project_id}/story/qc/validate` | Run deterministic screenplay validation. | Returns checks/issues; never approves creative work. |
| `POST /api/projects/{project_id}/story/qc/critique` | Run SCRIPT_CRITIC creative critique. | Scene-cited findings; never approves creative work. |
| `GET /api/projects/{project_id}/story/artifacts/{artifact_type}` | Read latest artifact of given type. | Read-only. |

## Audience Experience status

The merged AUDIENCE_EXPERIENCE directory contains design documents, templates,
hook patterns and draft JSON contracts. No Audience Experience HTTP routes,
database persistence, frontend panels or agent dispatch have been implemented.
The presence of a JSON contract does not imply that the backend validates or
stores records against it.

The internal screenplay pipeline currently creates a premise-specific scaffold
only. Its production-breakdown method verifies that the script is approved, then
raises NotImplementedError; it does not insert demo scenes into project data.

## CR_006 proposed story and screenplay capabilities (IMPLEMENTED)

The proposal at DOCS/CHANGE_REQUESTS/CR_006_STORY_CONTEXT_SCREENPLAY_QC.md
is APPROVED (ARCH_V1.3.0) and implemented with the routes registered above.
This table records implemented evidence, not a roadmap:

| Proposed capability | Current evidence | Missing implementation |
|---|---|---|
| Versioned Series Bible | The series table has a bible_json field. | Version history, structured validation, canon decisions and API/UI editing. |
| Episode Brief | The episodes table exists; the project schema describes genre/style identifiers. | Episode-level brief persistence and end-to-end genre/style selection through database, API and UI. |
| Screenplay context assembly | A written contract exists in DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md. | Runtime profile/canon loading, validation, hashing and scoped prompt assembly. |
| Staged screenplay generation | story_pipeline.py creates an honest, premise-specific scaffold. | Real provider response handling, outline/scene-card generation, screenplay prose and revision orchestration. |
| Creative script critique | SCRIPT_CRITIC instruction exists. | Independent review execution with scene/line evidence and prioritized findings. |
| Script technical validation | Existing QC method is simulated. | Deterministic validation of the actual screenplay structure, references, continuity facts and runtime estimate. |
| Human screenplay approval | Approval engine and Windows review flow exist with platform limitations. | End-to-end integration with real generated revisions and verified human review. |

The proposal does not add routes or change runtime behavior. Do not infer
implementation from this roadmap or from the presence of existing tables,
instructions or schemas.

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
