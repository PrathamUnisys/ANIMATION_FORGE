# Architecture

**Status:** Isolated local MVP implemented; repository-wide runtime has not been changed. This document describes current boundaries and remaining proposed stages.

## Overview

Use a small, local-first, file-based workspace as the system of record. The current CLI initializes a workspace, registers a new artifact path and hash, validates manifest integrity, counts narration, estimates runtime and checks selected references. Research and creative content remain in readable Markdown/JSON. No database, frontend, agent swarm or remote service was added.

```text
User idea + constraints
       │
       ▼
Brief ──► Research dossier / claim ledger
                    │
                    ▼
           Concept + architecture ── human selection
                    │
                    ▼
                 Script vN
              ┌─────┴──────┐
              ▼            ▼
     Independent review  Fact check
              └─────┬──────┘
                    ▼
             Script vN+1
                    │
        Deterministic checks/runtime
                    │
                    ▼
        Human approval → handoff
```

## Components and responsibilities

| Component | Responsibility | Cannot do |
|---|---|---|
| Workspace/manifest | Stable project ID, artifact paths, versions, source revision/hash, stage and check results | Select a story, invent evidence, or mark approval on behalf of a human |
| Brief/intake | Store the user's idea, audience, scope, language rule, desired format/runtime, production limits and open questions | Fill unknown facts/canon silently |
| Research dossier | Store attributable sources, locators, dates, source type and limitations | Prove a claim true from a URL alone |
| Claim ledger | Link atomic factual assertions to source evidence, scope and verification state | Treat generated prose or a source list as proof |
| Story/concept tools | Propose evidence-supported narrative routes and structure alternatives | Force one beat template or silently set human choices |
| Script/prompt kit | Produce speakable narration with visual/audio directions and claim links | Convert reconstructions into factual footage or alter approved history |
| Creative critic | Report passage-specific craft findings on exact script version | Revise or approve the work |
| Fact checker | Confirm support, scope, uncertainty and attribution claim by claim | Use a creative review as factual verification |
| Deterministic QC | Validate schema, counts, IDs, references, map/timing and metadata consistency | Judge engagement, truth, fairness or emotional quality |
| Human reviewer | Select concepts and approve the final artifact through existing governance | Have AI approval substituted for their decision |

## Data flow and revision lineage

Each artifact records project ID, artifact type, revision, created date, previous revision where relevant, status, source IDs/hashes, and its own file hash. A script revision stores the exact claim IDs/passages it uses. Review and fact-check artifacts store the exact script hash and reviewer role/provenance. Editing any narration creates a new script revision; it invalidates or marks downstream metadata stale until regenerated/reconciled.

## Existing Animation Forge integration

The current CR_006 story pipeline offers useful patterns: context hashes, exact source references, latest-outline approval gates, immutable script revisions, provider request provenance and separate deterministic/creative reports. Its current staged pipeline does not perform general web research, claim-level source verification or end-to-end documentary production. The older scaffold method is explicitly scaffold-only. The isolated module may export artifacts for later import, but no backend routes, database tables or shared schema are changed in this proposal.

## Human gates

Human review is required for selecting materially different concepts/architecture and for approval of the final script. Source/rights restrictions and approved canon outrank AI suggestions. An unresolved critical fact or scope issue blocks claiming fact clearance. Technical PASS status never means creative approval.

## External integrations

Initial implementation is manual/local. A researcher may use approved browser/search tools and save source references. No search provider, analytics connector, model provider, or rights service is assumed. Existing local LLM access may be used through a documented adapter only if that adapter can be verified and does not silently fall back to mock output.

## Failure behavior

Missing source, malformed JSON, failed schema validation, unavailable reviewer, unresolved finding, invalid reference or uncertain measurement remains visible. No stage advances by silently fabricating missing data. Each check reports its own result and evidence.
