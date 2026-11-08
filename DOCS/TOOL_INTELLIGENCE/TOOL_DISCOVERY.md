---
prompt_id: TOOL_INTEL_DISCOVERY
version: 1.0.0
modified_date: 2026-11-09
description: Discover tool candidates and classify integration evidence.
dependencies: ["TOOL_INTEL_REQUIREMENTS", "TOOL_INTEL_ONLINE_RESEARCH"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial candidate discovery procedure
---
# Tool Discovery

## Search and qualify
Search only for candidates that address a documented requirement. Capture product and exact edition/version, maintainer, official project URL, release/support status, deployment mode, and candidate-specific evidence. Search official vendor/product docs first; use repositories and community sources to identify maintenance signals, known limitations, and integration examples, labeling them accordingly.

Classify candidate connections independently:
- **Official**: documented and maintained by the product owner.
- **Community/third-party**: maintained outside the product owner; identify maintainer and project.
- **Experimental**: explicitly unstable, preview, or unverified for the intended version/use.
- **Internal adapter**: application-owned code; state exactly what that code does today.
No category implies the application has implemented the connection. Distinguish an installed/configured connector from a name, mock, demo, or design proposal.

## Screening
Apply hard constraints first: intended use/license, OS/runtime, data policy, required inputs and outputs, hardware ceiling, and budget. Record exclusion reasons and source date. Keep a balanced shortlist with a viable fallback where requirements warrant it; avoid collecting names without a decision path.

## Lifecycle and output
The research engine recognizes `DISCOVERED`, `RESEARCHED`, `TESTED`, `RECOMMENDED`, `APPROVED`, `REJECTED`, and `RETIRED` (`backend/rnd/research_engine.py`). Use these as evidence-backed states; no state is a substitute for human authorization. Produce a candidate register with source ledger, requirement coverage, risks, and required next check.

Important implementation caveat: engine candidate data contains hard-coded examples and scores, and its “authorized POC” currently returns fixed metrics without running a tool. Treat those records as demo/scaffolding, not independently verified discovery or test results.
