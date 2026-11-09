# P4 Trial Log (2026-11-09)

## Trial 1 — Rhubarb Lip Sync 1.14.0 — LOCAL_TESTED ✓
- Source: https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.14.0/Rhubarb-Lip-Sync-1.14.0-Windows.zip (GitHub API tag v1.14.0, 87 MB zip)
- Backup: not needed (portable, no install). Isolated: `C:\Users\sb291\AppData\Local\Temp\opencode\p4\rhubarb\extracted\`
- Command 1: `rhubarb.exe --version` → `Rhubarb Lip Sync version 1.14.0`
- Test task: `D:\Work\Rigby2D-Projects\fight-audio.wav` (529,278 bytes) → `rhubarb -r pocketSphinx -f json -o fight-audio.json fight-audio.wav`
- Time: `Measure-Command` TotalSeconds **2.42** for 3.00s audio
- Output: `fight-audio.json` metadata duration 3.00, 13 mouthCues (X,D,C,B,X,D,C,B,X,D,C,B,X) — matches pronunciation of fight call sequence.
- Downstream: `-f dat --datFrameRate 24 --datUsePrestonBlair` → `fight-audio.dat` 118 bytes, Moho switch: frames 1 rest, 5 AI, 9 E, 10 etc, 15 rest… Preston Blair mapping verified (D=AI, C=E, B=etc, X=rest).
- Quality/failure: no failure, deterministic JSON. CPU-only, no GPU.
- Rollback: delete `C:\Users\sb291\AppData\Local\Temp\opencode\p4\rhubarb\` (zip + extracted). No system change.
- Verdict: **LOCAL_TESTED — production ready for TTS→Moho lip-sync.** Projected saving: manual mouth keys 30–60 min/shot vs 2.4s auto + cleanup.

## Trial 2 — Kokoro-82M 0.9.4 (hexgrad) — LOCAL_TESTED ✓
- Source: https://huggingface.co/hexgrad/Kokoro-82M + https://github.com/hexgrad/kokoro (Apache-2.0, StyleTTS2, 82M params, v1.0 2025-01-27 SHA256 496dba11)
- Isolated env: Python 3.12.3 venv `D:\Work\ANIMATION_FORGE\.venv-kokoro-test\`, HF cache → D: (`hf_cache`/`D:\hf_cache`), `pip install kokoro soundfile` → kokoro 0.9.4, torch 2.15.0 (CPU 126 MB wheel), transformers 5.22.2, misaki, espeakng-loader; auto-installed `en-core-web-sm` 3.8.0 (12.8 MB)
- Test task: `KPipeline(lang_code='a')(“Hello, this is a test…”, voice='af_heart')`
- Time: first run **65.32 s** (model download ~330 MB), second run **8.27 s** for 4.575 s audio (CPU torch, 1.8× realtime, no VRAM)
- Output: `D:\Work\ANIMATION_FORGE\.venv-kokoro-test\test_voice.wav` — 219,644 bytes, 24,000 Hz, 1 ch, 4.575 s PCM_16
- Downstream chain test: same WAV → Rhubarb pocketSphinx JSON → 29 cues (X,C,E,F,B,C,B,G,E,C,A…) duration 4.57 — proves TTS→lip-sync→Moho chain end-to-end.
- Quality/failure: no failure; warnings only (HF unauthenticated, symlinks, weight_norm deprecated, LSTM dropout). CPU torch = no GPU required.
- Rollback: delete `D:\Work\ANIMATION_FORGE\.venv-kokoro-test\` (venv + cached model). No system Python touched.
- Verdict: **LOCAL_TESTED — offline voice generation works on 4 GB VRAM laptop.** Fills #9 gap vs ElevenLabs (paid) + Qwen node missing model.

## Pending
- Trials 3–4 ComfyUI nodes (not started) — requires ComfyUI backup before custom_nodes modify
- Trial 5 asset indexer script (not started)
