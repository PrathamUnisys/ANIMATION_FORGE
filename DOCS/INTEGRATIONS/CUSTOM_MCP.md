---
prompt_id: INTEGRATION_CUSTOM_MCP
version: 1.0.0
modified_date: 2026-11-09
description: Requirements for assessing and adding a third-party MCP server.
dependencies: ["INTEGRATION_MCP_GATEWAY", "TOOL_INTEL_LICENSING", "TOOL_INTEL_POC"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial third-party MCP integration guidance
---
# Custom MCP Server

## Status
The gateway can store a registered server's metadata and accepts `STDIO` or `STREAMABLE_HTTP` as declared transport values (`backend/integrations/mcp_gateway.py`). Live protocol handshakes, tool discovery, and tool invocation are not implemented by the inspected gateway method; execution echoes arguments. Do not describe registration as a working MCP client connection.

## Intake checklist
- Identify official vs community server, maintainer, repository/release, license, supported protocol/version, dependencies, and security/update history.
- Inventory every tool/resource/prompt, exact schema, permission tier, filesystem/network/process scope, data sent/returned, and side effects.
- Inspect source/dependencies or obtain a provenance-appropriate package; pin versions and hashes. Do not run unknown code on the production host.
- Obtain explicit human approval before install/registration. Require scoped approval for paid, destructive, network, or project-modifying actions.
- Test isolated, least-privileged operation: malformed arguments, injection-like inputs, denial cases, disconnects, timeouts, oversized responses, and logs. Review output before use.

Document transport and capabilities as official/community/experimental, and separate code inspected from behavior actually exercised. No data-sharing or installation consent is implied here.
