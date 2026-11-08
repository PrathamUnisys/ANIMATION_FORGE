---
prompt_id: DEPT_POST_PRODUCTION
version: 1.1.0
date: 2026-11-09
modified_date: 2026-11-09
description: Editorial assembly, finishing, delivery, and review procedure for post-production
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE_HUMAN_APPROVAL_POLICY", "CORE_OUTPUT_CONTRACTS", "DEPT_ANIMATION", "DEPT_AUDIO"]
change_history:
  - version: 1.1.0
    date: 2026-11-09
    summary: Establish post-production intake, conform, technical checks, and handoff
---
# POST-PRODUCTION DEPARTMENT RULES

## Entry requirements and inputs
- Accept only identified, versioned shot/animation and audio sources with their approval/QC states, edit intent, runtime, frame rate, resolution, language, subtitle requirements, and target delivery specifications.
- Confirm source files exist and can be read before conforming. Track missing media, duration differences, sync assumptions, and whether a source is only a preview or a final candidate.
- Use `SCHEMAS/ASSET.schema.json` for registry entries and `SCHEMAS/APPROVAL.schema.json` for approval records where structured records are used. No dedicated post-production report schema exists.

## Department workflow
1. Build an edit/conform plan from approved material; identify shot order, transitions, audio, subtitles/captions, titles, and any proposed changes.
2. Preserve source identifiers and revisions. Use an available configured editing/export capability only; a plan or timeline description is not evidence that a rendered master was exported.
3. Inspect the assembled sequence for continuity, picture/audio sync, runtime, frame rate, resolution, subtitle coverage, black/missing frames, clipping, and file integrity where those checks can actually be performed.
4. Prepare a `PRODUCTION_REPORT` and, when applicable, a `QC_REPORT` distinguishing measured results from unchecked items and creative notes from technical findings.
5. Fix only the affected edit element or source task; document changes and re-run impacted checks.

## Outputs and dependencies
- Deliver versioned assembly/export references if actually created, a `PRODUCTION_REPORT`, a `QC_REPORT`, and asset/provenance updates. Clearly label previews, intermediates, and final candidates.
- Animation supplies picture; Audio supplies dialogue/music/effects; Storyboard/Previs provide intended timing and continuity; Production supplies delivery constraints.

## Gates, exceptions, and handoff
- Technical QC may report pass, defect, or manual-inspection need; it never grants creative approval. Final delivery requires the designated human approval gate.
- Escalate missing/ambiguous sources, unsupported codecs, absent render/export capability, unresolved sync or rights concerns, spec conflicts, or failed checks. State what remains unverified; never invent QC measurements or claim a final master exists without confirming it.
- Retain approved source versions and record lineage for every assembly revision. Do not overwrite or silently substitute approved content.
