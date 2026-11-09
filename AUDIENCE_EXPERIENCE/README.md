---
prompt_id: AUDIENCE_EXPERIENCE_INDEX
version: 0.2.0
modified_date: 2026-11-09
description: Research-derived draft workspace for audience-focused storytelling, packaging, production and analytics
---

# Audience Experience

## Purpose
Help Animation Forge plan and review the experience promised to viewers across story development, screenplay, animation, audio, packaging and post-publication learning. This is a cross-cutting creative layer; it does not replace genre, series format, channel style, story-source governance or human approval.

## Status
**DESIGN PACK DRAFT — NOT YET AN ACTIVE RUNTIME FEATURE.**

This branch contains a design pack, playbooks, 30 hook patterns, screenplay templates, JSON contracts and an illustrative pilot example. No database, API, frontend, production agent, global output contract or active workflow has been changed. Do not claim these features are executable until implementation is verified.

## Research basis
Based on the Library report **Executive Summary(1)** covering screenplay structures, hooks, retention mapping, mystery/horror checklists, visual/audio storytelling, packaging, analytics and QA. See `RESEARCH_FINDINGS/RESEARCH_REPORT_SYNTHESIS.md` for interpretation and limitations.

## Core artifacts
- `DESIGN_PACK.md`: consolidated module specification.
- `HOOK_LIBRARY/HOOK_LIBRARY.json`: 30 original patterns across five categories.
- `SCRIPT_FORMATS/ANIMATED_EPISODE.md`: 6–10 minute episode template.
- `SCRIPT_FORMATS/YOUTUBE_SHORT.md`: 30–60 second Short template.
- `SCHEMAS/`: Audience Plan, Retention Map, Packaging Options and Creative Review contracts.
- `PLAYBOOKS/`: draft operating guidance.
- `EXAMPLES/`: illustrative pilot records, not approved canon.

## Evidence and rule discipline
Preserve source, claim, context, limitations and evidence grade. Distinguish platform documentation, empirical research, practitioner convention and project hypothesis. Do not infer private retention from public views. Do not turn timing ranges, numerical QA scores, cut frequencies or title formulas into universal rules. Activate findings only through a reviewed change.

## Intended flow
Audience promise → hook options → story outline → screenplay + Retention Map → creative review → production breakdown → storyboard/camera/audio → packaging selection → publication → analytics snapshot → experiment → reviewed playbook update.

## Architecture boundaries
Genre governs narrative conventions. Series format governs episode relationships. Channel style governs brand/presentation. Audience Experience supplies cross-cutting guidance. Rights remain separate. Creative review is distinct from technical QC and human approval. Existing screenplay schemas and output contracts remain authoritative until approved changes are applied.

## Next boundary
A governed change request must cover schema, agent, context-assembly, persistence, API, frontend, migration, test and rollback changes. This draft pack alone does not implement them.
