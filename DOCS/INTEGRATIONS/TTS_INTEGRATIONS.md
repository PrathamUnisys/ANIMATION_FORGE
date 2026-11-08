---
prompt_id: INTEGRATION_TTS
version: 1.0.0
modified_date: 2026-11-09
description: Guidance for evaluating local and hosted text-to-speech providers.
dependencies: ["TOOL_INTEL_COST", "TOOL_INTEL_LICENSING", "TOOL_INTEL_POC"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial TTS integration guidance
---
# TTS Integrations

## Status
`ProviderManager` contains metadata for ElevenLabs and local Kokoro, validates some setting names, and estimates usage from configured rates. In the inspected implementation it does not make TTS API calls or synthesize through those providers (`backend/providers/manager.py`). `backend/departments/production_studios.py` assembles example provider payloads but writes a simple tone WAV instead of using a speech model. `PROVIDERS/TTS/` profiles describe candidate/provider intent, not proof of execution. Kokoro/XTTS and ElevenLabs must be treated as unverified until separately tested.

## Evaluation
For every model/version confirm official API/SDK, supported language/voice, quotas/pricing, retention/training policy, commercial/voice rights, and exact controls from current primary sources. Label any community wrapper/community model as such. Never infer consent or cloning rights from possession of a reference recording; require documented speaker authorization and lawful use.

Use approved dialogue text; do not add unspoken stage directions to spoken content. Test pronunciation, timing, voice consistency, artifacts, output format, and offline behavior with rights-cleared samples. Capture actual request settings and response/output evidence; do not publish secrets or sample voices without approval.

Cloud calls require explicit data and spending approval; local model downloads require approval and license review. Human review decides whether voices and final audio are acceptable.
