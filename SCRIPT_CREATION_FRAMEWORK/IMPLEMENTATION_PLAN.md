# Implementation Plan

**Status:** M0 and the deterministic/local portion of M1 are implemented; M2 and a full pilot remain. See `TASK_BACKLOG.md` and `IMPLEMENTATION_PROGRESS.md`.
**Design baseline:** `FRAMEWORK_PROPOSAL.md`, `TECHNICAL_DECISIONS.md`, `EXISTING_SCRIPT_AUDIT.md`.  
**Governance:** Keep work isolated under this directory. A Change Request is required before changing protected shared files.

## Milestones

### M0 — Design and operating contracts

Complete repository audit, independent research synthesis, storytelling method, architecture, limitations, source attribution convention, stage/status definitions, file layout, test plan and backlog. Label all unimplemented behavior as planned. **Exit:** design review documents internally consistent; no source files in protected directories changed.

### M1 — Project workspace and data contracts

Implement a local-first project folder initializer, versioned artifact naming, machine-readable manifest and starter brief/source/claim/concept/architecture/script/review templates. Add project settings for audience, format, language, runtime target and production constraints. **Exit:** a new example project can be initialized and its artifact links/statuses can be validated without a database or network.

### M2 — Research and claim workflow

Add source dossier and claim ledger templates/contracts, source IDs, claim-to-passage linking, uncertainty/verification fields, and instructions for manual/web-assisted research. No automated source discovery or fact verification claim. **Exit:** a real sample topic can record sources and claim dispositions; missing/unsupported claims are visible.

### M3 — Story discovery and architecture

Add reusable prompt components for idea analysis, story opportunity, concept alternatives, structure selection and beat architecture. Include documentary/explainer engines and genre-sensitive risk prompts without forcing three acts. **Exit:** a pilot proceeds from brief and research bundle to a selected, human-reviewable architecture; exact user decisions remain separate.

### M4 — Script drafting and production format

Provide narrator-first script format, visual/audio direction conventions, source claim IDs, accessibility guidance, title/thumbnail promise, Retention Map and production notes. Add language/runtime metadata and immutable revision handling in the local workspace. **Exit:** a complete YS10-derived or other existing-topic draft can be stored as a new revision without changing preserved experiment files.

### M5 — Independent editorial and factual review

Add separate critic and fact-check prompt contracts, exact-revision review manifests, evidence-led findings and finding response log. Define external reviewer execution boundary; never label self-review independent. **Exit:** review output is linked to exact hash and review provenance is explicit; if a genuinely separate reviewer is unavailable, status says so.

### M6 — Deterministic checks and runtime reconciliation

Implement parser/checks for Markdown/JSON syntax, optional actual JSON Schema validation using a selected Draft 2020-12 validator, narration counts, runtime arithmetic, revision IDs, source claim refs, headings/map links and stale metadata. Record each check individually. **Exit:** checks run against exact pilot revision; parse and schema checks are reported separately; failures are preserved honestly.

### M7 — End-to-end pilot, docs and governance assessment

Run a real topic through intake, research, concept, architecture, draft, independent review if available, fact check, revision, QC and production handoff. Record interventions, limitations and comparison to the prior scripts. Run prescribed repository tests and instruction validator; inspect diff/status. Draft a CR only if integration into protected files is actually warranted. **Exit:** capability statuses distinguish implemented/tested, limited, planned and unsupported. No creative approval is implied.

## Architecture decisions to validate during build

- Default to a simple filesystem workspace and a small Python command-line utility only where it removes repeated deterministic work.
- Keep structured data in JSON/Markdown; do not add DB tables or a frontend for a manual-first pilot.
- Reuse existing `backend` endpoints only through a documented adapter if they cover the required use case; do not assume they provide source research or general documentary drafting.
- Use prompt templates for model-assisted creative stages, but require explicit source material and preserve generated artifacts. Any provider call must be real, attributable and failure-visible.
- Do not create an automatic numerical “quality” or retention predictor.

## Verification and change discipline

Per task, run only the checks relevant to the exact artifact and report statuses as PASS, FAIL, NOT_EXECUTED, NOT_AVAILABLE, NOT_TESTED or NOT_APPLICABLE. For JSON, parsing and schema validation are separate. For Markdown scripts, recount actual narration blocks and reconcile timestamps and claim IDs. Tests must not write over original/revised YS experiment files. After every repository change update root `AGENTS.md` per its mandatory rule, run its §5 commands, inspect any known test-run noise and restore only verified noise, then review `git diff` and `git status`.
