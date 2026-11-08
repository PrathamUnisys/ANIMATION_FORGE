---
prompt_id: TEMPLATE_DOC_VOICE_PROFILE
version: 1.0.0
date: 2026-11-09
modified_date: 2026-11-09
description: Reusable stable voice identity and performance-reference template
dependencies: ["TEMPLATE_DOC_CHARACTER_BIBLE", "SCHEMAS/AUDIO.schema.json", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial reusable voice profile template
document_type: reusable_document_template
---
# TEMPLATE — VOICE PROFILE

> Reusable descriptive reference, not an executable agent prompt, voice clone, recording, or provider configuration. Do not include sensitive biometric data or claim a voice asset exists unless it does.

## Identity and approval
- **Project / character / profile ID**: `[IDS]`
- **Profile version / date / owner**: `[DETAIL]`
- **Character-bible revision**: `[REFERENCE]`
- **Status / human reviewer / decision date**: `[PROPOSED / AWAITING HUMAN REVIEW / APPROVED / REVISION REQUESTED / REJECTED]`
- **Rights, consent, and permitted use**: `[DOCUMENTED BASIS OR UNRESOLVED; DO NOT ASSUME]`

## Stable voice characteristics
- **Language, locale, accent**: `[DETAIL]`
- **Perceived range / texture / resonance**: `[NON-IDENTIFYING DESCRIPTORS]`
- **Pitch and pace range**: `[QUALITATIVE OR MEASURED BASIS]`
- **Articulation / breath / vocal mannerisms**: `[DETAIL]`
- **Pronunciation references**: `[AUDIO_SCRIPT DICTIONARY OR SOURCE]`
- **Consistency anchors**: `[FEATURES THAT SHOULD REMAIN STABLE]`
- **Avoid / boundaries**: `[UNWANTED DELIVERY OR CONTENT]`

## Performance direction (scene-specific, not identity)
| Scene / line | Emotion and intention | Energy / pacing | Pause or emphasis | Source revision |
|---|---|---|---|---|
| `[ID]` | `[DIRECTION]` | `[DETAIL]` | `[DETAIL]` | `[REFERENCE]` |

## Asset and configuration references
- **Approved sample/asset IDs and locations**: `[LINKS OR NONE]`
- **Provider/model/configuration**: `[ONLY IF ACTUALLY CONFIGURED; OTHERWISE NOT SELECTED]`
- **Audio requirements / output expectations**: `[SEE SCHEMAS/AUDIO.schema.json FOR PACKAGE FIELDS]`
- **Unknowns / limitations**: `[DETAIL]`

No dedicated voice-profile schema exists. Human approval is required for creative voice choices; technical audio checks are not approval.
