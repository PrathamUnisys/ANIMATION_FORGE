---
prompt_id: TEMPLATE_DOC_TOOL_RND_REPORT
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable evidence-based tool research and recommendation report template
dependencies: ["SCHEMAS/RESEARCH_REPORT.schema.json", "SCHEMAS/TOOL.schema.json", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable tool R&D report template
document_type: reusable_document_template
---
# TEMPLATE — TOOL R&D REPORT

> Reusable research-report template, not an executable agent prompt, tool endorsement, or claim that research/tests were performed. Mark unavailable evidence and untested candidates explicitly.

## Report metadata
- **Report ID / project ID / research date**: `[IDS; DATE]`
- **Owner / scope / decision needed**: `[DETAIL]`
- **Status**: `[DRAFT / AWAITING HUMAN APPROVAL / APPROVED / REJECTED / ADDITIONAL RESEARCH REQUESTED]`

## Requirements and method
- **Production need / use case**: `[TASK AND BOUNDARIES]`
- **Requirements**: `[FUNCTIONAL, QUALITY, HARDWARE, COST, LICENSE, SAFETY, MAINTENANCE]`
- **Search methodology and limits**: `[SOURCES, QUERIES, DATE RANGE, ACCESS LIMITATIONS]`
- **Evaluation criteria / weights**: `[CRITERIA AND RATIONALE]`

## Evidence and candidates
| Candidate / version | Official source URL and source type | Retrieved date | License / commercial-use evidence | Capabilities / limits | Test status |
|---|---|---|---|---|---|
| `[TOOL]` | `[URL; official_docs / github_repo / pricing_page / community_report]` | `[DATE]` | `[SOURCE AND UNCERTAINTY]` | `[FACTS WITH CITATIONS]` | `[NOT TESTED / TESTED WITH EVIDENCE]` |

For structured records, use `SCHEMAS/TOOL.schema.json`; record scores only when supported by evidence and use its 0–10 scales. Use `SCHEMAS/RESEARCH_REPORT.schema.json` for report fields including `report_id`, `project_id`, `research_date`, `search_methodology`, `requirements`, `candidates`, `recommendations`, and `decision_status`.

## Findings and recommendation
- **Findings by requirement**: `[EVIDENCE; SOURCE; CONFIDENCE; GAPS]`
- **Recommendation(s) and rationale**: `[OPTIONS; TRADE-OFFS; NOT AN APPROVAL]`
- **Estimated cost / hardware / compatibility**: `[BASIS, RANGE, DATE, OR UNKNOWN]`
- **Licensing / rights risks**: `[UNRESOLVED ITEMS AND OWNER]`
- **Alternatives rejected / why**: `[DETAIL]`

## Tests and next steps
| Test / environment | Authorization / cost basis | Procedure summary | Observed result / evidence | Limitations |
|---|---|---|---|---|
| `[TEST OR NOT RUN]` | `[REQUIRED PERMISSION]` | `[SUMMARY]` | `[EVIDENCE]` | `[LIMITS]` |

- **Decision status**: `[AWAITING_HUMAN_APPROVAL / APPROVED / REJECTED / ADDITIONAL_RESEARCH_REQUESTED]`
- **Authorized human reviewer / decision / date**: `[RECORD; NO AUTO-APPROVAL]`
- **Proposed next step**: `[COMPARISON / AUTHORIZED POC / STOP]`
