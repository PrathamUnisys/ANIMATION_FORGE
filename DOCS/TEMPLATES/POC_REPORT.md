---
prompt_id: TEMPLATE_DOC_POC_REPORT
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable bounded proof-of-concept test plan and results template
dependencies: ["TEMPLATE_DOC_TOOL_RND_REPORT", "TEMPLATE_DOC_TOOL_COMPARISON", "SCHEMAS/RESEARCH_REPORT.schema.json", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable proof-of-concept report template
document_type: reusable_document_template
---
# TEMPLATE — PROOF-OF-CONCEPT REPORT

> Reusable planning and evidence template, not an executable agent prompt or authorization to install, download, spend, or execute. Obtain explicit human authorization before any cost-bearing or download action.

## Scope and authorization
- **Project / POC ID / candidate and version**: `[IDS]`
- **Owner / date / status**: `[DETAIL]`
- **Research/comparison references**: `[REPORT IDS]`
- **Purpose and bounded scope**: `[WHAT THIS POC WILL AND WILL NOT TEST]`
- **Explicit human authorization**: `[REVIEWER; SCOPE; COST/DOWNLOAD LIMIT; DATE; OR NOT AUTHORIZED]`
- **Environment / hardware / software**: `[OBSERVED ENVIRONMENT OR UNKNOWN]`

## Hypotheses and test design
| Requirement / hypothesis | Test case | Inputs and rights | Pass threshold | Measurement method |
|---|---|---|---|---|
| `[REQUIREMENT]` | `[TEST]` | `[AUTHORIZED INPUTS]` | `[THRESHOLD]` | `[HOW VERIFIED]` |

## Execution log
| Date/time | Test ID | Actual action/tool/version | Cost / resource use | Observed output/evidence | Deviations |
|---|---|---|---|---|---|
| `[TIME]` | `[ID]` | `[ONLY ACTIONS THAT OCCURRED]` | `[VALUE OR NOT MEASURED]` | `[REFERENCE]` | `[DETAIL]` |

## Results
- **Results by criterion**: `[OBSERVED DATA; INCLUDE FAILED AND NOT-RUN TESTS]`
- **Reproducibility / limitations**: `[INPUTS, CONFIG, ENVIRONMENT, SAMPLE SIZE, UNKNOWN DETAILS]`
- **Quality, reliability, performance, cost**: `[MEASUREMENTS AND METHOD OR UNTESTED]`
- **Privacy, security, license, safety findings**: `[EVIDENCE AND OPEN ITEMS]`
- **Artifacts and asset records**: `[PATHS/IDS OR NONE; NEVER CLAIM NONEXISTENT FILES]`

## Recommendation and decision
- **Conclusion**: `[SUPPORTED / NOT SUPPORTED / INCONCLUSIVE]`
- **Recommendation and alternatives**: `[DETAIL]`
- **Risks and follow-up**: `[DETAIL]`
- **Human decision**: `[AWAITING_HUMAN_APPROVAL / APPROVED / REJECTED / ADDITIONAL_RESEARCH_REQUESTED]`
- **Reviewer / date / rationale**: `[RECORD]`

`SCHEMAS/RESEARCH_REPORT.schema.json` can represent project R&D reports and `poc_results`; this prose POC report is not itself a schema-defined record.
