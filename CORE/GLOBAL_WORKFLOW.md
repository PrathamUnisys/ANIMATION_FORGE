---
prompt_id: CORE_GLOBAL_WORKFLOW
version: 1.0.0
modified_date: 2026-11-09
description: End-to-end 17-stage production journey and gate enforcement
dependencies: ["CORE_SYSTEM_CONSTITUTION", "CORE_HUMAN_APPROVAL_POLICY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Define mandatory 17-stage production pipeline
---
# GLOBAL PRODUCTION WORKFLOW

Every project progresses through these 17 sequential stages:
1. `USER_STORY_IDEA`
2. `STORY_ANALYSIS`
3. `SCRIPT_DEVELOPMENT` (13 structured passes)
4. `SCREENPLAY_APPROVAL` (**Mandatory Human Gate #1**)
5. `PRODUCTION_REQUIREMENT_ANALYSIS`
6. `ONLINE_TOOL_RESEARCH_AND_RND`
7. `TOOL_COMPARISON`
8. `PROOF_OF_CONCEPT` (Requires explicit cost/download authorization)
9. `HUMAN_TOOLCHAIN_APPROVAL` (**Mandatory Human Gate #2** -> generates `APPROVED_TOOLCHAIN.json`)
10. `PRODUCTION_PLANNING`
11. `AUDIO_AND_VISUAL_PRODUCTION` (Characters, Environments, Dialogue/TTS)
12. `STORYBOARD_AND_ANIMATIC` (**Mandatory Human Gate #3: Animatic Gate**)
13. `ANIMATION`
14. `POST_PRODUCTION`
15. `QUALITY_CONTROL` (Automated technical QC pass)
16. `HUMAN_FINAL_APPROVAL` (**Mandatory Human Gate #4**)
17. `COMPLETED_PRODUCTION_PACKAGE`
