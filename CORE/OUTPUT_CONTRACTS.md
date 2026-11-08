---
prompt_id: CORE_OUTPUT_CONTRACTS
version: 1.1.0
modified_date: 2026-11-09
description: Schema-backed operation, deliverable, and validation output rules
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE/HUMAN_APPROVAL_POLICY.md"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Standardize JSON output envelope
  - version: 1.1.0
    date: 2026-11-09
    summary: Define validation and truthful capability reporting
---
# OUTPUT CONTRACTS

## Selecting a contract

Use the schema for the actual entity being produced: project, task, scene,
shot, asset, audio, approval, tool, toolchain, or research report. The repository
does not define one universal envelope schema for every operation. Use an
operation envelope only where the caller or registered capability requires
one; do not fabricate fields and imply that it is persisted or validated.

## Operation envelope

Where an agent operation uses the documented envelope, include:

- `operation_id`, matching a registered implemented operation or explicitly
  marked proposed capability;
- `project_id` and `agent_id`;
- `status`: `awaiting_review`, `completed_analysis`, `failed`, or `blocked`;
- `outputs`: typed descriptors with stable IDs, file paths, revisions, and
  approval status matching the applicable schema;
- `warnings`: material assumptions, missing inputs, and unresolved risks;
- `validation`: `schema_valid` and `technical_checks_passed`, each based on
  checks actually performed;
- `requires_human_approval`: true for creative deliverables awaiting human
  review.

Do not set a success status when generation, validation, persistence, or a
required gate failed. For a blocked operation, identify the unmet
prerequisite. For a failed operation, state the error and preserved outputs.

## Schema and status discipline

- Validate against the repository's current schema when available. Report the
  schema version/path and validation result.
- Preserve exact field names, types, required properties, and enums. Do not
  use a value from the Task schema in an Asset field unless that Asset schema
  allows it.
- Do not label technical success as creative approval. The approved state
  must arise only from the human decision flow.
- Do not claim that a schema check occurred if no validator ran.
- If the requested output has no schema, state that fact and return a
  self-describing artifact without implying schema conformance.

## Capability and artifact reporting

Use only registered operations. Distinguish implemented, unavailable, and
planned capabilities in both prose and machine-readable output where the
contract supports it. Include output paths relative to the project root and
do not report a file as created until persistence is verified.
