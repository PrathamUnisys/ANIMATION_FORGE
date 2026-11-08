---
prompt_id: INTEGRATION_CUSTOM_PLUGINS
version: 1.0.0
modified_date: 2026-11-09
description: Govern third-party creative plugin discovery, testing, and installation.
dependencies: ["TOOL_INTEL_LICENSING", "TOOL_INTEL_POC", "TOOL_INTEL_TOOLCHAIN_APPROVAL"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial plugin integration guidance
---
# Custom Plugins

## Status
`backend/integrations/plugin_manager.py` validates a plugin manifest and records lifecycle state. It requires a human authorization flag for `APPROVED_FOR_INSTALLATION`, `INSTALLED`, and `ENABLED`, and prevents `INSTALLED` unless installation was approved. This manager does not download, install, execute, sandbox, or validate plugin behavior.

## Lifecycle and controls
Use `DISCOVERED → EVALUATED → INSTALLATION_PROPOSED → APPROVED_FOR_INSTALLATION → INSTALLED → TESTED → ENABLED`; allow `DISABLED`/`REMOVED` for rollback. Keep package identity, version/hash, publisher, source, permissions, dependencies, supported host versions, license, data flows, and rollback instructions in the review record.

Before installation, verify official vs community source, current compatibility and license, inspect dependencies, malware/security advisories, and backup/restore. Get explicit human approval for the exact version, host, permissions, and project; do not auto-update or enable. Test with sample assets in an isolated profile, verify behavior, logs, performance, and outputs, then request enablement approval if required.

Treat manifest validation and lifecycle status as metadata—not a security sandbox, compatibility proof, or successful test. Preserve human approval of generated creative work separately.
