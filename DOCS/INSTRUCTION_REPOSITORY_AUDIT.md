---
prompt_id: DOCS_INSTRUCTION_REPOSITORY_AUDIT
version: 1.1.0
modified_date: 2026-11-09
description: Evidence-based inventory, consistency findings, and validation results for the instruction repository
dependencies: ["CORE_SYSTEM_CONSTITUTION", "DOCS_CAPABILITY_REGISTRY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Inventory implementation and instruction surfaces under approved CR_001
  - version: 1.1.0
    date: 2026-11-09
    summary: Extend the governed instruction inventory for CR_003 genre, channel-style, tool and library architecture
---
# Instruction Repository Audit

## Scope and method

This audit records the initial implementation and instruction inventory and
the documentation delivered under approved `CR_001`. Source inspection was
limited to repository files; generated `.venv/`, `frontend/node_modules/`,
build output, and database runtime state are not instruction source.

The initial repository contained 70 Markdown documents in the application
directories, 11 JSON schemas, 35 JSON files overall, and a SQLite database
with 38 tables, including the internal `_lock_probe` table. Some Markdown
files are project deliverables and user-facing guides, not governed
instructions. The validator targets only the instruction corpus listed below,
rather than imposing prompt front matter on every project script or unrelated
developer document.

## Application implementation inventory

### Public local API

`backend/main.py` declares four authenticated-by-token HTTP routes:

- `GET /api/health` - architecture and database integrity summary.
- `GET /api/dashboard` - project, approval, asset, toolchain, integration,
  decision, and QC records.
- `POST /api/projects` - create a project at `USER_STORY_IDEA`.
- `POST /api/approvals/decide` - submit a human decision through the approval
  engine.

The API does **not** expose endpoints for all 17 policy workflow stages.
Project stage is a persisted string; the route list does not implement a
general stage-transition API. The approval route accepts a `HUMAN_`-prefixed
reviewer string but does not establish a trusted logged-in identity. The
development token also has a fixed fallback. These are implementation
limitations, not assurances supplied by the instruction documents.

### Registered operations and backend modules

The MCP gateway registers 17 named built-ins and implements permission checks
for calls against registered external-server records. The current call path
returns an acknowledgement echoing arguments rather than dispatching a real
operation. The built-ins are therefore catalog entries, not verified
end-to-end handlers. Exact IDs and caveats are listed in
[CAPABILITY_REGISTRY.md](./CAPABILITY_REGISTRY.md).

Backend modules include governance and approval engines, an agent executor,
screenplay and production pipelines, R&D, provider accounting, technical QC,
ComfyUI workflow validation/provenance recording, Blender/Unreal script
validation and package generation, plugin lifecycle records, and a StoryQuest
JSON outbox. Internal Python methods are not automatically HTTP routes or
registered MCP capabilities.

Observed gaps that instruction authors must not overstate:

- Provider invocation/accounting code does not invoke a live LLM service; the
  credential vault is in-memory.
- ComfyUI validation and output recording do not constitute a verified
  generation-server dispatch; health checks can be simulated by a caller.
- The MCP operation path and health check do not prove external tool execution
  or network reachability.
- QC records fixed outcomes for configured checks rather than inspecting all
  rendered media.
- A Blender/Unreal AST safety check does not prove that the external
  application executed successfully.
- StoryQuest writes an event outbox; this is not evidence of remote delivery.
- A `HUMAN_` identifier prefix is not identity authentication.
- A fixed 16-GB VRAM baseline in R&D is not a measurement of the current
  workstation.

### Persistent data and schemas

The database contains 37 application tables and the internal `_lock_probe`
table (38 total): `_lock_probe`, `agent_executions`,
`agent_prompts`, `agents`, `application_settings`, `approvals`,
`architecture_versions`, `asset_references`, `asset_revisions`, `assets`,
`audio_assets`, `audit_events`, `change_requests`, `characters`,
`cost_records`, `creative_decisions`, `dependencies`, `environments`,
`episodes`, `execution_logs`, `generation_jobs`, `integrations`, `mcp_servers`,
`operating_modes`, `plugin_records`, `projects`, `provider_usage`,
`qc_reports`, `research_reports`, `scenes`, `schema_migrations`, `scripts`,
`series`, `shots`, `tasks`, `tool_candidates`, `tool_evaluations`, and
`toolchain_profiles`.

The database uses text status columns without per-column `CHECK` constraints.
The authoritative structured enums are therefore in the schemas and
application transition logic, not the SQLite column declarations.

The 11 schemas are `AGENT`, `APPROVAL`, `ASSET`, `AUDIO`, `PROJECT`,
`RESEARCH_REPORT`, `SCENE`, `SHOT`, `TASK`, `TOOL`, and `TOOLCHAIN`.
Notable vocabulary relationships verified by the validator:

- `APPROVAL.state` has the seven creative lifecycle states.
- `ASSET.approval_status` uses those states plus `ARCHIVED`.
- `TASK.status` uses those states plus `BLOCKED`.
- `AGENT.outputs[].approval_status` is a deliberately narrower lowercase
  summary vocabulary (`pending`, review, approved, revision, rejected); it is
  not a direct copy of the complete approval state machine.
- `AGENT.status`, tool-candidate lifecycle, and research decision status each
  have distinct enums and meanings.

Two storage representations are not one-to-one schema mirrors: audio is
represented by per-line `audio_assets` rows while `AUDIO.schema.json` describes
a package; asset metadata is split between `assets` and `asset_revisions`
while `ASSET.schema.json` describes a combined registry record. These
differences are documented rather than silently changing the API contract.
No schema change was needed for this instruction-authoring request.

## Existing repository inventory

Before CR_001, the repository had:

- 9 `CORE/` policies and 8 operating modes.
- 16 agent instruction files plus the production director instruction.
- 8 department rule files.
- 17 existing developer/user/integration documents in `DOCS/`.
- 6 provider profiles.
- 5 project Markdown deliverables.
- 11 structured schemas.

The directory structure also includes the React/Vite frontend, Tauri shell,
test suite, integration adapters, plugin manifests, project assets, and local
SQLite data. Refer to the repository tree and implementation code for the
full non-instruction source layout.

## Specifications reconciled

1. **Policy versus enforcement:** The 17-stage workflow remains the policy
   target, but documentation now states that the current HTTP surface does not
   implement every stage transition.
2. **Capability names versus handlers:** Registry descriptions are separated
   from verified execution. Registered MCP names are not described as working
   handlers.
3. **Approval versus identity:** Creative approval remains human-only, while
   the current `HUMAN_` prefix check is explicitly distinguished from
   authentication.
4. **Status vocabulary:** The validator checks specific schema mappings and
   keeps task, approval, asset, operation, and research states distinct.
5. **Architecture rollback:** The built-in architecture snapshot captures
   Markdown in `CORE/` and `MODES/` only; it is not a full-repository backup.
   Files outside that scope require separate copies and hashes before a
   future change.
6. **Toolchain research and approval:** Research evidence, tests, cost and
   license uncertainty, and human toolchain approval are separate steps.
   Documentation does not substitute for authorization.
7. **Templates versus capabilities:** Reusable templates are documents only;
   they do not create API routes, database persistence, or application
   validators.

## Delivered under CR_001

- **42 Markdown files created:** 2 core policies, the capability registry,
  10 tool-intelligence guides, 10 integration instructions, 18 reusable
  templates, and this audit.
- **57 existing Markdown files updated:** 9 core policies, 8 modes, 17 agent
  instructions, 8 department procedures, 6 provider profiles, 4 integration
  guides, 2 agent/R&D guides, 2 developer/install guides, and 1 build/test
  report.
- **Schemas created or updated: 0.** Existing schema differences were
  inspected and documented; none required changing for this documentation
  scope.
- **Validation rules:** 8 rule groups covering YAML/front-matter metadata and
  unique IDs; dependency resolution and cycles; local Markdown links;
  source-to-document operation IDs; schema status vocabulary; agent
  permission/approval/output requirements; mode and department completeness;
  and complete audit inventory.
- **Automated tests:** 9 focused tests in
  `TESTS/test_instruction_repository.py`.
- **Executable validator:** `scripts/validate_instruction_repository.py`.

The validator covers the governed instruction corpus below and compares the
capability registry with source decorators/catalog entries. It does not run
production, prove external integrations, or replace human semantic review.

## Three review passes

### Pass 1 - completeness

Check that every required core policy, mode, agent, department, tool-intelligence
guide, integration instruction, and template exists and has front matter or
the applicable template metadata. The validator's inventory check also
requires every governed Markdown file to be listed in this audit.

### Pass 2 - consistency

Check unique IDs, dependency references/cycles, local links, operation IDs,
status mappings, mode/agent approval boundaries, and source-to-document
registry parity. Document implementation gaps rather than hiding them.

### Pass 3 - operational usability

Check that agent and department procedures identify inputs, outputs, steps,
approval boundaries, and failure handling; that tool research separates
discovery, research, tests, recommendations, and human approval; and that
integrations and templates distinguish available implementation from planned
work.

## Validation results

Three review passes are complete:

1. **Completeness:** all 96 governed documents have parseable front matter,
   unique prompt IDs, resolved dependencies, and audit-inventory entries;
   required agent, mode, and department sections are present.
2. **Consistency:** dependency graph is acyclic; local links, operation IDs,
   source registry parity, status mappings, and agent approval/output
   boundaries validate without findings.
3. **Operational usability:** each mode includes activation/context, allowed
   and forbidden work, permission limits, procedure, approval, output,
   memory, conflict, failure, and success guidance. Department instructions
   include inputs, workflow, outputs, dependencies, gates, exceptions, and
   handoff. A targeted scan found no TODO/FIXME/TBD/placeholder markers in
   governed non-template instructions.

Final command results:

- `.\.venv\Scripts\python.exe scripts\validate_instruction_repository.py` -
  **96 files, 8 rule groups, 0 findings**.
- `.\.venv\Scripts\python.exe -m pytest -q TESTS\test_instruction_repository.py TESTS\test_animation_forge_suite.py` -
  **24 passed** (9 instruction-repository tests and 15 application tests).
- `.\.venv\Scripts\python.exe -m py_compile scripts\validate_instruction_repository.py TESTS\test_instruction_repository.py` -
  **passed**.

## Remaining planned capabilities and unresolved requirements

- Real MCP handler dispatch and endpoint-backed connection health checks.
- Provider API invocation, secure persistent credential storage, and verified
  current provider profiles/limits.
- Real ComfyUI generation dispatch and hardware profiling.
- Media-derived QC for rendered video/audio rather than predetermined check
  results.
- Trusted reviewer identity authentication for human approval routes.
- Verified remote StoryQuest delivery and actual external application
  execution where required.
- Schemas for database entities and document types that currently have no
  structured schema.
- A full-repository architecture snapshot/rollback mechanism. Current built-in
  snapshots omit schemas, agents, departments, providers, docs, and code.
- The exact application enforcement path for every policy workflow stage.

These are clearly labeled limitations or planned work in the operational
guidance. No runtime capability was added by this documentation change.

## Governed instruction inventory

Every path below is included in validator coverage:

### Core

- `CORE/ASSET_VERSIONING.md`
- `CORE/CHANGE_CONTROL.md`
- `CORE/ERROR_HANDLING.md`
- `CORE/GLOBAL_WORKFLOW.md`
- `CORE/HUMAN_APPROVAL_POLICY.md`
- `CORE/MEMORY_POLICY.md`
- `CORE/OUTPUT_CONTRACTS.md`
- `CORE/RULE_HIERARCHY.md`
- `CORE/SECURITY_POLICY.md`
- `CORE/SYSTEM_CONSTITUTION.md`
- `CORE/TOOL_SELECTION_POLICY.md`

### Modes

- `MODES/ARCHITECTURE_MODE.md`
- `MODES/CREATIVE_MODE.md`
- `MODES/EXPERIMENT_MODE.md`
- `MODES/MAINTENANCE_MODE.md`
- `MODES/PRODUCTION_MODE.md`
- `MODES/REVIEW_MODE.md`
- `MODES/SCRIPTWRITING_MODE.md`
- `MODES/TOOL_RND_MODE.md`

### Agents

- `AGENTS/ANIMATION_ENGINEER/INSTRUCTION.md`
- `AGENTS/AUDIO_DIRECTOR/INSTRUCTION.md`
- `AGENTS/CAMERA_DIRECTOR/INSTRUCTION.md`
- `AGENTS/CHARACTER_ARCHITECT/INSTRUCTION.md`
- `AGENTS/CHARACTER_DESIGNER/INSTRUCTION.md`
- `AGENTS/ENVIRONMENT_DESIGNER/INSTRUCTION.md`
- `AGENTS/PREVIS_DIRECTOR/INSTRUCTION.md`
- `AGENTS/QUALITY_CONTROLLER/INSTRUCTION.md`
- `AGENTS/RESEARCH_ANALYST/INSTRUCTION.md`
- `AGENTS/SCREENWRITER/INSTRUCTION.md`
- `AGENTS/SCRIPT_BREAKDOWN/INSTRUCTION.md`
- `AGENTS/SCRIPT_CRITIC/INSTRUCTION.md`
- `AGENTS/STORYBOARD_DIRECTOR/INSTRUCTION.md`
- `AGENTS/STORY_ARCHITECT/INSTRUCTION.md`
- `AGENTS/VIDEO_EDITOR/INSTRUCTION.md`
- `AGENTS/WORLD_ARCHITECT/INSTRUCTION.md`
- `ORCHESTRATION/PRODUCTION_DIRECTOR/INSTRUCTION.md`

### Departments

- `DEPARTMENTS/ANIMATION/DEPARTMENT_RULES.md`
- `DEPARTMENTS/AUDIO/DEPARTMENT_RULES.md`
- `DEPARTMENTS/CHARACTERS/DEPARTMENT_RULES.md`
- `DEPARTMENTS/ENVIRONMENTS/DEPARTMENT_RULES.md`
- `DEPARTMENTS/POST_PRODUCTION/DEPARTMENT_RULES.md`
- `DEPARTMENTS/PREVIS/DEPARTMENT_RULES.md`
- `DEPARTMENTS/STORY/DEPARTMENT_RULES.md`
- `DEPARTMENTS/STORYBOARD/DEPARTMENT_RULES.md`

### Research, integrations, and templates

- `DOCS/BUILD_AND_TEST_REPORT.md` (historical build report, updated with current audit reference)
- `DOCS/CAPABILITY_REGISTRY.md`
- `DOCS/AGENT_GUIDE.md`
- `DOCS/INSTRUCTION_REPOSITORY_AUDIT.md`
- `DOCS/TOOL_RND_GUIDE.md`
- `DOCS/BLENDER_INTEGRATION_GUIDE.md`
- `DOCS/COMFYUI_INTEGRATION_GUIDE.md`
- `DOCS/MCP_INTEGRATION_GUIDE.md`
- `DOCS/UNREAL_INTEGRATION_GUIDE.md`
- `DOCS/TOOL_INTELLIGENCE/ONLINE_RESEARCH_RULES.md`
- `DOCS/TOOL_INTELLIGENCE/REQUIREMENT_ANALYSIS.md`
- `DOCS/TOOL_INTELLIGENCE/TOOL_DISCOVERY.md`
- `DOCS/TOOL_INTELLIGENCE/TOOL_EVALUATION.md`
- `DOCS/TOOL_INTELLIGENCE/COST_ANALYSIS.md`
- `DOCS/TOOL_INTELLIGENCE/LICENSING_CHECK.md`
- `DOCS/TOOL_INTELLIGENCE/HARDWARE_COMPATIBILITY.md`
- `DOCS/TOOL_INTELLIGENCE/TOOLCHAIN_APPROVAL.md`
- `DOCS/TOOL_INTELLIGENCE/POC_PLANNER.md`
- `DOCS/TOOL_INTELLIGENCE/CROSS_PROJECT_RESEARCH_MEMORY.md`
- `DOCS/INTEGRATIONS/COMFYUI.md`
- `DOCS/INTEGRATIONS/BLENDER.md`
- `DOCS/INTEGRATIONS/UNREAL.md`
- `DOCS/INTEGRATIONS/MCP_GATEWAY.md`
- `DOCS/INTEGRATIONS/CUSTOM_MCP.md`
- `DOCS/INTEGRATIONS/CUSTOM_PLUGINS.md`
- `DOCS/INTEGRATIONS/TTS_INTEGRATIONS.md`
- `DOCS/INTEGRATIONS/IMAGE_GENERATION.md`
- `DOCS/INTEGRATIONS/VIDEO_GENERATION.md`
- `DOCS/INTEGRATIONS/EDITING_TOOLS.md`
- `DOCS/TEMPLATES/PROJECT_BRIEF.md`
- `DOCS/TEMPLATES/STORY_BIBLE.md`
- `DOCS/TEMPLATES/SCREENPLAY.md`
- `DOCS/TEMPLATES/CHARACTER_BIBLE.md`
- `DOCS/TEMPLATES/ENVIRONMENT_BIBLE.md`
- `DOCS/TEMPLATES/AUDIO_SCRIPT.md`
- `DOCS/TEMPLATES/VOICE_PROFILE.md`
- `DOCS/TEMPLATES/STORYBOARD.md`
- `DOCS/TEMPLATES/SHOT_LIST.md`
- `DOCS/TEMPLATES/ANIMATION_SPECIFICATION.md`
- `DOCS/TEMPLATES/TOOL_RND_REPORT.md`
- `DOCS/TEMPLATES/TOOL_COMPARISON.md`
- `DOCS/TEMPLATES/TOOLCHAIN_PROFILE.md`
- `DOCS/TEMPLATES/POC_REPORT.md`
- `DOCS/TEMPLATES/ASSET_MANIFEST.md`
- `DOCS/TEMPLATES/PRODUCTION_REPORT.md`
- `DOCS/TEMPLATES/QC_REPORT.md`
- `DOCS/TEMPLATES/CHANGE_REQUEST.md`

### Provider profiles

- `PROVIDERS/AUDIO/SFX_MUSIC_PROFILE.md`
- `PROVIDERS/IMAGE/COMFYUI_FLUX_SDXL_PROFILE.md`
- `PROVIDERS/LLM/DEFAULT_LLM_PROFILE.md`
- `PROVIDERS/TTS/ELEVENLABS_PROFILE.md`
- `PROVIDERS/TTS/LOCAL_KOKORO_XTTS_PROFILE.md`
- `PROVIDERS/VIDEO/COMFYUI_WAN_LTX_PROFILE.md`

 
## CR_003 governed instruction inventory

The following files extend the governed corpus. The genre and channel registries are intentionally separate. The style registry is empty until a real channel identity has been defined.

### Change and screenplay context
- `DOCS/CHANGE_REQUESTS/CR_003_GENRE_STYLE_TOOL_LIBRARY.md`
- `DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md`

### Genre profiles
- `GENRES/README.md`
- `GENRES/TEMPLATES/GENRE_INSTRUCTION_TEMPLATE.md`
- `GENRES/FANTASY/INSTRUCTION.md`
- `GENRES/COMEDY/INSTRUCTION.md`

### Channel style profiles
- `STYLES/README.md`
- `STYLES/TEMPLATES/CHANNEL_STYLE_GUIDE_TEMPLATE.md`

### Tool manuals
- `TOOLS/README.md`
- `TOOLS/TEMPLATES/TOOL_MANUAL_TEMPLATE.md`
- `TOOLS/BLENDER/TOOL.md`
- `TOOLS/UNREAL_ENGINE/TOOL.md`
- `TOOLS/COMFYUI/TOOL.md`

### Asset library
- `LIBRARY/README.md`

### CR_003 validation scope

- The instruction validator includes the new Markdown folders and the screenplay context contract.
- JSON Schema contracts cover genre registry, channel-style registry, tool profile/catalogue, asset index, storage-root configuration and screenplay context manifest.
- Registry validation checks file references, genre/style profile IDs and versions, tool manual IDs, task-to-tool and task-to-provider mappings, ProviderManager registration, duplicate IDs, asset storage-root references, tag vocabulary and evidence requirements for claimed tool availability.
- Tool availability remains `NOT_VERIFIED` until a real local check is recorded. Integration maturity is separately marked `SIMULATION_ONLY` for the current Blender, Unreal and ComfyUI adapters.
- The new genre and style project fields are optional in the project schema for backward compatibility. Database migrations, UI selectors, runtime context assembly and local storage-root configuration have not been implemented by CR_003.
