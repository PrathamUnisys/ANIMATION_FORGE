---
prompt_id: DOCS_UNREAL_INTEGRATION_GUIDE
version: 1.1.0
modified_date: 2026-11-09
description: Operational guide for evaluating Unreal Engine integration capability and safety.
dependencies: ["CORE_SYSTEM_CONSTITUTION", "TOOL_INTEL_TOOLCHAIN_APPROVAL", "INTEGRATION_UNREAL"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Added instruction metadata while retaining guide content
---
# Unreal Engine Evaluation Guide

The inspected `backend/integrations/blender_unreal_adapters.py` contains no Unreal-specific API calls, Remote Control client, or Editor execution. Unreal support is **planned/unverified at application integration level**; the adapter's name and generic sample output are not evidence of an Unreal connection.

For a proposed integration, verify the exact Unreal version, plugins, Python/Sequencer API status, Remote Control configuration, license, hardware, and target workflow against current official sources and the real installation. Flag experimental/preview interfaces, separate official APIs from community bridges, and record versions and dates.

Get human approval before plugin installation, endpoint/network configuration, downloads, or paid work. Test with a minimal isolated project, capture logs and actual rendered output, restrict access to the intended interface, and manually review the result. Do not claim 5.5+ support without verified compatibility. Human toolchain and creative approvals remain mandatory. See `DOCS/INTEGRATIONS/UNREAL.md`.
