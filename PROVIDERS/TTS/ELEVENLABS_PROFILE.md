---
prompt_id: PROVIDER_TTS_ELEVENLABS
version: 1.1.0
modified_date: 2026-11-09
description: ElevenLabs TTS candidate metadata and checks; parameter availability requires current source verification.
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial provider profile
  - version: 1.1.0
    date: 2026-11-09
    summary: Distinguished registered metadata from live TTS execution and added evidence gates
---
# PROVIDER PROFILE: PROVIDER_TTS_ELEVENLABS

## Capability status
`ProviderManager` registers `ELEVENLABS_TTS` metadata, example model identifiers (`eleven_v3`, `eleven_multilingual_v2`), allowed setting names, and a per-character cost value. The inspected manager does not call ElevenLabs or synthesize speech (`backend/providers/manager.py`). Production code can assemble an example request payload but generates a simple tone WAV instead of provider speech (`backend/departments/production_studios.py`). Listed values are implementation metadata, not current API/pricing verification. `pronunciation_dictionary_locators` appears in the prior profile text but is not in the manager's allowed settings.

## Before use
Check current official model/API documentation for exact model IDs, supported parameters/ranges, pronunciation features, quotas, plan pricing, data retention and commercial terms. Record retrieval date and plan/region. Treat community SDKs/wrappers separately from the official service. Do not rely on stale costs or parameter names.

Require approved dialogue and explicit human authorization for paid calls and external transfer. Never add unspoken stage directions to raw dialogue. Voice cloning/reference use requires documented rights and speaker consent. Test with synthetic or approved text, capture actual settings/results, and have a human review pronunciation, delivery, identity, rights, and final audio before acceptance.
