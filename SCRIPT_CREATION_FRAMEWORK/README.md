# Animation Forge Script Creation Framework

**Status:** Isolated local MVP. Project workspaces, artifact hashes, JSON parsing and Draft 2020-12 schema validation, narration counts, `SCRIPT_ESTIMATE` arithmetic, claim/source ID checks and Retention Map timecode checks are implemented and tested. Automatic research, model orchestration, independent-review execution and production export are not implemented.

## Purpose

Help a creator move from an idea to a researched, narrated YouTube documentary or explainer using a topic-fitting story shape, plain spoken language, traceable claims, separate creative and fact review, and production notes. It does not promise views or retention, verify facts by itself, or approve creative work.

## Quick start

From the repository root with its Python environment:

```powershell
.\.venv\Scripts\python -m SCRIPT_CREATION_FRAMEWORK.cli init --root .\SCRIPT_PROJECTS --id sample-001 --title "A new documentary idea"
.\.venv\Scripts\python -m SCRIPT_CREATION_FRAMEWORK.cli validate-manifest --project .\SCRIPT_PROJECTS\sample-001
.\.venv\Scripts\python -m SCRIPT_CREATION_FRAMEWORK.cli count .\SCRIPT_PROJECTS\sample-001\scripts\original\script_template.md --rate-wpm 120 --holds-min 0 --holds-max 20
```

The initializer copies blank templates and creates a manifest. It does not research or write content. See [User Guide](USER_GUIDE.md) for stage-by-stage use and other CLI checks.

## Workflow

Idea → research dossier and claim ledger → story route → architecture → script → independent creative review + separate fact check → revision → deterministic checks → human decision → handoff.

The workflow adapts to the topic. It does not require a fixed act count, arbitrary hook interval or universal story formula. The writing prompt follows the simple-English rule: an average 12-year-old should understand each sentence, while mature topics and depth remain available.

## What is implemented

- Isolated Python package and command line interface.
- Safe workspace initializer with starter files and a manifest.
- New artifact registration with SHA-256 and no-overwrite path behavior.
- Project, claim, source, review and Retention Map Draft 2020-12 schemas.
- Narration-only word counter and clearly labelled runtime estimate.
- Explicit claim/source ID and script/map timecode checks.
- Reusable prompts for discovery, research synthesis, architecture, drafting, separate review, fact check, revision and handoff.

The prompts are materials for a human/model workflow, not an integrated AI engine. See [Known Limitations](KNOWN_LIMITATIONS.md).

## Documentation

- [Existing script audit](EXISTING_SCRIPT_AUDIT.md)
- [Research report](RESEARCH_REPORT.md)
- [Storytelling methodology](STORYTELLING_METHODOLOGY.md)
- [Framework proposal](FRAMEWORK_PROPOSAL.md)
- [Architecture](ARCHITECTURE.md)
- [User guide](USER_GUIDE.md)
- [Research workflow](RESEARCH_WORKFLOW.md)
- [Editorial review guide](EDITORIAL_REVIEW_GUIDE.md)
- [Prompt engineering guide](PROMPT_ENGINEERING_GUIDE.md)
- [Schemas and data](SCHEMAS_AND_DATA.md)
- [Implementation plan and backlog](IMPLEMENTATION_PLAN.md), [TASK_BACKLOG.md](TASK_BACKLOG.md)
- [Implementation progress](IMPLEMENTATION_PROGRESS.md)
- [Known limitations](KNOWN_LIMITATIONS.md)

## Governance

This module is isolated from protected Animation Forge instructions, schemas, runtime and database structures. Any integration or shared-file change must follow `CORE/CHANGE_CONTROL.md` and receive required approval.
