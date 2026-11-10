# Framework Development Guide

**Status:** Isolated MVP implementation exists under this folder; model orchestration and export are not built. See `ARCHITECTURE.md`, `IMPLEMENTATION_PROGRESS.md` and `KNOWN_LIMITATIONS.md`.

## Design origin

The framework responds to an audit of Animation Forge's CR_006 story pipeline, source dossier workflow, creative critique and deterministic QC, plus ten original/revised YouTube scripts and their independent review history. It reuses stage gates, exact-revision provenance and human approval, while addressing the gap between screenplay scaffolding and documented documentary research/claim verification.

## How to change the framework

1. Read `AGENTS.md` and relevant entries in the repository map.
2. Read `CORE/CHANGE_CONTROL.md` before changing protected instructions, schemas, runtime or global workflow.
3. Keep a proposed module change local where possible. State purpose, affected artifacts, compatibility, acceptance criteria, tests and rollback.
4. Update the backlog/progress documents and user-facing docs alongside behavior.
5. Run focused checks and the root prescribed tests/validator; report each result honestly.
6. Review the exact diff and ensure tests did not alter the original experiment or unrelated project files.

## Maintenance principles

- Preserve immutable script and review revisions.
- Do not claim live research, fact checking, schema validation, independent critique, runtime measurement or approval without execution evidence.
- Add tools only for repeated, deterministic work; keep creative judgment with writer/reviewer/human.
- Treat external platform guidance as date-sensitive; record source and review date.
- Update `KNOWN_LIMITATIONS.md` when behavior or integrations change.
- Any change to shared protected files requires the formal approved process, not a local proposal.

## Current implementation layout

`workspace.py` creates safe local workspaces and immutable artifact/hash records. `schemas/` holds project, source, claim, review and Retention Map contracts. `runtime.py` counts tagged narration and computes `SCRIPT_ESTIMATE`. `validation.py` performs schema, claim/source and timecode checks. `cli.py` exposes these operations. `prompts/` contains human/model prompt cards. `templates/` contains starter files. `TESTS/test_script_creation_framework.py` exercises deterministic behavior. There is no automated research/provider orchestrator, lifecycle state machine, independent reviewer scheduler or handoff exporter.
