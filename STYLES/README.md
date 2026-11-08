---
prompt_id: STYLES_INDEX
version: 1.0.0
modified_date: 2026-11-09
description: Registry for separate YouTube channel and publishing-brand style guides
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE_RULE_HIERARCHY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Establish independent versioned style guides for each channel
---
# Channel Style Guide Library

## Purpose

`STYLES/` stores the creative and publishing identity of each YouTube channel or content brand. Each channel gets its own folder:

`STYLES/<CHANNEL_ID>/STYLE_GUIDE.md`

Do not create one global style guide and apply it to every channel. One production system may support multiple channels with different audiences, content formats, pacing and brand identity.

## What a channel guide controls

A channel guide defines:
- Channel positioning, audience and promise.
- Content pillars and recurring episode/series formats.
- Target runtime, opening hook, segment structure and ending pattern.
- Narration, dialogue, humor density, tone and language.
- Visual identity: palette, composition, typography, camera language and animation feel.
- Sound identity, music direction and sound effects.
- Thumbnail/title/description conventions and calls to action.
- Content boundaries, accessibility and brand consistency.
- Links to approved reusable channel-brand assets in `LIBRARY/ASSET_INDEX.json`.

## What it does not control

A style guide is not a genre, screenplay template or story bible. It must not rewrite established character/world canon, override project restrictions, dictate technical tools, or force the same formula into every story.

Do not copy another creator's distinctive scripts, characters, logos or exact presentation. Convert references into high-level original traits and record which parts are inspiration versus approved channel identity.

## Selection and versioning

A project may select one channel style guide using `channel_style_id`. Record its version in screenplay-generation provenance. Channel-neutral work may leave this unset and use project direction alone.

Use `TEMPLATES/CHANNEL_STYLE_GUIDE_TEMPLATE.md` to create a new channel guide. Keep each channel's approved logos, fonts, title cards, sound marks and other reusable assets referenced by stable asset IDs rather than embedded in the guide.

## Available channels

The registry is `CHANNELS.json`. It is intentionally empty until a real channel identity and owner-approved guide exist. Do not invent a channel brand to make the registry look populated.
