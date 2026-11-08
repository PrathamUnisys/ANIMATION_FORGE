---
prompt_id: CORE_SECURITY_POLICY
version: 1.0.0
modified_date: 2026-11-09
description: Security boundaries, secret handling, path sandboxing, and MCP permissions
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Define security controls
---
# SECURITY POLICY

1. **Secrets Management**: API keys are stored via Windows Credential Manager (`keyring` / DPAPI) or encrypted local vault—never in Markdown files, JSON configs, or unredacted logs.
2. **Filesystem Sandboxing**: Agents may only read/write within their permitted project subdirectories. Path traversal (`..`) and writing over files in `APPROVED/` are blocked at the filesystem guard layer.
3. **MCP Permission Tiers**: Every tool is classified as `READ_ONLY`, `DRAFT_CREATION`, `LOCAL_MODIFICATION`, `EXTERNAL_NETWORK`, `PAID_OPERATION`, or `DESTRUCTIVE_OPERATION`.
4. **Prompt Injection Defense**: External research snippets and tool outputs are wrapped in `<untrusted_external_data>` delimiters and scanned for instruction-override patterns.
5. **No Unrestricted Shell**: AI agents never receive raw shell execution primitives.
