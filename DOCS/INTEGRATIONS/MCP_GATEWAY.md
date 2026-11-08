---
prompt_id: INTEGRATION_MCP_GATEWAY
version: 1.0.0
modified_date: 2026-11-09
description: Operational guidance for Animation Forge's MCP gateway.
dependencies: ["TOOL_INTEL_TOOLCHAIN_APPROVAL"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial gateway guidance with mock behavior caveats
---
# MCP Gateway

## Status
`backend/integrations/mcp_gateway.py` defines internal tool metadata, validates external-server registration transport and permission tiers, and applies selected approval flags. External registration requires human-approved installation. However, the inspected `execute_mcp_tool` returns an acknowledged echo of arguments; it does not invoke an MCP SDK client or remote tool. The health-check method accepts a simulated reachability flag. Treat execution/connection as **scaffolded, not live verified**.

## Governance
Use the six declared tiers: `READ_ONLY`, `DRAFT_CREATION`, `LOCAL_MODIFICATION`, `EXTERNAL_NETWORK`, `PAID_OPERATION`, `DESTRUCTIVE_OPERATION`. Classify every external tool from its actual effects, not its name. Apply least privilege, exact server/tool allowlists, bounded schemas, timeout and output limits, audit records, and explicit consent. Require approved production instructions for draft creation, explicit budget approval for paid work, and individual approval for destructive actions.

Before registration, review server source/maintainer, transport, command/endpoint, environment, filesystem/network access, secrets, data handling, version, and update process. Human approval is required for install. Do not expose arbitrary file access or treat transport support as an integration security review.

## Test evidence
Test authentication, live connection, schema validation, denial cases, timeout/error handling, and audit behavior against an isolated server before production. Clearly label simulated tests. Do not pass real arguments/secrets through a scaffold that only echoes them. Human approvals remain independent gates.
