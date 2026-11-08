---
prompt_id: CORE_RULE_HIERARCHY
version: 1.0.0
modified_date: 2026-11-09
description: Strict 8-tier priority hierarchy for instruction resolution
dependencies: ["CORE_SYSTEM_CONSTITUTION"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Establish 8-level rule priority hierarchy
---
# RULE HIERARCHY

All instructions loaded into an agent context are resolved strictly in this descending priority order:
1. **Tier 1 — System Integrity & Security Requirements** (`CORE/SECURITY_POLICY.md`)
2. **Tier 2 — Global Production Constitution** (`CORE/SYSTEM_CONSTITUTION.md`, `CORE/HUMAN_APPROVAL_POLICY.md`)
3. **Tier 3 — Project-Level Rules** (`PROJECTS/<ID>/PROJECT_BRIEF/PROJECT_RULES.md`)
4. **Tier 4 — Series Bible** (`MEMORY/SERIES/` & `PROJECTS/<ID>/STORY_BIBLE/`)
5. **Tier 5 — Department Instructions** (`DEPARTMENTS/<DEPT>/DEPARTMENT_RULES.md`)
6. **Tier 6 — Agent-Specific Instructions** (`AGENTS/<AGENT>/INSTRUCTION.md`)
7. **Tier 7 — Provider-Specific Instructions** (`PROVIDERS/<TYPE>/<PROVIDER>.md`)
8. **Tier 8 — Individual Task Instructions** (Runtime task payload)

## Conflict Resolution Protocol
- Lower-tier instructions must **never** override higher-tier rules.
- If the Rule Loader detects a contradiction (e.g., a task instruction requesting `auto_approve=true`, overwriting an approved file, or bypassing R&D toolchain lock), execution immediately halts with a `RuleConflictError` and logs an audit event.
