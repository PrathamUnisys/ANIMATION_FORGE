---
prompt_id: PROVIDER_AUDIO_SFX
version: 1.1.0
modified_date: 2026-11-09
description: Audio and sound-effects candidate profile with explicit implementation and evidence status.
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial provider profile
  - version: 1.1.0
    date: 2026-11-09
    summary: Clarified status, verification requirements, licensing, and approvals
---
# PROVIDER PROFILE: PROVIDER_AUDIO_SFX

## Capability status
- **Application integration:** No SFX/music provider or Stable Audio client is registered in `backend/providers/manager.py`. The production studio can write a simple synthesized-tone WAV for dialogue placeholder output, not model-generated SFX/music (`backend/departments/production_studios.py`, `_synthesize_clean_wav`).
- **Candidate only:** Stable Audio Open and local Foley matching are profile concepts, not verified or implemented generation capabilities. Do not state an API, model terms, quality, cost, or supported hardware without current primary-source evidence.

## Evaluation checklist
For each candidate, verify exact model/version and source, license/terms for model, training data and outputs, commercial use, attribution, source-recording rights, prompt/audio limits, formats, latency, current hardware needs, maintenance, and reproducible test results. Distinguish official service/API from community models, scripts, and libraries.

For Foley libraries, record provenance, license, acquisition source, and per-asset metadata; do not assume a local file is cleared for reuse. Before paid use, download, or external transfer, present scope and cost/data exposure for human approval. Do not infer costs as zero.

Human review must assess intelligibility, clipping, loudness, synchronization, creative fit, and licensing before an audio deliverable is approved. See `DOCS/INTEGRATIONS/EDITING_TOOLS.md` and `DOCS/TOOL_INTELLIGENCE/LICENSING_CHECK.md`.
