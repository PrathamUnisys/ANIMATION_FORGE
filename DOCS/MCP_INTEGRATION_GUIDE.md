---
prompt_id: DOCS_MCP_INTEGRATION_GUIDE
version: 1.1.0
modified_date: 2026-11-09
description: Operational guide for MCP gateway capabilities, permission tiers, and limitations.
dependencies: ["CORE_SYSTEM_CONSTITUTION", "TOOL_INTEL_TOOLCHAIN_APPROVAL", "INTEGRATION_MCP_GATEWAY"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Added instruction metadata while retaining guide content
---
# Internal MCP Gateway: Implemented Metadata and Limits

`backend/integrations/mcp_gateway.py` defines 17 built-in tool metadata entries and stores external MCP server registrations after validating declared `STDIO`/`STREAMABLE_HTTP` transport and permission tiers. Registration requires a human-approved-install flag. In the inspected implementation, `execute_mcp_tool` returns an acknowledged argument echo rather than invoking a remote tool; `run_server_health_check` can set status using a simulation flag. Do not represent these methods as a live MCP client/server transport or verified connection.

## Permission tiers
- `READ_ONLY`: no intended mutation; verify actual tool behavior.
- `DRAFT_CREATION`: requires approved production instructions.
- `LOCAL_MODIFICATION`: restrict to project drafts; require scoped authorization.
- `EXTERNAL_NETWORK`: review and audit data sent externally.
- `PAID_OPERATION`: explicit human spending/budget authorization.
- `DESTRUCTIVE_OPERATION`: individual human authorization per call.

These are classifications, not proof that all boundaries are enforced. The current executor directly checks the draft, paid, and destructive flags; do not infer enforcement of other tiers from their presence.

Review custom-server provenance, permissions, schemas, versions, network/filesystem access, and data handling before human-approved installation. Test live behavior safely before claiming integration. See `DOCS/INTEGRATIONS/MCP_GATEWAY.md` and `DOCS/INTEGRATIONS/CUSTOM_MCP.md`.
