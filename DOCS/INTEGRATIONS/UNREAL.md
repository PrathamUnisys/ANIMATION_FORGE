---
prompt_id: INTEGRATION_UNREAL
version: 1.0.0
modified_date: 2026-11-09
description: Operational guidance for evaluating Unreal Engine integrations.
dependencies: ["TOOL_INTEL_POC", "TOOL_INTEL_TOOLCHAIN_APPROVAL"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial Unreal integration guidance
---
# Unreal Engine Integration

## Status
Unreal-specific execution is **planned/not implemented** in the inspected adapter. `SafeBlenderAndUnrealAdapter` stages a generic Python sample and example output after a human animatic gate; it does not import Unreal's Python API, connect Remote Control, create a Level Sequence, or invoke the Editor (`backend/integrations/blender_unreal_adapters.py`). The mention of Unreal in candidate/example documentation is not proof of support.

## Evaluation and safe adoption
1. Verify the exact Unreal release, platform, Editor and plugin availability, Python/Sequencer API status, Remote Control configuration, license terms, and hardware using current official sources. Mark preview/experimental API surfaces clearly.
2. Determine whether the project needs Editor automation, remote control, render-queue execution, or merely interchange; do not assume interchange is an integration.
3. Human-approve toolchain, any plugin installation, data exposure, network endpoint, downloads, and costs before a PoC.
4. Run a small isolated test on the target installation; bind remote control to a restricted local interface unless separately approved and secured. Capture actual logs, sequence, render, version, settings, and resource metrics.
5. Validate scene/timing/output in the application and obtain human creative approval.

Do not label the connection official, tested, or production-ready without direct evidence. This guidance does not enable the integration or authorize Editor execution.
