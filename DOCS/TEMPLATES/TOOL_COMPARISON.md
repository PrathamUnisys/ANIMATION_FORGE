---
prompt_id: TEMPLATE_DOC_TOOL_COMPARISON
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable side-by-side tool evaluation and trade-off template
dependencies: ["TEMPLATE_DOC_TOOL_RND_REPORT", "SCHEMAS/TOOL.schema.json", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable tool comparison template
document_type: reusable_document_template
---
# TEMPLATE — TOOL COMPARISON

> Reusable comparison worksheet, not an executable agent prompt or an approval. Keep evidence, estimates, and judgments distinguishable.

## Comparison scope
- **Project / report ID / date / owner**: `[DETAIL]`
- **Production use case / required output**: `[DETAIL]`
- **Constraints and must-haves**: `[COST, PLATFORM, LICENSE, PRIVACY, QUALITY, AUTOMATION]`
- **Candidates and versions**: `[TOOL IDs AND VERSIONS]`
- **Source research references**: `[URLS / REPORT IDs / RETRIEVAL DATE]`

## Evidence comparison
| Criterion | Importance / weight | Candidate A: score + evidence | Candidate B: score + evidence | Unknowns / test needed |
|---|---:|---|---|---|
| Quality / consistency | `[WEIGHT]` | `[SCORE; SOURCE/TEST]` | `[SCORE; SOURCE/TEST]` | `[GAP]` |
| Reliability / performance | `[WEIGHT]` | `[DETAIL]` | `[DETAIL]` | `[GAP]` |
| Automation / integration | `[WEIGHT]` | `[DETAIL]` | `[DETAIL]` | `[GAP]` |
| Cost / hardware | `[WEIGHT]` | `[DETAIL]` | `[DETAIL]` | `[GAP]` |
| Compatibility / maintainability | `[WEIGHT]` | `[DETAIL]` | `[DETAIL]` | `[GAP]` |
| Licensing / commercial use | `[WEIGHT]` | `[SOURCE; UNCERTAINTY]` | `[SOURCE; UNCERTAINTY]` | `[LEGAL REVIEW]` |

Use criteria and score ranges from `SCHEMAS/TOOL.schema.json` when recording a structured `ToolCandidate`; its scores are 0–10. Do not calculate a score for missing evidence or represent a research score as test performance.

## Trade-offs and recommendation
- **Disqualifying gaps / risks**: `[DETAIL]`
- **Advantages / disadvantages by candidate**: `[DETAIL]`
- **Recommended candidate or no recommendation**: `[OPTION AND RATIONALE]`
- **Required proof-of-concept tests**: `[TESTS, PASS CRITERIA, AUTHORIZATION/COST NEEDS]`
- **Fallbacks**: `[OPTIONS; NOT ASSUMED CONFIGURED]`

## Decision
- **Recommendation status**: `[PROPOSED / AWAITING HUMAN APPROVAL / APPROVED / REJECTED / MORE RESEARCH]`
- **Human reviewer / decision / date / comments**: `[RECORD]`
- **Next step**: `[AUTHORIZED POC / TOOLCHAIN PROPOSAL / STOP]`

No dedicated comparison-document schema exists; the tool schema applies to individual candidates, not this whole worksheet.
