---
prompt_id: TOOL_INTEL_HARDWARE
version: 1.0.0
modified_date: 2026-11-09
description: Assess actual workstation compatibility and resource headroom.
dependencies: ["TOOL_INTEL_REQUIREMENTS", "TOOL_INTEL_DISCOVERY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial hardware verification procedure
---
# Hardware Compatibility

Collect the actual host's OS/build, CPU, physical/logical cores, RAM, GPU model, driver/runtime, dedicated/shared VRAM, free disk, and relevant peripherals. Note how and when each value was observed; do not substitute a project baseline or vendor minimum for a host probe.

For each pinned tool/model/version, compare official minimum/recommended requirements, supported OS and acceleration backend, storage/download size, and workload peak memory with measured available resources. Verify key features (e.g., GPU backend, codecs, headless mode) in the intended environment. Leave safety margin for concurrent workloads; record throttling, latency, and fallback behavior from a real test only.

**Status rule:** `compatible` requires evidence for the exact target host/version/workload. Otherwise report `provisionally compatible`, `incompatible`, or `unknown`, with blockers and test needed. Avoid universal VRAM/CPU claims; hardware needs vary by resolution, precision, model, scene, and settings.

The current `inspect_hardware_profile` returns a hard-coded 16 GB VRAM/32 GB RAM baseline and only reads OS/architecture/CPU count (`backend/rnd/research_engine.py`). It is not a full hardware inventory and must not be reported as a live measurement. The schema's `hardware_compatible` boolean is likewise not proof of host testing.

Obtain human authorization before downloads or resource-intensive POCs. Document versions, settings, measured peaks, host conditions, and cleanup.
