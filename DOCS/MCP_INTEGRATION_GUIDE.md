# Internal MCP Gateway & Custom Adapter Guide

`AnimationForgeMcpGateway` (`backend/integrations/mcp_gateway.py`) implements both an MCP Client (`STDIO` and `Streamable HTTP`) and an MCP Server exposing 17 controlled studio tools.

## 6-Tier Permission Classification
- `READ_ONLY`: Allowed for configured, connected integrations.
- `DRAFT_CREATION`: Requires approved production instructions.
- `LOCAL_MODIFICATION`: Restricted to draft project directories.
- `EXTERNAL_NETWORK`: Audited outbound requests.
- `PAID_OPERATION`: Requires explicit human budget/spending authorization.
- `DESTRUCTIVE_OPERATION`: Requires individual human authorization per call.
