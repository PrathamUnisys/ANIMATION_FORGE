---
prompt_id: TEMPLATE_DOC_AUDIO_SCRIPT
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable dialogue, performance direction, pronunciation, and timing template
dependencies: ["TEMPLATE_DOC_SCREENPLAY", "TEMPLATE_DOC_VOICE_PROFILE", "SCHEMAS/AUDIO.schema.json"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable audio script template
document_type: reusable_document_template
---
# TEMPLATE — AUDIO SCRIPT

> Reusable production document, not an executable agent prompt and not a recording or synthesis result. Copy one line row per spoken line; retain approved screenplay wording exactly.

## Package record
- **Project / audio package / scene ID**: `[PROJECT; PACKAGE_ID; SCENE_ID]`
- **Script ID and revision**: `[APPROVED SCRIPT REFERENCE]`
- **Language / locale / owner / revision**: `[DETAIL]`
- **Status / human review record**: `[STATE; REVIEWER; DATE; COMMENTS]`

## Pronunciation dictionary
| Term | Pronunciation (IPA or readable guide) | Language | Notes / source |
|---|---|---|---|
| `[TERM]` | `[PRONUNCIATION]` | `[LOCALE]` | `[SOURCE / CONFIDENCE]` |

## Dialogue lines
| Line ID | Character ID | Exact spoken text | Emotion / performance direction | Pause before / after (ms) | Timing / comedy notes | Voice-profile ref |
|---|---|---|---|---|---|---|
| `[LINE_ID]` | `[CHAR_ID]` | `[VERBATIM APPROVED TEXT]` | `[DIRECTION]` | `[N / N]` | `[NOTES]` | `[PROFILE REVISION]` |

## Technical and generation notes
- **Required output format / sample rate / channel layout**: `[REQUIREMENTS, NOT MEASURED RESULTS]`
- **Provider / model / payload**: `[ONLY IF SELECTED AND ACTUALLY CONFIGURED; OTHERWISE NOT SELECTED]`
- **Audio-file path / asset ID per line**: `[PATH/ID OR NOT CREATED]`
- **Dependencies**: `[PICTURE / TIMING / PRONUNCIATION / LICENSE]`

Map structured packages to `SCHEMAS/AUDIO.schema.json`; required line fields include `line_id`, `character_id`, `spoken_text`, `emotion_direction`, `pause_before_ms`, `pause_after_ms`, and `provider_tts_payload`. Use an empty object only when a payload is intentionally absent and the consumer accepts it; otherwise mark the line blocked rather than inventing one.

## Line review and handoff
| Line ID | Completeness / pronunciation / intelligibility | Technical check and measured result | Sync reference | Issue / correction |
|---|---|---|---|---|
| `[LINE_ID]` | `[FINDING]` | `[CHECK OR NOT RUN]` | `[SHOT / TIME / NOT AVAILABLE]` | `[ACTION]` |

Technical checks do not approve creative performance. Record the human decision separately; revise only affected lines and preserve approved prior versions.
