---
prompt_id: TEMPLATE_DOC_TOOLCHAIN_PROFILE
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable proposed or approved project toolchain profile template
dependencies: ["TEMPLATE_DOC_TOOL_COMPARISON", "SCHEMAS/TOOLCHAIN.schema.json", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable toolchain profile template
document_type: reusable_document_template
---
# TEMPLATE — TOOLCHAIN PROFILE

> Reusable profile template, not an executable agent prompt or evidence that tools are installed, connected, or approved. Mark proposed versus locked status accurately.

## Profile identity
- **Toolchain ID / project ID / version**: `[IDS; INTEGER VERSION]`
- **Profile owner / date**: `[DETAIL]`
- **Status**: `[PROPOSED / AWAITING_HUMAN_REVIEW / APPROVED / REJECTED / RETIRED]`
- **Locked**: `[TRUE ONLY AFTER AUTHORIZED HUMAN APPROVAL; OTHERWISE FALSE]`
- **Cost limit (USD)**: `[AUTHORIZED LIMIT OR 0/UNSET]`

## Tools and workflow
| Tool ID / version | Provider ID | Workflow ID | Configuration reference | Dependencies | Input formats | Output formats | Approved capabilities |
|---|---|---|---|---|---|---|---|
| `[ID]` | `[ID OR UNKNOWN]` | `[ID OR UNKNOWN]` | `[REFERENCE; NO SECRETS]` | `[IDS]` | `[FORMATS]` | `[FORMATS]` | `[SCOPED LIST]` |

## Fallbacks and constraints
- **Fallback options**: `[TOOL / CONDITIONS / OWNER; NOT ASSUMED AVAILABLE]`
- **Known limitations / compatibility**: `[DETAIL]`
- **License and commercial-use status**: `[EVIDENCE OR UNRESOLVED]`
- **Cost/download authorization requirements**: `[DETAIL]`
- **Security/privacy considerations**: `[DETAIL; NO CREDENTIALS IN THIS DOCUMENT]`

## Approval history
| Approval ID / target revision | State | Human reviewer | Date | Comments |
|---|---|---|---|---|
| `[ID]` | `[AWAITING_HUMAN_REVIEW / APPROVED / REVISION_REQUESTED / REJECTED]` | `[HUMAN REVIEWER OR PENDING]` | `[DATE]` | `[RATIONALE]` |

Structured profile fields map to `SCHEMAS/TOOLCHAIN.schema.json`. A proposed profile must remain unlocked and cannot be treated as approved for execution until the required human decision is recorded. Do not put credentials or secret configuration values here.
