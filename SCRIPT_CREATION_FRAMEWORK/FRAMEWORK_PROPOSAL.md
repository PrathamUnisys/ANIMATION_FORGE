# Script Creation Framework — Proposal

**Status:** Design proposal. No protected repository framework is changed or approved here.  
**Purpose:** Provide a reusable, human-directed route from a rough topic to a researched, reviewable YouTube documentary/explainer script and production handoff.

## Proposed flow

```text
Idea and constraints
  → Research dossier + claim ledger
  → Story opportunity and concept choice
  → Story architecture
  → Package and opening proposal
  → Script draft
  → Independent creative review + factual verification
  → Revision and exact-revision reconciliation
  → Deterministic checks + human approval
  → Production handoff
```

Stages may be combined for simple topics, but claim verification and independent review remain distinct from writing. Every generated/edited artifact is versioned. Missing evidence, rights questions and human decisions remain visible.

## Roles / module boundaries

- **Project coordinator:** owns stage/status bookkeeping and artifact links; not a creative approver.
- **Researcher:** source collection, claim ledger, chronology/mechanism and uncertainty. The writer's own knowledge does not replace this evidence.
- **Story editor/architect:** proposes viable narrative routes and a spine that matches the evidence; does not authorize canon or rights.
- **Writer:** drafts from selected architecture and evidence; must preserve unresolved claims as caveats or omit them.
- **Independent critic:** receives exact package/script and requested review scope without writer self-assessment or claimed fixes; returns passage-specific findings only.
- **Fact checker:** audits factual claims against source text and limits; cannot certify unsupported source quality automatically.
- **Deterministic QC:** counts, references, IDs, map/timecode consistency, required state, schema. Does not evaluate story or verify facts.
- **Human owner:** selects meaningful creative options and approves the final revision through the repository's existing governance path.

This is a responsibility model, not a requirement to run eight AI agents. Initial implementation should use a small coordinator, reusable prompts/templates, deterministic utilities, and separate reviewer runs only where available.

## Artifact lifecycle

1. **BRIEF_DRAFT** — intake normalized, unknowns listed.
2. **RESEARCH_DRAFT / RESEARCH_REVIEW** — source dossier and claims built; unsupported material remains blocked or caveated.
3. **CONCEPT_PROPOSED / CONCEPT_SELECTED** — concepts and trade-offs shown; selection is a human decision.
4. **ARCHITECTURE_DRAFT / ARCHITECTURE_SELECTED** — story spine, beats, visual carrier and open questions.
5. **SCRIPT_DRAFT** — complete narration/production directions, linked claims.
6. **CREATIVE_REVIEW / FACT_CHECK** — independent review and claim audit, distinct reports.
7. **REVISION** — new revision with a finding-response log and prior version retained.
8. **QC_RECONCILED** — exact revision's deterministic checks and companion outputs agree; failures/unrun checks explicit.
9. **HUMAN_REVIEW / APPROVED** — approval remains outside AI authority and follows repository governance.
10. **PRODUCTION_HANDOFF** — only after appropriate human approval, with measured timing added later.

These statuses describe artifacts/stages and do not replace repository approval states until integrated through a Change Request.

## Quality standard

Use passage-specific BLOCKER / MAJOR / MINOR / NOTE findings. A blocker means the script cannot be responsibly used/reviewed as scoped (e.g. critical unsupported claim, unresolved source/rights gate, broken causal premise), not merely disliked. Report observation, interpretation, consequence, recommendation, confidence, and unchecked areas. No average score gate. Fact checking records claim-level evidence status. Deterministic QC reports each result separately as PASS, FAIL, NOT_EXECUTED, NOT_AVAILABLE, NOT_TESTED or NOT_APPLICABLE as appropriate. These result labels are not human approval.

## Data boundaries

- Brief and user direction are distinct from sourced fact.
- Sources and claim ledger retain attribution and date; script points to claims by stable ID or an equivalent traceable link.
- Concept/architecture proposals remain distinct from selected human decisions.
- Exact script text is immutable per revision; revisions never overwrite history.
- Reviews identify the revision/hash they inspected and distinguish independent reviewer work from author self-review.
- Count/runtime/map/package metadata are regenerated or reconciled from the exact revision.
- Analytics, if later used, are measured platform data and do not retroactively become editorial evidence about an unpublished script.

## Integration boundary and governance

Initial artifacts and any code should live under `SCRIPT_CREATION_FRAMEWORK/`. Do not edit `CORE/`, `MODES/`, `SCHEMAS/`, `AGENTS/`, `DEPARTMENTS/`, global workflow or application runtime without an approved Change Request. Before integration, resolve the contradictory score-based and no-score creative review guidance; document exact files, compatibility, tests and rollback. The existing CR_006 screenplay lifecycle may be reused via documented adapters, but its current pipeline is not a general research/fact-checking engine.

## Not claimed

The proposal does not establish that a particular hook, duration, story engine or writing style increases retention. It does not automatically verify facts, clear rights, measure runtime, approve work, or guarantee publication performance.
