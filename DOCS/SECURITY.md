# Security & Safety Controls

1. **Zero Plaintext Secrets**: API keys are managed through `SecureCredentialVault` (Windows Credential Manager / OS keyring) and scrubbed from all logs via regex redaction (`[REDACTED_SECRET]`).
2. **Directory Sandboxing**: `resolve_safe_project_path` blocks `..` traversal, absolute paths, cross-department access, and any write to `APPROVED/`.
3. **Prompt Injection Protection**: External research snippets are scanned for override patterns and isolated inside `<untrusted_external_data>` tags.
4. **No Unrestricted Shell**: No AI agent has shell execution access.
