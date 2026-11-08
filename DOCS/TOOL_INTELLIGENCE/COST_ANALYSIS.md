---
prompt_id: TOOL_INTEL_COST
version: 1.0.0
modified_date: 2026-11-09
description: Estimate end-to-end project tool costs and require authorization.
dependencies: ["TOOL_INTEL_REQUIREMENTS", "TOOL_INTEL_ONLINE_RESEARCH"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial cost analysis procedure
---
# Cost Analysis

## Estimate total cost of ownership
Use a dated official pricing/terms source for paid products and record currency, region, plan, billing unit, taxes/fees if known, included quota, overage, and cancellation terms. Estimate the project workload from approved requirements: calls/characters/tokens/minutes, retries, revisions, storage, egress, seats, and duration. Show assumptions and low/expected/high scenarios; flag unknowns instead of filling them with a guessed price.

For local/self-hosted tools, “no per-run API charge” is not “free.” Account for hardware acquisition/use, power, storage, model downloads, setup, maintenance, and operator time when material. Separate sunk and incremental costs.

## Authorization gate
Before any paid call, subscription, credit use, download with cost/quota implications, or model/toolchain PoC, present the action, maximum spend/data transfer, duration, and cancellation/cleanup plan to the human. Wait for explicit approval. Approval must be scoped; it does not authorize later spend or unrelated downloads. Stop at the approved cap.

The MCP gateway distinguishes `PAID_OPERATION`; the R&D POC method accepts a human-authorization flag for cost/downloads. These are control points, not proof of accurate estimates or provider billing enforcement (`backend/integrations/mcp_gateway.py`, `backend/rnd/research_engine.py`). `ProviderManager` contains example rate metadata, not current vendor pricing (`backend/providers/manager.py`). Verify current rates independently.

## Output
Provide dated sources, calculation, exposure/cap, uncertainty, and human decision. Update estimates when workload, rates, plan, or scope changes. Cost approval does not constitute toolchain or creative approval.
