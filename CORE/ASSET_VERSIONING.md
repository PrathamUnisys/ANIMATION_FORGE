---
prompt_id: CORE_ASSET_VERSIONING
version: 1.1.0
modified_date: 2026-11-09
description: Non-destructive asset revision and provenance tracking policy
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Asset versioning rules
  - version: 1.1.0
    date: 2026-11-09
    summary: Clarify revision identity, provenance availability, and approval locks
---
# ASSET VERSIONING POLICY

## Identity and revision

- Assign each logical asset a stable project-scoped `asset_id`. Start its
  revision at 1 and increase monotonically for each materially different
  submission.
- A revision is immutable after approval. Changes produce a new draft revision
  and preserve the approved source and its review history.
- Keep project ID, asset ID, revision, type, status, and file path consistent
  between registry records and manifests.
- Do not call an asset approved because it was generated, registered, or
  passed technical validation.

## Files and provenance

- Save draft outputs as new revision files. Preserve prior source files and
  hashes; do not replace the only available copy.
- Record provenance fields supported by the asset/revision schema, including
  creator, tool/provider/model when known, workflow, prompt, seed, inputs,
  license, and creation time. Use explicit `unknown`/unavailable values only
  where the schema permits them; never fabricate provenance.
- Hash the exact bytes of each retained file. A hash establishes file
  integrity relative to that digest, not authorship or creative approval.
- The schema and database may store the current revision metadata but do not
  necessarily enforce a particular `APPROVED/` folder convention. Follow the
  configured project layout and report unimplemented archival behavior.

## Approval and recovery

Attach approval to the exact asset ID and revision. A human approval for one
revision does not approve later revisions. Keep rejected and superseded
revisions for audit unless retention policy authorizes removal.

Before a migration or bulk operation, take a scoped backup, verify it, and
document restore steps. Never use destructive cleanup to resolve a version
conflict.
