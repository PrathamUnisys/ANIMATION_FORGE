# Task Backlog

**Updated:** 2026-11-10. Status applies only to implementation within the isolated module; it does not imply framework-wide or production approval.

| ID | Task | Dependency | Files | Acceptance/evidence | Priority | Complexity | State |
|---|---|---|---|---|---|---|---|
| SCF-001 | Audit existing scripts, workflow, governance and ten-script experiment | None | `EXISTING_SCRIPT_AUDIT.md` | Ten original/revised scripts, reviews, history and live capabilities read | P0 | M | DONE |
| SCF-002 | Research storytelling, platform and evidence practices | SCF-001 | `RESEARCH_REPORT.md` | Source links, evidence types and limits documented | P0 | M | DONE |
| SCF-003 | Define adaptable methodology, quality criteria and boundaries | SCF-001–002 | Methodology, proposal, technical decisions | Topic-specific structures; separate creative/fact/human gates | P0 | M | DONE |
| SCF-004 | Create design docs, backlog and implementation sequence | SCF-003 | Guides, plan, backlog, progress | Initial design/docs existed before module code | P0 | M | DONE |
| SCF-005 | Add isolated project workspace, templates and data schemas | SCF-004 | `workspace.py`, `schemas/`, `templates/` | Workspace initialization and five JSON schemas validated | P0 | L | DONE (MVP) |
| SCF-006 | Preserve registered revisions and verify integrity | SCF-005 | `workspace.py`, `manifest` schema | Hash check, no overwrite and path containment tests | P0 | M | DONE (MVP) |
| SCF-007 | Track claims, source IDs, locators and uncertainty | SCF-005 | claim/source schemas, templates, validator | Missing claim/source references reported; no truth guarantee | P0 | L | DONE (reference checks only) |
| SCF-008 | Provide research/story discovery and architecture methods | SCF-003 | `prompts/01-03`, methodology docs | Prompt assets define adaptive routes; no forced act count | P0 | M | DONE (prompt assets only) |
| SCF-009 | Provide accessible narration drafting workflow | SCF-008 | `prompts/04`, script template | Spoken words, visuals, claim markers and simple-English rule documented | P0 | M | DONE (prompt assets only) |
| SCF-010 | Separate independent creative review and fact-check | SCF-007, 009 | `prompts/05-06`, review schema | Reviewer relation and passage/source evidence captured | P0 | M | DONE (workflow contract only) |
| SCF-011 | Add deterministic JSON/schema, claim/source and map checks | SCF-005–010 | `validation.py`, CLI, schemas, tests | JSON parse and schema validation distinct; actual Draft 2020-12 validator used | P0 | L | DONE (MVP) |
| SCF-012 | Count narration and calculate transparent runtime estimate | SCF-009 | `runtime.py`, CLI, tests | Excludes visual directions, `SCRIPT_ESTIMATE`; YS10 parity 789 | P0 | M | DONE (MVP) |
| SCF-013 | Generate verified production handoff bundle | SCF-005–012 | Future `handoff.py` | Exact revision, review, fact-check, sources and open issues packaged; approval retained | P0 | M | NOT STARTED |
| SCF-014 | Run a new-topic complete pilot from intake to handoff | SCF-005–013 | `examples/`, pilot report | Research, architecture, script, genuinely independent review, fact check and human inputs recorded | P0 | L | NOT STARTED |
| SCF-015 | Assess protected integration/change request | SCF-014 | Governance report or formal CR | No protected file change without required approval | P1 | M | NOT STARTED |
| SCF-016 | Evaluate CLI and possible future user interface | SCF-014 | usability memo | UI justified by pilot evidence, not built as a demo | P2 | M | NOT STARTED |
| SCF-017 | Add model-provider and workflow orchestration, if justified | SCF-014 | Future adapter/module | Provider is configurable, provenance logged, no fake source verification | P1 | L | NOT STARTED |

## Milestones

- **M0 Audit and design:** SCF-001–004 — complete.
- **M1 Isolated local foundation:** SCF-005–012 — MVP complete; orchestration remains manual.
- **M2 Pilot and handoff:** SCF-013–014 — not started.
- **M3 Governance and integration decisions:** SCF-015–017 — not started.
