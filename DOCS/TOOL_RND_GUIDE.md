# Mandatory Per-Project Tool R&D Guide

After screenplay approval, the `ProductionRndEngine` executes the 20-step R&D workflow:
1. Extracts technical requirements from the approved script.
2. Profiles workstation CPU/RAM/VRAM.
3. Evaluates candidate tools across 11 dimensions: `quality`, `reliability`, `automation`, `cost`, `hardware`, `consistency`, `performance`, `compatibility`, `licensing`, `maintainability`, `reusability`.
4. Enforces strict tool states (`DISCOVERED -> RESEARCHED -> TESTED -> RECOMMENDED -> APPROVED / REJECTED / RETIRED`).
5. Generates `PROJECT_RND_REPORT.md` with verified source URLs and locks `APPROVED_TOOLCHAIN.json` upon human approval.
