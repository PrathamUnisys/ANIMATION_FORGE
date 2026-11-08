---
prompt_id: TEMPLATE_DOC_ASSET_MANIFEST
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable project asset inventory, revision, provenance, dependency, and approval template
dependencies: ["SCHEMAS/ASSET.schema.json", "CORE_ASSET_VERSIONING", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable asset manifest template
document_type: reusable_document_template
---
# TEMPLATE — ASSET MANIFEST

> Reusable inventory template, not an executable agent prompt. Include only known records; mark absent files and unknown metadata explicitly. An inventory entry does not imply the asset is approved.

## Manifest record
- **Project ID / manifest revision / owner / updated at**: `[DETAIL]`
- **Source project metadata**: `[PROJECT REFERENCES]`
- **Status key**: `[PROPOSED / GENERATING / QUALITY_CHECK / AWAITING_HUMAN_REVIEW / APPROVED / REVISION_REQUESTED / REJECTED / ARCHIVED]`

## Asset records
| Asset ID | Name / type / description | Project / character / scene refs | File location | Revision | Created at / creation agent | Tool / provider / model / workflow | Approval status | Dependencies / inputs | License |
|---|---|---|---|---:|---|---|---|---|---|
| `[ID]` | `[DETAIL]` | `[IDS]` | `[PATH OR NOT CREATED]` | `[N]` | `[DETAIL]` | `[KNOWN DETAILS OR UNKNOWN]` | `[SCHEMA STATUS]` | `[IDS]` | `[INFO OR UNKNOWN]` |

For machine-readable records use `SCHEMAS/ASSET.schema.json`. Its required fields include `asset_id`, `name`, `type`, `project_id`, `file_location`, `revision`, `created_at`, `creation_agent`, `tool_used`, and `approval_status`. Use the schema's defined approval-state values; do not substitute free-text approval claims.

## Revision and integrity notes
- **Input/reference provenance**: `[SOURCE ASSET IDS, REVISIONS, PROMPT OR WORKFLOW REFERENCES IF AVAILABLE]`
- **Integrity checks and evidence**: `[HASH/FORMAT/OPEN CHECK; RECORD ONLY IF ACTUALLY RUN]`
- **Superseded revisions and retention location**: `[DETAIL]`
- **Missing or unavailable assets**: `[IDS; BLOCKED CONSUMERS]`
- **Human review links / decisions**: `[APPROVAL IDS, REVIEWER, DATE, COMMENTS]`

Keep approved assets immutable. A revision or manifest status is not itself a human approval decision.
