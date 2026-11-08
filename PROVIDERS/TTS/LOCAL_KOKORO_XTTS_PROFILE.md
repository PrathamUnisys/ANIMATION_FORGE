---
prompt_id: PROVIDER_TTS_LOCAL
version: 1.1.0
modified_date: 2026-11-09
description: Local TTS candidate profile; model execution, offline operation, licensing, and cost require verification.
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial provider profile
  - version: 1.1.0
    date: 2026-11-09
    summary: Clarified unimplemented status and verification requirements
---
# PROVIDER PROFILE: PROVIDER_TTS_LOCAL

## Capability status
`ProviderManager` registers metadata for `LOCAL_KOKORO_TTS` and the identifier `kokoro-82m-v1.0`; its `invoke_llm` method is unrelated to speech synthesis. Production code builds an example Kokoro payload but writes a simple tone WAV rather than invoking a TTS model (`backend/providers/manager.py`, `backend/departments/production_studios.py`). XTTSv2 is not registered there. “Offline,” “zero cost,” and reference voice cloning are unverified candidate claims, not application capabilities.

## Verification before selection
Verify the exact source repository/model files and versions; each software, model and voice license; commercial and output terms; supported languages; required runtimes, accelerator and storage; and any voice-reference consent requirements. Separate official model releases from community wrappers and forks. Confirm offline behavior by testing without network access—do not infer it from local weights.

Authorize downloads and toolchain choice with a human. Test a rights-cleared sample on the target machine and record versions, settings, resource use, output format, logs, and measured runtime. Human-review speech quality and permission before use.
