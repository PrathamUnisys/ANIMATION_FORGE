---
prompt_id: CORE_ERROR_HANDLING
version: 1.0.0
modified_date: 2026-11-09
description: Failure classification, safe recovery, and truthful status reporting
dependencies: ["CORE/SYSTEM_CONSTITUTION.md", "CORE/SECURITY_POLICY.md", "CORE/OUTPUT_CONTRACTS.md"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Define explicit errors, bounded retries, and recovery reporting
---
# ERROR HANDLING POLICY

## General rules

- Surface failures explicitly. Never silently default, swallow an exception,
  or return success-shaped data when a required operation failed.
- Preserve the original error, relevant identifiers, and successful outputs.
  Redact secrets and minimize unrelated user data in logs and reports.
- Stop before irreversible or externally visible work when required input,
  authorization, connectivity, or a safety check is missing.
- Retry only transient failures, with bounded attempts and a documented
  backoff when available. Do not retry paid or destructive operations without
  renewed authorization.

## Failure classes

1. **Invalid input or contract** - identify the field/schema violation; request
   correction. Do not mutate persisted state.
2. **Missing context or prerequisite** - return blocked with the exact missing
   approval, asset, stage, or capability.
3. **Policy/permission denial** - stop the call; explain the permission
   required. Never evade the denial through another provider or tool.
4. **Provider/network failure** - report endpoint/provider, request ID when
   available, whether the request may have incurred cost, and safe retry
   conditions. Do not expose credentials.
5. **Generation or technical validation failure** - retain logs and draft
   artifacts as appropriate; distinguish technical validation from creative
   review.
6. **Persistence or filesystem failure** - verify whether any partial output
   was written. Preserve prior files and report exact verified paths.
7. **Governance or state conflict** - do not force a transition; report the
   conflicting record and required human action.
8. **Security incident** - follow `CORE/SECURITY_POLICY.md`, stop the
   affected operation, protect evidence, and report without repeating secrets.

## Recovery procedure

1. Stop the affected operation at the narrowest safe boundary.
2. Capture non-sensitive diagnostic context: operation, project, revision,
   timestamp, error category, and last verified state.
3. Check for partial output or side effects before retrying.
4. Identify a non-destructive recovery path and its prerequisites.
5. Obtain additional authorization if cost, network transfer, installation,
   or destructive action is involved.
6. Retry only after correcting the cause; record the outcome and remaining
   uncertainty.

## Reporting

Return `failed` for an attempted operation that errored; use `blocked` when
the operation cannot start because a prerequisite or permission is absent.
Include warnings, completed sub-steps, preserved output paths, and an actionable
next step. Do not claim a rollback, cleanup, notification, or recovery unless
it was executed and verified. Follow the applicable schema in
`CORE/OUTPUT_CONTRACTS.md`.
