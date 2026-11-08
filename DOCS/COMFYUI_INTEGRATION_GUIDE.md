---
prompt_id: DOCS_COMFYUI_INTEGRATION_GUIDE
version: 1.1.0
modified_date: 2026-11-09
description: Operational guide describing ComfyUI adapter behavior and verified-use requirements.
dependencies: ["CORE_SYSTEM_CONSTITUTION", "TOOL_INTEL_TOOLCHAIN_APPROVAL", "INTEGRATION_COMFYUI"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Added instruction metadata while retaining guide content
---
# ComfyUI Adapter Status and Operator Guide

## Implemented behavior
`backend/integrations/comfyui_adapter.py` validates supplied workflow node class names and `ckpt_name` values against **hard-coded** lists, writes supplied output bytes to a versioned path, and records a provenance manifest and database rows. It does not make HTTP/WebSocket requests, submit to `/prompt`, query live model/node inventories, or generate output. `check_connection_health` uses a caller-supplied `local_daemon_running` flag; it is not a socket health check. A returned `CONNECTED` value is therefore not independent live verification.

Manifest fields such as model IDs and node versions are fixed values in this implementation. Compare them with the actual run before relying on them as provenance. The adapter's class-name check is neither a complete graph/schema validator nor a security boundary.

## Operational use
Before any real run, verify the local ComfyUI installation, endpoint, nodes, model files and license, target hardware, and workflow in the actual host. Obtain human approval for toolchain choice, downloads, and any paid/network operation. Run only an approved workflow in draft storage through an explicitly configured live client path, then record actual versions, settings, logs, output hashes, inputs, and date. Do not mark an unexecuted or simulated workflow as tested.

Creative output remains a draft pending human review. See `DOCS/INTEGRATIONS/COMFYUI.md` and `DOCS/TOOL_INTELLIGENCE/POC_PLANNER.md`.
