---
prompt_id: CORE_ASSET_VERSIONING
version: 1.0.0
modified_date: 2026-11-09
description: Non-destructive asset revision and provenance tracking policy
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Asset versioning rules
---
# ASSET VERSIONING POLICY

1. Every asset is registered with a stable `asset_id` and monotonically increasing `revision` (starting at `1`).
2. Approved revisions are copied/locked under `PROJECTS/<ID>/APPROVED/` with SHA-256 integrity hashes.
3. New generations create `revision = N + 1` in `DRAFTS/` without modifying prior revisions.
4. Full generation provenance (workflow JSON, model IDs, seed, prompt, references, cost) is stored per revision.
