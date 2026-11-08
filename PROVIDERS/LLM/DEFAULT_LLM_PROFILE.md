---
prompt_id: PROVIDER_LLM_DEFAULT
version: 1.1.0
modified_date: 2026-11-09
description: LLM provider metadata profile with implemented behavior and unimplemented adapter distinctions.
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial provider profile
  - version: 1.1.0
    date: 2026-11-09
    summary: Distinguished local metadata/fallback from live model execution
---
# PROVIDER PROFILE: PROVIDER_LLM_DEFAULT

## Capability status
`ProviderManager` registers `LOCAL_DETERMINISTIC_STUDIO` and `OPENAI_COMPATIBLE_CLOUD` metadata and has a fallback when a cloud credential is absent (`backend/providers/manager.py`). Its `invoke_llm` method records usage/cost metadata and returns provider/model/token fields; it does not call an LLM endpoint or return generated text. Anthropic, Gemini, and Ollama are not registered by the inspected manager. These profiles/endpoints are not live integrations.

The in-memory credential vault shown in the manager is not evidence of OS Credential Manager persistence. Do not enter real credentials into demo flows or treat metadata fallback as a model invocation.

## Provider verification
Before adoption, verify official API/model docs, exact endpoint and model, supported parameters, pricing and quotas, retention/training policy, region, license, and current deprecation status. Mark official client vs community wrapper and experimental capabilities. Never assume OpenAI-compatible means equivalent parameters or behavior.

Test a minimal approved request through a real adapter with synthetic data; record request/response evidence, version, latency, errors, and actual billed units. Obtain explicit human approval for external data transfer and paid use. Avoid logging prompts/secrets containing sensitive material.
