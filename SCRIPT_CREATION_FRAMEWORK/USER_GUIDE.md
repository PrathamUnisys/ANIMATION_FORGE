# User Guide

## Create a project

From the repository root:

```powershell
.\.venv\Scripts\python -m SCRIPT_CREATION_FRAMEWORK.cli init --root .\SCRIPT_PROJECTS --id ocean-cables --title "How the internet crosses the ocean"
```

The module needs Python 3.10+ and `jsonschema>=4.22,<5`. Install its dependency with `.\.venv\Scripts\python -m pip install -r SCRIPT_CREATION_FRAMEWORK\requirements.txt` if it is not already installed.

The command refuses to overwrite an existing project ID. It creates folders and starter templates only; no research, script, or approval is generated.

## Run the creative workflow

1. Fill `brief/brief.md` with the topic, audience, simple-language needs, target duration and production limits.
2. Use `prompts/01_TOPIC_DISCOVERY.md` to identify the central question, story options and research gaps.
3. Find and open sources yourself. Record IDs, URLs, access dates, locators and limitations in `research/sources/sources.json`. Record claims and source IDs in `research/claims/claims.json`. A prompt or ledger cannot prove truth.
4. Use `prompts/02_RESEARCH_SYNTHESIS.md` to map evidence, then `prompts/03_STORY_ARCHITECTURE.md` to choose a structure that fits the material.
5. Draft with `prompts/04_SCRIPT_DRAFTING.md`. Keep spoken words separate from direction tags. Mark factual passages with `<!-- CLAIM:ID -->` and use stable passage IDs where practical.
6. Give the exact script revision to a reviewer who did not write or revise it. Use `prompts/05_INDEPENDENT_CREATIVE_REVIEW.md`. If they are connected to authorship, record self-review or related-review instead.
7. Have a human check each factual claim against the opened sources with `prompts/06_FACT_CHECK.md`. Revise into a new file and record responses using `prompts/07_REVISION.md`.
8. Run the deterministic checks below. A passing check covers only its stated mechanical rule.
9. Human approval is a separate decision. Use `prompts/08_HANDOFF_CHECKLIST.md` only after approval, or label the package a draft and state what gate is missing.

## Preserve an artifact

Each revision goes to a new path:

```powershell
.\.venv\Scripts\python -m SCRIPT_CREATION_FRAMEWORK.cli add-artifact --project .\SCRIPT_PROJECTS\ocean-cables --type SCRIPT --source .\draft.md --path scripts/original/script-v1.md
.\.venv\Scripts\python -m SCRIPT_CREATION_FRAMEWORK.cli validate-manifest --project .\SCRIPT_PROJECTS\ocean-cables
```

The manifest records the artifact hash. Editing a registered file later causes hash validation to fail. Register the corrected revision at a new path; do not overwrite it.

## Checks

```powershell
.\.venv\Scripts\python -m SCRIPT_CREATION_FRAMEWORK.cli parse-json .\SCRIPT_PROJECTS\ocean-cables\research\claims\claims.json
.\.venv\Scripts\python -m SCRIPT_CREATION_FRAMEWORK.cli validate-json-schema --path .\SCRIPT_PROJECTS\ocean-cables\research\claims\claims.json --schema .\SCRIPT_CREATION_FRAMEWORK\schemas\claims.schema.json
.\.venv\Scripts\python -m SCRIPT_CREATION_FRAMEWORK.cli check-claims --script .\draft.md --claims .\SCRIPT_PROJECTS\ocean-cables\research\claims\claims.json --sources .\SCRIPT_PROJECTS\ocean-cables\research\sources\sources.json
.\.venv\Scripts\python -m SCRIPT_CREATION_FRAMEWORK.cli count .\draft.md --rate-wpm 120 --holds-min 0 --holds-max 30
.\.venv\Scripts\python -m SCRIPT_CREATION_FRAMEWORK.cli check-map --script .\draft.md --map .\retention_map.json
```

Parsing and schema validation are distinct. The schema command uses the supplied schema and Python `jsonschema` Draft 2020-12 validator. Claim checks compare explicit markers and ledger/source IDs; they do not find unmarked claims or establish truth. Map checks compare ordered timestamp labels; they do not establish that the times are accurate. Runtime output is always `SCRIPT_ESTIMATE` until narration/animatic/final playback is measured.

## Status and limitations

The manifest tracks artifact status but does not enforce the complete creative lifecycle or human approvals. Research collection, model invocation, independent review scheduling, rights clearance and handoff assembly remain human-operated. See [Known Limitations](KNOWN_LIMITATIONS.md).
