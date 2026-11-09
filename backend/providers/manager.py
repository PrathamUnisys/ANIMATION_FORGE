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


class WindowCredentialVault:
    """Windows Credential Manager-backed vault (CR_006 M2).

    Stores secrets under generic credentials named ``AnimationForge/<provider>``.
    Never logs secrets. Falls back to an explicit error if unavailable.
    """
    def __init__(self):
        if os.name != "nt":
            raise RuntimeError("WindowsCredentialVault requires Windows Credential Manager")

    def _cred_name(self, provider_id: str) -> str:
        return f"AnimationForge/{provider_id}"

    def set_credential(self, provider_id: str, secret_key: str) -> None:
        if not secret_key or not secret_key.strip():
            raise ValueError("Cannot store empty secret key")
        import ctypes
        from ctypes import wintypes
        advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
        class CREDENTIALW(ctypes.Structure):
            _fields_ = [
                ("Flags", wintypes.DWORD), ("Type", wintypes.DWORD),
                ("TargetName", wintypes.LPWSTR), ("Comment", wintypes.LPWSTR),
                ("LastWritten", wintypes.FILETIME), ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", wintypes.LPVOID), ("Persist", wintypes.DWORD),
                ("AttributeFlags", wintypes.DWORD), ("TargetAlias", wintypes.LPWSTR),
                ("UserName", wintypes.LPWSTR),
            ]
        advapi32.CredWriteW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_void_p]
        advapi32.CredWriteW.restype = wintypes.BOOL
        blob = secret_key.strip().encode("utf-16-le")
        buf = (ctypes.c_ubyte * len(blob)).from_buffer_copy(blob)
        cred = CREDENTIALW()
        cred.Type = 1  # CRED_TYPE_GENERIC
        cred.TargetName = self._cred_name(provider_id)
        cred.CredentialBlobSize = len(blob)
        cred.CredentialBlob = ctypes.cast(buf, ctypes.c_void_p)
        cred.Persist = 2  # CRED_PERSIST_LOCAL_MACHINE (survives restart on this machine)
        if not advapi32.CredWriteW(0, self._cred_name(provider_id), 0, ctypes.byref(cred)):
            raise ctypes.WinError(ctypes.get_last_error())

    def get_credential(self, provider_id: str) -> Optional[str]:
        import ctypes
        from ctypes import wintypes
        advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
        advapi32.CredReadW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.DWORD, wintypes.BOOL, ctypes.c_void_p]
        advapi32.CredReadW.restype = wintypes.BOOL
        advapi32.CredFree.argtypes = [ctypes.c_void_p]
        out = ctypes.c_void_p()
        if not advapi32.CredReadW(0, self._cred_name(provider_id), 1, False, ctypes.byref(out)):
            return None
        try:
            ptr = ctypes.cast(out, ctypes.POINTER(ctypes.c_void_p))
            # CREDENTIAL struct layout: use raw offsets via c_void_p array is fragile;
            # read CredentialBlobSize at offset 24 bytes (x64 Win) then blob pointer.
            # Safer: use ctypes structure with correct fields.
            class CREDENTIAL(ctypes.Structure):
                _fields_ = [
                    ("Flags", wintypes.DWORD), ("Type", wintypes.DWORD),
                    ("UserName", wintypes.LPWSTR), ("CredentialBlobSize", wintypes.DWORD),
                    ("CredentialBlob", wintypes.LPBYTE),
                ]
            # Actually marshal full CREDENTIAL type:
            class FULL_CREDENTIAL(ctypes.Structure):
                _fields_ = [
                    ("Flags", wintypes.DWORD), ("Type", wintypes.DWORD),
                    ("UserName", wintypes.LPWSTR), ("CredentialBlobSize", wintypes.DWORD),
                    ("CredentialBlob", wintypes.LPVOID), ("LastWritten", wintypes.FILETIME),
                    ("Persist", wintypes.DWORD), ("AttributeFlags", wintypes.DWORD),
                    ("TargetName", wintypes.LPWSTR), ("TargetAlias", wintypes.LPWSTR),
                    ("Comment", wintypes.LPWSTR),
                ]
            p = ctypes.cast(out, ctypes.POINTER(FULL_CREDENTIAL))
            size = p.contents.CredentialBlobSize
            if size <= 0 or not p.contents.CredentialBlob:
                return None
            blob = (ctypes.c_ubyte * size).from_address(p.contents.CredentialBlob)
            return bytes(blob).decode("utf-16-le", errors="ignore")
        finally:
            advapi32.CredFree(out)

    def has_credential(self, provider_id: str) -> bool:
        try:
            return bool(self.get_credential(provider_id))
        except Exception:
            return False


WindowsCredentialVault = WindowCredentialVault


class ProviderError(Exception):
    def __init__(self, category: str, detail: str):
        super().__init__(f"{category}: {detail}")
        self.category = category
        self.detail = redact_secrets(detail)


class DeterministicMockProvider:
    """Deterministic test provider (CR_006 M2). No network, seeded outputs.

    Outputs are labelled MOCK and are never presented as live generation.
    """
    def __init__(self, seed: int = 42):
        self.seed = seed

    def generate(self, model_id: str, prompt: str, temperature: float = 0.4, timeout_sec: int = 30) -> Dict[str, Any]:
        import time
        t0 = time.time()
        # Deterministic pseudo-content: extract requested JSON keys from prompt if present.
        content = f"[MOCK:{self.seed}:{model_id}] Deterministic response to prompt ({len(prompt)} chars, temp={temperature})."
        # Try to echo structured JSON if prompt asks for JSON
        if "JSON" in prompt:
            # Return a minimal valid JSON object with the model identity for test assertions.
            content = json.dumps({"mock": True, "model": model_id, "prompt_len": len(prompt)}, indent=2)
        return {
            "content": content,
            "provider_id": "DETERMINISTIC_MOCK",
            "model_id": model_id,
            "request_id": f"MOCK_{self.seed}_{hash(prompt) & 0xFFFFFF:06X}",
            "status": "MOCK",
            "latency_ms": int((time.time() - t0) * 1000),
            "usage": None,
            "usage_source": "MOCK_NO_USAGE",
        }


class OllamaOpenAICompatibleAdapter:
    """Real local LLM adapter via OpenAI-compatible HTTP (Ollama).

    Config: ``http://localhost:11434/v1`` (from opencode.jsonc ollama provider).
    Models: ``ornith:9b`` (primary), ``qwen3.5:4b`` (fallback).
    No API key required. Usage is recorded ONLY from provider-returned fields.
    """
    def __init__(self, base_url: str = "http://localhost:11434/v1"):
        self.base_url = base_url.rstrip("/")

    def generate(self, model_id: str, prompt: str, temperature: float = 0.4, timeout_sec: int = 120, max_retries: int = 2) -> Dict[str, Any]:
        import urllib.request, urllib.error, time
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        data = json.dumps(payload).encode("utf-8")
        last_exc: Optional[Exception] = None
        for attempt in range(max_retries + 1):
            t0 = time.time()
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                    body = resp.read().decode("utf-8")
                    raw = json.loads(body)
                latency_ms = int((time.time() - t0) * 1000)
                # OpenAI-compatible shape: choices[0].message.content
                try:
                    content = raw["choices"][0]["message"]["content"]
                except (KeyError, IndexError, TypeError):
                    raise ProviderError("INVALID_RESPONSE", f"Missing choices[0].message.content: {redact_secrets(body[:500])}")
                usage = raw.get("usage") or {}
                # Ollama also nests token counts inside usage (prompt_eval_count etc.)
                prompt_tokens = usage.get("prompt_tokens", usage.get("prompt_eval_count"))
                completion_tokens = usage.get("completion_tokens", usage.get("eval_count"))
                total_tokens = usage.get("total_tokens")
                if total_tokens is None and prompt_tokens is not None and completion_tokens is not None:
                    total_tokens = int(prompt_tokens) + int(completion_tokens)
                return {
                    "content": content,
                    "provider_id": "OLLAMA_OPENAI_COMPATIBLE",
                    "model_id": model_id,
                    "request_id": f"OLLAMA_{int(time.time()*1000)}",
                    "status": "LIVE",
                    "latency_ms": latency_ms,
                    "usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "raw": usage,
                    },
                    "usage_source": "PROVIDER_RETURNED" if usage else "PROVIDER_RETURNED_EMPTY",
                }
            except urllib.error.HTTPError as e:
                last_exc = e
                if e.code in (401, 403):
                    raise ProviderError("AUTHENTICATION", f"HTTP {e.code} {redact_secrets(e.read().decode('utf-8', errors='ignore')[:500])}")
                if e.code == 429:
                    raise ProviderError("RATE_LIMIT", f"HTTP 429 {redact_secrets(e.read().decode('utf-8', errors='ignore')[:500])}")
                if e.code >= 500 and attempt < max_retries:
                    continue
                raise ProviderError("HTTP_ERROR", f"HTTP {e.code} {redact_secrets(e.read().decode('utf-8', errors='ignore')[:500])}")
            except urllib.error.URLError as e:
                last_exc = e
                if attempt < max_retries:
                    time.sleep(0.5 * (2 ** attempt))
                    continue
                raise ProviderError("CONNECTION_ERROR", f"{e.reason}; is Ollama running? endpoint {url}")
            except TimeoutError as e:
                last_exc = e
                if attempt < max_retries:
                    time.sleep(0.5 * (2 ** attempt))
                    continue
                raise ProviderError("TIMEOUT", f"Timed out after {timeout_sec}s")
        raise ProviderError("UNKNOWN", str(last_exc) if last_exc else "Failed after retries")


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
            },
            "OLLAMA_OPENAI_COMPATIBLE": {
                "provider_id": "OLLAMA_OPENAI_COMPATIBLE",
                "category": "LLM",
                "requires_api_key": False,
                "models": ["ornith:9b", "qwen3.5:4b"],
                "cost_per_1k_tokens_usd": 0.0,
                "base_url": "http://localhost:11434/v1",
                "supports_temperature": True,
                "profile_path": "PROVIDERS/LLM/DEFAULT_LLM_PROFILE.md",
            },
            "DETERMINISTIC_MOCK": {
                "provider_id": "DETERMINISTIC_MOCK",
                "category": "LLM",
                "requires_api_key": False,
                "models": ["mock-42"],
                "cost_per_1k_tokens_usd": 0.0,
                "supports_temperature": True,
                "profile_path": "PROVIDERS/LLM/DEFAULT_LLM_PROFILE.md",
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

    # ---- CR_006 M2: Real live generation (no silent fallback) ----

    def generate_text(self, project_id: str, provider_id: str, model_id: str, prompt: str, temperature: float = 0.4, timeout_sec: int = 120) -> Dict[str, Any]:
        """Make a REAL provider request and record provenance.

        Providers: OLLAMA_OPENAI_COMPATIBLE (live local), DETERMINISTIC_MOCK (test).
        No fallback to fake output on failure — raises ProviderError.
        Persists a provider_requests row and provider_usage ONLY when the
        provider returns usage fields.
        """
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        request_id = f"REQ_{int(datetime.now(timezone.utc).timestamp()*1000)}_{project_id}"
        if provider_id not in self.providers:
            raise ValueError(f"Provider {provider_id} is not registered")
        spec = self.providers[provider_id]
        if model_id not in spec["models"]:
            raise ValueError(f"Model {model_id} is not registered for provider {provider_id}")
        if provider_id == "DETERMINISTIC_MOCK":
            result = DeterministicMockProvider().generate(model_id, prompt, temperature, timeout_sec)
        elif provider_id == "OLLAMA_OPENAI_COMPATIBLE":
            adapter = OllamaOpenAICompatibleAdapter(spec.get("base_url", "http://localhost:11434/v1"))
            result = adapter.generate(model_id, prompt, temperature, timeout_sec)
        elif provider_id == "OPENAI_COMPATIBLE_CLOUD":
            # Cloud path: requires vault credential; not yet wired to endpoint config.
            # Fail closed instead of simulating.
            raise ProviderError("NOT_CONFIGURED", "OPENAI_COMPATIBLE_CLOUD endpoint URL is not configured. Use OLLAMA_OPENAI_COMPATIBLE or DETERMINISTIC_MOCK.")
        else:
            raise ProviderError("UNSUPPORTED", f"Provider {provider_id} has no live adapter")
        result["request_id"] = request_id
        usage = result.get("usage") or {}
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT INTO provider_requests
                   (request_id, project_id, provider_id, model_id, status, latency_ms,
                    prompt_tokens, completion_tokens, total_tokens, usage_source, error_category, error_detail, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    request_id, project_id, result["provider_id"], result["model_id"], result["status"],
                    result.get("latency_ms"), usage.get("prompt_tokens"), usage.get("completion_tokens"),
                    usage.get("total_tokens"), result.get("usage_source", "UNKNOWN"), None, None, now
                )
            )
            # Record actual usage only when provider returned it (never invented)
            if usage.get("prompt_tokens") is not None or usage.get("completion_tokens") is not None:
                conn.execute(
                    """INSERT INTO provider_usage
                       (usage_id, project_id, provider_id, model_id, operation_type,
                        prompt_tokens, completion_tokens, units_consumed, recorded_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)""",
                    (
                        f"USE_{request_id}", project_id, result["provider_id"], result["model_id"], "LLM_GENERATION",
                        int(usage.get("prompt_tokens") or 0), int(usage.get("completion_tokens") or 0), now
                    )
                )
            conn.commit()
        return result

    def validate_structured(self, content: str, required_keys: List[str]) -> Dict[str, Any]:
        """Parse JSON response and validate required keys; raises ProviderError on failure."""
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ProviderError("INVALID_JSON", f"Response is not valid JSON: {redact_secrets(str(e))}")
        if not isinstance(data, dict):
            raise ProviderError("INVALID_JSON", "Response JSON must be an object")
        missing = [k for k in required_keys if k not in data]
        if missing:
            raise ProviderError("SCHEMA_VALIDATION", f"Missing required keys: {missing}")
        return data
