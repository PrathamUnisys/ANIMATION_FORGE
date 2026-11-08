---
prompt_id: INTEGRATION_COMFYUI
version: 1.0.0
modified_date: 2026-11-09
description: Operational guidance for local ComfyUI image and video workflows.
dependencies: ["TOOL_INTEL_TOOLCHAIN_APPROVAL", "PROVIDER_IMAGE_COMFYUI", "PROVIDER_VIDEO_COMFYUI"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial integration guidance with implementation status
---
# ComfyUI Integration

## Status
**Implemented, limited adapter:** `backend/integrations/comfyui_adapter.py` validates supplied graph node types and `ckpt_name` values against hard-coded inventories, records a connection status selected by a caller-provided boolean, and writes caller-supplied output bytes plus provenance. **Not implemented in this adapter:** HTTP/WS connection, `/prompt` submission, querying live installed nodes/models, or generation. A displayed `CONNECTED` state is not a live health check. Do not claim a live ComfyUI integration from these methods alone.

## Operator workflow
1. Verify and record local ComfyUI version, endpoint, custom nodes, model/checkpoint files, licenses, and resource needs in the target environment.
2. Obtain toolchain, download, and cost approvals; use a project-approved workflow and draft-only output location.
3. Before execution, inspect the graph and every node/model input; a local manifest or adapter allowlist is not a security boundary.
4. Run through an explicitly configured/verified ComfyUI client path, capture actual job IDs, logs, outputs, versions, seed and settings. Do not describe a locally validated JSON graph as generated output.
5. Preserve workflow, model identifiers/hashes, inputs, seed, output hash, run date, and source/license evidence. Human-review each creative deliverable.

The adapter's manifest includes fixed model/node-version fields; verify them against the actual run before treating provenance as factual. Remote use requires separate network, privacy, security, and cost review; no endpoint is approved by this guide.
