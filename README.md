# Animation Forge

**An AI-assisted production workspace for developing and producing animated stories, from the first premise to a reviewed delivery package.**

Animation Forge combines a human-led production workflow, specialised AI-agent instructions, project and story governance, tool/provider catalogues, asset metadata, and a desktop application built with Python, React, TypeScript, and Tauri.

> **Important status note:** This repository contains both working application code and a larger target architecture. A documented agent, tool, provider, workflow stage, API operation, or schema does not automatically mean that its end-to-end runtime implementation exists. Check the implementation-status notes below and `DOCS/CAPABILITY_REGISTRY.md` before claiming that an operation is executable.

---

## Start here: instructions for AI coding agents

**Fast context:** read **`AGENTS.md`** first. It is the maintained AI context map (current state, reality matrix, known failures, update rule). Do not load the entire repository into context by default.

This README is the repository map. Read the small set of governing documents first, then follow the task-specific route.

### Recommended reading order

1. **This README** — understand the architecture and find the right files.
2. **`CORE/SYSTEM_CONSTITUTION.md`** — understand the project's governing principles.
3. **`CORE/RULE_HIERARCHY.md`** — understand instruction precedence and conflict handling.
4. **`CORE/HUMAN_APPROVAL_POLICY.md`** and **`CORE/OUTPUT_CONTRACTS.md`** — understand approval boundaries and output contracts.
5. **`DOCS/CAPABILITY_REGISTRY.md`** — check which HTTP routes and MCP operations are actually exposed, and read their caveats.
6. **`DOCS/INSTRUCTION_REPOSITORY_AUDIT.md`** — understand known implementation gaps and the instruction inventory.
7. **`DOCS/DEVELOPER_GUIDE.md`** — use the local development, testing, and packaging guidance.
8. Read only the relevant agent, department, provider, tool, schema, and backend files for the task at hand.

If a task changes a governed instruction or architecture rule, inspect the applicable change-request and approval process before editing it. The developer guide describes the repository's current procedure.

### Task routing: where an AI agent should go

| Task | Start with | Then inspect |
|---|---|---|
| Understand the whole application | `DOCS/DEVELOPER_GUIDE.md`, `DOCS/INSTRUCTION_REPOSITORY_AUDIT.md` | `backend/main.py`, `frontend/src/App.tsx`, `src-tauri/` |
| Change global rules or workflow | `CORE/RULE_HIERARCHY.md`, relevant `CORE/*.md` | `CORE/GLOBAL_WORKFLOW.md`, schemas, validator and tests |
| Develop a story or premise | `AGENTS/STORY_ARCHITECT/INSTRUCTION.md` | `GENRES/REGISTRY.json`, selected genre instructions, project brief and Story Bible |
| Write or revise a screenplay | `AGENTS/SCREENWRITER/INSTRUCTION.md` | `DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md`, selected genre/style profiles, `backend/departments/story_pipeline.py` |
| Break a script into production work | `AGENTS/SCRIPT_BREAKDOWN/INSTRUCTION.md` | scene/shot/task schemas, production workflow and tool catalogue |
| Add or change a genre | `GENRES/README.md` | `GENRES/REGISTRY.json`, `GENRES/TEMPLATES/`, `SCHEMAS/GENRE_REGISTRY.schema.json` |
| Add or change a YouTube channel style | `STYLES/README.md` | `STYLES/CHANNELS.json`, `STYLES/TEMPLATES/`, `SCHEMAS/CHANNEL_STYLE_REGISTRY.schema.json` |
| Find or add a production tool | `TOOLS/README.md` | `TOOLS/CATALOG.json`, the tool's `TOOL.md`, relevant provider profiles and adapter code |
| Find or add an asset | `LIBRARY/README.md` | `LIBRARY/ASSET_INDEX.json`, `LIBRARY/TAG_TAXONOMY.json`, storage-root configuration and asset schemas |
| Change an LLM, image, or TTS provider | `PROVIDERS/` | `backend/providers/manager.py`, the relevant integration/production module, tests and current provider documentation |
| Add or change an API route | `backend/main.py` | `DOCS/CAPABILITY_REGISTRY.md`, API tests and relevant schemas |
| Change database behaviour | `backend/database.py` | database schema/migration code, models, API consumers and tests |
| Change the desktop UI | `frontend/src/` | `frontend/package.json`, Tauri IPC commands and backend API contracts |
| Change desktop lifecycle or packaging | `src-tauri/` | `DOCS/INSTALLATION.md`, `DOCS/BUILD_AND_TEST_REPORT.md` |
| Validate instruction documents | `scripts/validate_instruction_repository.py` | `TESTS/test_instruction_repository.py` |
| Validate application behaviour | `TESTS/` | implementation and `DOCS/CAPABILITY_REGISTRY.md` |

---

## What the system is designed to do

Animation Forge is intended to help a person manage a repeatable animation-production process:

1. Capture a story idea and project constraints.
2. Analyse and refine the premise.
3. Develop a screenplay using selected genre and channel-style guidance.
4. Submit creative work for human review.
5. Break approved scripts into production requirements and tasks.
6. Research and compare tools, then obtain approval for a toolchain.
7. Create and manage character, environment, audio, and other assets.
8. Build storyboards, previs, and animatics.
9. Produce animation and rendered media.
10. Edit, mix, subtitle, and package the result.
11. Run technical quality checks.
12. Obtain final human approval and assemble the delivery package.

The intended 17-stage policy sequence is defined in **`CORE/GLOBAL_WORKFLOW.md`**. That document is the workflow specification, not proof that every stage has an executable API or automatic state transition.

### Human approval is part of the workflow

Agents can research, analyse, draft, review, and recommend. They cannot turn their own proposal into approved story canon or approve their own creative deliverables. Technical QC and creative approval are separate decisions. See `CORE/HUMAN_APPROVAL_POLICY.md`.

---

## Core architecture concepts

### 1. Genre and channel style are separate

Do not combine these into one field or one prompt:

- **Genre** controls narrative conventions: story logic, conflict, character patterns, tone expectations, pacing, and visual storytelling.
- **Channel style** controls the publishing identity: audience, channel promise, format, runtime, presentation, humour density, visual/audio identity, titles, thumbnails, and calls to action.

A project selects one primary genre, optional secondary genres, and an optional channel style. The same story can be presented in different channel styles without silently changing its genre or approved canon.

Current registered genres:
- `GENRE_FANTASY` — `GENRES/FANTASY/INSTRUCTION.md`
- `GENRE_COMEDY` — `GENRES/COMEDY/INSTRUCTION.md`

The channel registry at `STYLES/CHANNELS.json` is intentionally empty until actual channel requirements are supplied. Use the template in `STYLES/TEMPLATES/` when adding one; do not invent a channel identity.

The intended runtime context-loading contract is **`DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md`**. It specifies profile selection, precedence, version/hash provenance, and focused screenplay review. The runtime assembler is not yet implemented.

### 2. Agents are instruction contracts, not automatically executable workers

Agent role instructions live in `AGENTS/`; production orchestration instructions live in `ORCHESTRATION/`. The guide at `DOCS/AGENT_GUIDE.md` describes the agent roster, dispatch process, context, hand-offs, and boundaries.

An instruction file explains how a role should work. It does not prove that an API route, dispatcher, or autonomous agent implementation exists. Verify the caller and implementation before describing a role as executable.

### 3. Tools are discovered by production task

`TOOLS/CATALOG.json` groups candidate tools and providers by task and capability tags. Examples include screenplay development, image generation, character/environment assets, storyboards, 3D modelling, animation, rendering, video generation, TTS, and editing/delivery.

Current desktop-tool manuals:
- Blender — `TOOLS/BLENDER/TOOL.md`
- Unreal Engine — `TOOLS/UNREAL_ENGINE/TOOL.md`
- ComfyUI — `TOOLS/COMFYUI/TOOL.md`

Provider configuration and metadata belong in `PROVIDERS/`, not duplicated in desktop-tool manuals. A catalogue entry means **candidate**, not installed, connected, approved, or successfully integrated. Check both availability and adapter maturity.

### 4. The asset library is an index, not a media dump

`LIBRARY/ASSET_INDEX.json` describes assets and their metadata. Actual media files are intended to live in configured storage roots outside Git.

The index supports stable asset IDs, media types, logical groups, project/series/channel association, root-relative locations, tags, revision and approval state, licence/source information, technical metadata, hashes, provenance, and relationships.

Use:
- `LIBRARY/TAG_TAXONOMY.json` for controlled tags.
- `LIBRARY/STORAGE_ROOTS.example.json` as the local storage configuration template.
- `LIBRARY/README.md` for indexing and location rules.

Copy the example to the ignored local file `LIBRARY/STORAGE_ROOTS.json` and set only paths that have actually been checked on the current machine. Never commit personal absolute paths or credentials.

---

## Repository map

| Path | What belongs here |
|---|---|
| `CORE/` | Global constitution, rule hierarchy, approval policy, output contracts, workflow policy, and other cross-project rules. |
| `MODES/` | Operating modes that constrain how work is performed. |
| `AGENTS/` | Role-specific instructions for specialised creative and production agents. |
| `DEPARTMENTS/` | Department-level instructions and production responsibilities. |
| `ORCHESTRATION/` | Production Director and coordination instructions. |
| `GENRES/` | Versioned narrative genre profiles, registry, and templates. |
| `STORY_ACQUISITION/` | Source dossiers, rights assessments and story-concept research workflow templates. No automatic legal clearance. |
| `AUDIENCE_EXPERIENCE/` | Draft audience promise, hooks, screenplay formats, Retention Map contracts, review checklists, packaging and analytics playbooks. Not yet a runtime feature. |
| `STYLES/` | Independent channel-style profiles, registry, and templates. |
| `TOOLS/` | Desktop-tool manuals, task catalogue, capability tags, and templates. |
| `PROVIDERS/` | LLM, image/video, and TTS provider profiles and configuration guidance. |
| `LIBRARY/` | Asset metadata index, tag taxonomy, storage-root example, and library rules. |
| `SCHEMAS/` | JSON Schemas for projects, agents, assets, approvals, tools, registries, and other data contracts. |
| `backend/` | Python application: API, database, governance, orchestration, providers, integrations, departments, R&D, and QC. |
| `frontend/` | React + TypeScript + Tailwind + Vite user interface. |
| `src-tauri/` | Rust/Tauri 2 desktop shell, sidecar lifecycle, IPC, and desktop configuration. |
| `TESTS/` | Backend/application tests and instruction-repository validation tests. |
| `scripts/` | Validation and development/build helper scripts. |
| `DOCS/` | Developer/installation guides, capability registry, audits, build evidence, and architecture contracts. |

### Important documents

| Document | Why it matters |
|---|---|
| `CORE/GLOBAL_WORKFLOW.md` | The intended production-stage sequence and human gates. |
| `CORE/RULE_HIERARCHY.md` | Which instruction wins when rules conflict. |
| `DOCS/AGENT_GUIDE.md` | Agent roster, dispatch and hand-off rules. |
| `DOCS/CAPABILITY_REGISTRY.md` | Observed API routes and registered MCP operations with caveats. |
| `DOCS/INSTRUCTION_REPOSITORY_AUDIT.md` | Evidence-based inventory and known gaps. |
| `DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md` | Target design for genre/style-aware screenplay context. |
| `DOCS/DEVELOPER_GUIDE.md` | Code layout, local development, validation and packaging notes. |
| `DOCS/INSTALLATION.md` | Local setup, run and test commands. |
| `DOCS/BUILD_AND_TEST_REPORT.md` | Build/test evidence and known packaging blockers. |

---

## Application stack and local development

### Main technologies

- **Backend:** Python, FastAPI, Pydantic, SQLite, JSON Schema.
- **Frontend:** React, TypeScript, Tailwind CSS, Vite.
- **Desktop:** Tauri 2 with a Rust host and a bundled Python backend sidecar.
- **AI/production integrations:** provider profiles and adapters for planned LLM, TTS, ComfyUI, Blender, and Unreal Engine workflows.

### Prerequisites

For the documented Windows development path:
- Windows 10/11, 64-bit.
- Python 3.11 or newer.
- Node.js 18 or newer and npm 9 or newer.
- Rust/Cargo only when building the Tauri desktop application.
- WiX and/or NSIS only when creating the optional MSI/NSIS installers.

### Setup

Run from the repository root in PowerShell:

```powershell
# Backend environment
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt

# Frontend dependencies and production build
cd frontend
npm install --no-audit --no-fund
npm run build
cd ..
```

### Tests and validation

```powershell
# Main application tests
.\.venv\Scripts\python -m pytest -q TESTS/test_animation_forge_suite.py

# Instruction repository tests
.\.venv\Scripts\python -m pytest -q TESTS/test_instruction_repository.py

# Validate governed instruction documents and references
.\.venv\Scripts\python scripts\validate_instruction_repository.py
```

Do not report tests as passing unless they were actually executed in the current environment. For the full desktop/backend run commands and packaging caveats, follow `DOCS/INSTALLATION.md` and `DOCS/BUILD_AND_TEST_REPORT.md`.

---

## Current implementation status and known gaps

The following distinctions are important when planning work or reporting progress:

| Area | Current state |
|---|---|
| Global workflow | The 17-stage production journey is documented as policy. Not every stage has an executable route or automatic transition. |
| Genre profiles | Fantasy and Comedy profiles are registered. |
| Channel styles | Registry exists but is empty; no channel profile has been supplied yet. |
| Screenplay context assembly | A detailed contract exists; the runtime assembler is not implemented. |
| Screenplay workflow | `StoryAndScreenplayPipeline` currently creates a premise-specific human-editable scaffold only. It does not call a live LLM, draft scene prose, complete the 13 passes or assign creative scores. |
| Production breakdown | Unavailable. The former fixed throne-room demo has been disabled; no scenes are created until a real approved-script-to-scene breakdown is implemented. |
| LLM providers | Provider metadata exists, but `ProviderManager` does not make a live LLM request. Simulated estimates are not persisted as actual token usage or cost. The credential vault is an in-memory test stub. |
| TTS | Provider metadata exists. The inspected production path creates a simple tone WAV rather than live provider speech. |
| ComfyUI | Workflow/profile validation and provenance-related code exist. Do not assume that the adapter submits a real job to a running ComfyUI server and retrieves its output. |
| Blender / Unreal Engine | Tool manuals and adapter-side validation exist. Do not assume the adapter launches the applications, executes a scene, or renders media. |
| Tool catalogue | Task groups and candidate tool/provider mappings exist. Local availability and live integration must be verified separately. |
| Asset library | Metadata schema and empty index exist. No actual asset catalogue or machine-specific storage-root configuration is supplied by the repository. |
| HTTP API | The observed route surface is documented in `DOCS/CAPABILITY_REGISTRY.md`. Do not infer additional API routes from agent instructions or internal Python methods. |
| MCP operations | Registered names are not proof of real dispatch. Read the capability registry before using or documenting an operation. |
| Project selectors | Genre and channel-style fields exist in the project schema. Full database persistence and UI selection remain separate implementation work. |
| Audience Experience | Research-derived documents and draft contracts are present under `AUDIENCE_EXPERIENCE/`. There is no runtime persistence, API, UI or agent integration yet. |
| Desktop packaging | Local build work is documented, but packaged runtime-resource layout still needs verification. |

This table is a navigation aid, not a substitute for checking the current source. When changing implementation, update the relevant audit, capability registry, tests, and status documentation so they do not drift apart.

---

## Working rules for AI contributors

1. **Inspect before editing.** Read the current implementation, schemas, tests, and relevant instructions. Do not assume a previous design document matches the present code.
2. **Keep changes focused.** Change the smallest set of files that solves the requested task. Avoid broad rewrites of the backend, database, or frontend without a concrete migration plan.
3. **Respect instruction precedence.** Apply `CORE/RULE_HIERARCHY.md`; lower-level task text cannot silently override global rules or approved project decisions.
4. **Keep genre and channel style independent.** Do not collapse them into one profile or one project field.
5. **Use registered IDs and schemas.** Avoid inventing IDs, status values, API routes, tool capabilities, or provider behaviour.
6. **Separate intended behaviour from implemented behaviour.** Use explicit labels such as planned, candidate, simulated, not verified, implemented, and tested.
7. **Preserve provenance.** For generated creative work and assets, retain source revisions, selected profile versions, tool/model details, prompt/workflow references, and hashes where the schema supports them. Never place credentials in provenance.
8. **Preserve human review.** Agents may create proposals and draft revisions; do not mark creative work approved or overwrite approved revisions.
9. **Add or update tests.** Cover the behaviour changed, run the relevant tests, and report the exact commands and outcomes.
10. **Keep documentation in sync.** When a route, registered operation, schema, instruction, or integration changes, update its registry/audit and tests in the same change.
11. **Do not fabricate verification.** A manual, catalogue entry, mocked response, static validation, or successful build is not proof of a live external integration.
12. **Report blockers plainly.** State what was inspected, what ran, what passed, what failed, and what remains unverified.

For changes to governed rules or agent instructions, follow the current change-request procedure in `DOCS/DEVELOPER_GUIDE.md` rather than bypassing governance.

---

## Contribution and change workflow

Before making a substantial change:

1. Identify the user-visible outcome and the smallest affected subsystem.
2. Trace the path from UI/API entry point to backend service, persistence, schema, and tests.
3. Check whether the requested behaviour is already implemented, partially implemented, or only specified in documentation.
4. Write or update the implementation and tests together.
5. Run focused tests first, then broader checks where practical.
6. Update documentation and capability/audit records.
7. Summarise changed files, validation evidence, limitations, and follow-on work.

Do not merge architectural or creative changes solely because they compile. A successful build is not a creative review, an integration test, or a production approval.

---

## Project status

Animation Forge is an evolving project. The repository intentionally keeps its long-term production architecture visible while documenting which parts are not yet connected end to end. The next meaningful engineering step after the architecture foundation is to implement and test one real screenplay-generation path: load the selected project, genre and channel-style context; call a real configured provider; validate the response; and persist a traceable draft revision.

Build one complete, verifiable path before expanding the catalogue of planned capabilities.
