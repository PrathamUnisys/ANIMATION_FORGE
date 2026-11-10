# Audience Experience Schema Alignment Proposal

**Status:** DRAFT DESIGN. No schema, database, API, or runtime behavior is changed by this document.

## 1. Why alignment is needed

The repository currently contains overlapping schema locations:
- Runtime-facing contracts in SCHEMAS/, including RETENTION_MAP.schema.json and CREATIVE_REVIEW.schema.json.
- Audience Experience design contracts in AUDIENCE_EXPERIENCE/SCHEMAS/, including Audience Plan, Packaging Options, Retention Map, and Creative Review.

The contracts are not identical. Replacing one with the other without a compatibility review could break existing backend validation, QC, persistence, or tests.

## 2. Observed differences

| Contract | Existing runtime-facing location | Audience Experience design location | Alignment issue |
|---|---|---|---|
| Retention Map | SCHEMAS/RETENTION_MAP.schema.json | AUDIENCE_EXPERIENCE/SCHEMAS/RETENTION_MAP.schema.json | Runtime contract is a compact entries structure; Audience Experience contract is revision-scoped beats with timing basis, viewer state, and review status. |
| Creative Review | SCHEMAS/CREATIVE_REVIEW.schema.json | AUDIENCE_EXPERIENCE/SCHEMAS/CREATIVE_REVIEW.schema.json | Runtime contract requires evidence-backed findings; Audience Experience design contract adds dimensions, critical checks, optional scores, and decision fields. |
| Audience Plan | No equivalent confirmed in the inspected runtime schema set | AUDIENCE_EXPERIENCE/SCHEMAS/AUDIENCE_PLAN.schema.json | Persistence and API ownership are not established by the design file alone. |
| Packaging Options | No equivalent confirmed in the inspected runtime schema set | AUDIENCE_EXPERIENCE/SCHEMAS/PACKAGING_OPTIONS.schema.json | Persistence, selection, and relationship to the audience promise require design. |

## 3. Proposed source-of-truth rule

Until a reviewed change request is approved:
- Treat SCHEMAS/ contracts as the existing runtime-facing contracts where current code/tests use them.
- Treat AUDIENCE_EXPERIENCE/SCHEMAS/ as design proposals unless a verified implementation explicitly consumes them.
- Do not edit either schema family as part of this proposal.
- Do not assume similarly named schemas are interchangeable.

## 4. Design decisions required in CR_007

1. Select one canonical contract location for each persisted entity.
2. Define whether audience contracts extend existing runtime contracts or are separate linked records.
3. Define stable IDs and foreign-key/reference semantics for episode, script revision, scene, beat, hook, and packaging option.
4. Define validation for references against the exact screenplay revision.
5. Define how draft/accepted/rejected states map to existing database and approval states.
6. Define whether numeric scores remain optional and advisory.
7. Define migration, compatibility, and rollback behavior.
8. Add valid/invalid fixtures and regression tests before changing production validators.

## 5. Reference integrity requirements

A Retention Map must refer to the exact episode and screenplay revision it describes. Each scene/beat reference must resolve against that revision or be explicitly marked unresolved. A map copied from an outline or generic template is not evidence that it matches the screenplay.

Packaging alternatives must reference the same audience promise and must not imply story events absent from the screenplay.

Creative Review findings must reference the exact reviewed revision and cite evidence. A review decision is not a human approval state.

## 6. Non-goals

This proposal does not authorize database migrations, API changes, frontend changes, schema replacement, or agent activation. Those belong to an approved CR_007 implementation scope.
