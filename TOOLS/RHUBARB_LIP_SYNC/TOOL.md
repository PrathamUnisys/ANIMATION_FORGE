---
prompt_id: TOOL_RHUBARB_LIP_SYNC
version: 1.0.0
modified_date: 2026-11-09
description: Operational guide for Rhubarb Lip Sync in Animation Forge
dependencies: ["TOOLS_INDEX", "SCHEMAS/TOOL_PROFILE.schema.json"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Local trial verified on fight-audio.wav, Moho 14.4 match
---
# Tool Manual — Rhubarb Lip Sync

## Identity and purpose

Rhubarb Lip Sync auto-creates 2D mouth animation from voice recordings (game / cartoon / Moho mouth poses).

- **Tool ID:** `RHUBARB_LIP_SYNC`
- **Official site:** https://github.com/DanielSWolf/rhubarb-lip-sync
- **Local status:** `INSTALLED` — trial `LOCAL_TESTED` 2026-11-09 (see Verification history)

## Installation and location

- Portable: `Rhubarb-Lip-Sync-1.14.0-Windows.zip` → extract anywhere. Test copy: `C:\Users\sb291\AppData\Local\Temp\opencode\p4\rhubarb\extracted\Rhubarb-Lip-Sync-1.14.0-Windows\rhubarb.exe`
- Version check: `rhubarb.exe --version` → `Rhubarb Lip Sync version 1.14.0`

## Connection and configuration

- CLI only, no server/GPU. `rhubarb <input.wav> -o output.<fmt>`
- Formats: `tsv | xml | json | dat` (Moho/OpenToonz switch). Moho match: `-f dat --datFrameRate 24 --datUsePrestonBlair`
- Recognizers: `pocketSphinx` (English, default) | `phonetic` (non-English). Optional `-d dialog.txt` improves accuracy.

## How to use

1. Generate voice (Kokoro → WAV 24 kHz).
2. `rhubarb -r pocketSphinx -f json -o lip.json voice.wav` (~2.4 s for 3 s speech, tested)
3. For Moho: `rhubarb -r pocketSphinx -f dat --datFrameRate 24 --datUsePrestonBlair -o lip.dat voice.wav` → import switch in Moho 14.4.
4. Tweak `extendedShapes GHX` (6 basic A–F + 3 optional) for your mouth-sheet.

## Debugging

| Symptom | Diagnostic | Fix |
|---|---|---|
| `not recognized` | PATH | Use full `rhubarb.exe` path |
| Wrong mouths | recognizer wrong | try `phonetic` or add `-d dialog.txt` |
| Moho import fail | frame rate mismatch | set `--datFrameRate 24` to match Moho project |

## Limits and hardware

- CPU-only. No GPU/VRAM. Works on all hardware. `LOCAL_TESTED` saving ~30–60 min/shot vs manual mouth keys (projected).

## Verification history

| Date | Machine / OS | Version | Test | Result |
|---|---|---|---|---|
| 2026-11-09 | sb291 / Win11 | 1.14.0 | `fight-audio.wav` (529 KB) → JSON 13 cues + Moho `.dat` 118 B (Preston Blair AI/E/etc) | LOCAL_TESTED ✓ |
| 2026-11-09 | sb291 / Win11 | 1.14.0 | Kokoro `test_voice.wav` (4.57 s) → JSON 29 cues | LOCAL_TESTED ✓ |

## Removal / rollback
Delete the `Temp\opencode\p4\rhubarb\` folder. No system install.
