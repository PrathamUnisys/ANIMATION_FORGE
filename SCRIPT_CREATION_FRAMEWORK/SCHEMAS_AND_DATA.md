# Schemas and Data

**Status:** Five module-local Draft 2020-12 JSON Schemas exist. Shared repository schemas were not changed.

## Contracts

| Schema | Purpose | Current boundary |
|---|---|---|
| `schemas/project_manifest.schema.json` | Project identity, stage, approval label, artifact hashes/status and checks | CLI validates manifest and file integrity; it does not enforce lifecycle transitions |
| `schemas/claims.schema.json` | Claim wording, passage refs, source IDs, scope, verification status and uncertainty | Reference audit checks IDs/explicit markers; a human verifies meaning and evidence |
| `schemas/sources.schema.json` | Stable source IDs, title/publisher/URL/type/access date/locator and limitations | Does not fetch URLs or establish source quality |
| `schemas/review.schema.json` | Review identity, revision hash and evidence-based findings | Prompt contract only; CLI does not schedule or verify reviewer independence |
| `schemas/retention_map.schema.json` | Timecodes, passage refs, viewer question, new information and payoff | Map checker compares timed headings, not audience response or timing truth |

The initializer copies Markdown templates and starter JSON for source, claim, review and map data. Source and claim starter files are validated against their schemas when explicitly checked.

## Validation behavior

`parse-json` checks JSON syntax only. `validate-json-schema --path FILE --schema SCHEMA` first parses the data and schema, checks the schema itself, then runs Python `jsonschema` `Draft202012Validator` with format checks. It reports parse and schema outcomes separately. Validation only applies to the specified file and schema.

`check-claims` compares `<!-- CLAIM:ID -->` markers with the claim ledger and, when `--sources` is supplied, checks claim source IDs against the source ledger. `check-map` compares ordered `##` heading timecodes with map entries. Neither check establishes semantic completeness, factual truth or measured audience retention.

Manifest artifact hashes detect post-registration edits. To preserve revisions, add changed content at a new unused path. Manifest status fields are data, not an approval engine.

## Not yet represented as enforced data

Concept selection rationale, full story architecture, revision response matrix, measured runtime, rights/access review, exact reviewer relationship and handoff bundle are captured in Markdown/prompt workflows but do not yet have complete machine-enforced lifecycle contracts. No protected `SCHEMAS/` file was overwritten.
