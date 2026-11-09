---
prompt_id: TOOL_KOKORO_TTS
version: 1.0.0
modified_date: 2026-11-09
description: Operational guide for Kokoro TTS in Animation Forge
dependencies: ["TOOLS_INDEX", "SCHEMAS/TOOL_PROFILE.schema.json"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Local trial verified, CPU-only, offline voice generation
---
# Tool Manual — Kokoro TTS

## Identity and purpose

Kokoro-82M is an open-weight TTS model (StyleTTS2, 82 M params, Apache-2.0) — local voice generation for dialogue/character voices.

- **Tool ID:** `KOKORO_TTS`
- **Official:** https://github.com/hexgrad/kokoro / https://huggingface.co/hexgrad/Kokoro-82M (v1.0 2025-01-27 SHA256 `496dba11`)
- **Local status:** `INSTALLED` — trial `LOCAL_TESTED` 2026-11-09

## Installation and location

- Isolated venv: `D:\Work\ANIMATION_FORGE\.venv-kokoro-test\` (Python 3.12.3)
- `pip install kokoro soundfile` → kokoro 0.9.4, torch 2.15.0 (CPU), transformers 5.22.2, misaki, en-core-web-sm
- Model cache: HF (`hexgrad/Kokoro-82M` ~330 MB) → `D:` cache to avoid C: pressure.

## Connection and configuration

```python
from kokoro import KPipeline
import soundfile as sf
pipe = KPipeline(lang_code='a')
gen = pipe("Hello...", voice='af_heart')
for _,_,audio in gen: sf.write("out.wav", audio, 24000)
```
- Voices: `af_heart` etc. Sample rate 24 kHz, WAV PCM_16.
- Offline: no API key needed. Keep venv isolated — don’t install into system Python.

## How to use

1. Write script lines, run pipeline voice `af_foot` per character for consistency.
2. Save WAV → feed Rhubarb (see RHUBARB_LIP_SYNC) → Moho .dat.
3. Add dialogue prefix per character for identity.

## Resource profile (12 GB RAM / 8 GB VRAM)

- CPU-only torch (126 MB wheel), ~0 MB VRAM, RAM ~2–3 GB with model loaded.
- Time: first run 65 s (model download), steady 8.27 s for 4.6 s audio (1.8× realtime, CPU).

## Debugging

| Symptom | Diagnostic | Fix |
|---|---|---|
| `ModuleNotFoundError: soundfile` | venv not active | use `.venv-kokoro-test\Scripts\python.exe` |
| Symlink warning (Windows) | HF cache | set `HF_HOME` to D:; ignore or Developer Mode |
| Slow | CPU torch | expected; GPU torch optional but not needed |

## Limits

- English only in this build (`lang_code='a'`). Distant from institutional TTS providers (ElevenLabs) — voice cloning needs separate review.

## Verification history

| Date | Machine / OS | Version | Test | Result |
|---|---|---|---|---|
| 2026-11-09 | sb291 / Win11 | kokoro 0.9.4 / model v1.0 | “Hello, this is a test…” → `test_voice.wav` 219 KB, 24 kHz, 4.575 s | LOCAL_TESTED ✓ |
| 2026-11-09 | sb291 / Win11 | same | same WAV → Rhubarb 29 cues | LOCAL_TESTED ✓ |

## Removal / rollback
Delete `D:\Work\ANIMATION_FORGE\.venv-kokoro-test\` (.gitignored). Model cache on D:. No global install.
