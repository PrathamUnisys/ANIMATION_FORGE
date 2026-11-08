---
prompt_id: CORE_CHANGE_CONTROL
version: 1.1.0
modified_date: 2026-11-09
description: Change Request lifecycle and rollback rules for Architecture Mode
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial Change Control specification
  - version: 1.1.0
    date: 2026-11-09
    summary: Define approval, scope, snapshot limits, and safe rollback procedure
---
# CHANGE CONTROL POLICY

## Scope

Use this process before changing `CORE/`, `MODES/`, `SCHEMAS/`, agent
definitions, or global workflow structures. Architecture Mode permits
requesting and applying approved work; it does not permit self-approval.

## Request fields

Create a structured request with:

- `change_request_id` and `current_architecture_version`;
- precise `requested_modification` and `reason`;
- affected departments and workflows;
- compatibility impact, advantages, and disadvantages;
- testing requirements, rollback plan, and proposed version;
- pending approval state and creation time.

Use the implemented `GovernanceEngine.create_change_request` in
`ARCHITECTURE_MODE`; the current database stores requests in `change_requests`
with `AWAITING_HUMAN_REVIEW`. Do not claim a request is approved until an
authenticated human approves it.

## Approval and application

1. Scope the smallest coherent change and enumerate files that may change.
2. Identify compatibility risks, tests, and an actionable rollback plan.
3. Record the request and present it to a human reviewer.
4. Wait for explicit approval. Do not edit governed files while the request is
   pending or rejected.
5. Apply only the approved file scope, validate it, and record the result.
6. Do not modify application runtime behavior under a documentation-only
   request.

## Snapshot and rollback limitations

The current governance snapshot implementation captures Markdown files in
`CORE/` and `MODES/` only. It does not capture `SCHEMAS/`, `AGENTS/`,
`DEPARTMENTS/`, `DOCS/`, `PROVIDERS/`, or source code. Therefore, before a
change that touches files outside `CORE/` and `MODES/`, preserve a separate,
verifiable copy of every in-scope file and record its location and hashes.
Never describe the built-in snapshot as a full-repository backup.

Rollback must restore only files changed under the approved request, using the
recorded pre-change copies. The governance `rollback_architecture` method
restores its stored `CORE/` and `MODES/` snapshot; it cannot roll back files
outside that snapshot. Verify the restored files and active version after
rollback. Do not overwrite unrelated user changes.

## Failure handling

If approval, version state, snapshot coverage, or the requested scope is
unclear, stop before editing. If validation fails after application, preserve
the evidence, report the failure, and use the approved rollback plan rather
than silently amending unrelated files.
