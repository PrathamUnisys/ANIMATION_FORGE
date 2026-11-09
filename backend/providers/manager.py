import os
import re
import json
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.database import DatabaseManager


class MissingCredentialError(Exception):
    """Raised when a cloud provider requires an API key that is not configured in secure OS storage."""


SECRET_PATTERNS = [
    re.compile(r"(sk-[a-zA-Z0-9_-]{12,})"),
    re.compile(r"(xi-[a-zA-Z0-9_-]{12,})"),
    re.compile(r"(AIza[0-9A-Za-z_-]{20,})"),
    re.compile(r"(Bearer\s+[A-Za-z0-9._~+/-]+=*)"),
]


def redact_secrets(text: str) -> str:
    if not text:
        return text
    redacted = text
    for pat in SECRET_PATTERNS:
        redacted = pat.sub("[REDACTED_SECRET]", redacted)
    return redacted


class SecureCredentialVault:
    """In-memory test stub only; this is not a persistent or OS-backed secure vault.

    Do not use this implementation for production credentials. A platform-backed
    credential-store adapter must replace it before live provider invocation.
    """
    def __init__(self):
        self._memory_vault: Dict[str, str] = {}

    def set_credential(self, provider_id: str, secret_key: str) -> None:
        if not secret_key or not secret_key.strip():
            raise ValueError("Cannot store empty secret key")
        self._memory_vault[provider_id] = secret_key.strip()

    def get_credential(self, provider_id: str) -> Optional[str]:
        return self._memory_vault.get(provider_id)

    def has_credential(self, provider_id: str) -> bool:
        return provider_id in self._memory_vault and bool(self._memory_vault[provider_id])


class ProviderManager:
    def __init__(self, db: DatabaseManager, vault: Optional[SecureCredentialVault] = None):
        self.db = db
        self.vault = vault or SecureCredentialVault()
        self.providers: Dict[str, Dict[str, Any]] = {
            "LOCAL_DETERMINISTIC_STUDIO": {
                "provider_id": "LOCAL_DETERMINISTIC_STUDIO",
                "category": "LLM",
                "requires_api_key": False,
                "models": ["forge-story-reasoner-local-v1", "forge-breakdown-fast-v1"],
                "cost_per_1k_tokens_usd": 0.0,
                "supports_temperature": True,
                "profile_path": "PROVIDERS/LLM/DEFAULT_LLM_PROFILE.md",
            },
            "OPENAI_COMPATIBLE_CLOUD": {
                "provider_id": "OPENAI_COMPATIBLE_CLOUD",
                "category": "LLM",
                "requires_api_key": True,
                "models": ["gpt-4o", "gpt-4o-mini"],
                "cost_per_1k_tokens_usd": 0.005,
                "supports_temperature": True,
                "profile_path": "PROVIDERS/LLM/DEFAULT_LLM_PROFILE.md",
            },
            "ELEVENLABS_TTS": {
                "provider_id": "ELEVENLABS_TTS",
                "category": "TTS",
                "requires_api_key": True,
                "models": ["eleven_v3", "eleven_multilingual_v2"],
                "cost_per_1k_chars_usd": 0.18,
                "allowed_settings": {"stability", "similarity_boost", "style", "speed", "use_speaker_boost"},
                "profile_path": "PROVIDERS/TTS/ELEVENLABS_PROFILE.md",
            },
            "LOCAL_KOKORO_TTS": {
                "provider_id": "LOCAL_KOKORO_TTS",
                "category": "TTS",
                "requires_api_key": False,
                "models": ["kokoro-82m-v1.0"],
                "cost_per_1k_chars_usd": 0.0,
                "allowed_settings": {"voice_preset", "speed", "pitch_shift"},
                "profile_path": "PROVIDERS/TTS/LOCAL_KOKORO_XTTS_PROFILE.md",
            },
            "COMFYUI_LOCAL_GRAPH": {
                "provider_id": "COMFYUI_LOCAL_GRAPH",
                "category": "IMAGE_VIDEO",
                "requires_api_key": False,
                "models": ["flux1-dev-fp8.safetensors", "wan2.1-i2v-14b-480p.safetensors"],
                "cost_per_run_usd": 0.0,
                "profile_path": "PROVIDERS/IMAGE/COMFYUI_FLUX_SDXL_PROFILE.md",
            }
        }

    def validate_provider_settings(self, provider_id: str, settings: Dict[str, Any]) -> None:
        if provider_id not in self.providers:
            raise ValueError(f"Unknown provider: {provider_id}")
        spec = self.providers[provider_id]
        if "allowed_settings" in spec:
            unsupported = set(settings.keys()) - spec["allowed_settings"]
            if unsupported:
                raise ValueError(f"Unsupported provider settings for {provider_id}: {sorted(unsupported)}")

    def invoke_llm(
        self,
        project_id: str,
        provider_id: str,
        model_id: str,
        prompt: str,
        temperature: float = 0.4,
        fallback_provider_id: Optional[str] = "LOCAL_DETERMINISTIC_STUDIO"
    ) -> Dict[str, Any]:
        """Return an explicitly simulated estimate; this method does not call a provider.

        The old implementation wrote invented token counts and estimated costs into
        tables that represented actual usage. Until a real provider adapter exists,
        keep estimates out of actual usage and cost records.
        """
        if provider_id not in self.providers:
            raise ValueError(f"Provider {provider_id} is not registered")
        requested_provider_id = provider_id
        spec = self.providers[provider_id]
        if model_id not in spec["models"]:
            raise ValueError(f"Model {model_id} is not registered for provider {provider_id}")

        if spec["requires_api_key"] and not self.vault.has_credential(provider_id):
            if fallback_provider_id and fallback_provider_id in self.providers:
                provider_id = fallback_provider_id
                spec = self.providers[provider_id]
                model_id = spec["models"][0]
            else:
                raise MissingCredentialError(f"Missing credential for provider '{provider_id}'.")

        estimated_prompt_tokens = max(1, len(prompt.split()))
        return {
            "status": "SIMULATED",
            "requested_provider_id": requested_provider_id,
            "provider_id": provider_id,
            "model_id": model_id,
            "estimated_prompt_tokens": estimated_prompt_tokens,
            "estimated_completion_tokens": None,
            "estimated_cost_usd": None,
            "usage_recorded": False,
            "warning": "No provider request was made. No token usage or cost has been recorded."
        }
