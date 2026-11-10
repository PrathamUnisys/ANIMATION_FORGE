# EP10 QC Results & Remaining Issues

**Episode:** EP10 — *The Ministry of Small Apologies*  
**Improved script:** `SCRIPTS/EP10_screenplay.md` (framework-upgrade working revision, 2026-11-10)  
**Baseline:** `SCRIPTS/BASELINE/EP10_screenplay.md` / DB `SCR_SCRIPT_LAB_10_V14`

## QC executed (this pass)
| Check | Result | Evidence |
|---|---|---|
| Verbatim required beats present | PASS | `the Ministry of Small Apologies`, `the grievance that never happened`, `the sincerity audit` all found in improved script. |
| Verbatim required clues/props present | PASS | `the apology form 7B`, `the unread complaints shelf`, `the audit's sincerity score` all found. |
| Scene structure tags | PASS | `SC01`–`SC05` present (5). INT. headings present for all scenes. |
| Retention Map JSON validity (schema structure) | PASS | `DEVELOPMENT/EP10/RETENTION_MAP.json` parses (`python -m json.tool` exit 0); contains required top-level fields and 6 beats referencing existing `SC01`–`SC05`. |
| Baseline preserved | PASS | `SCRIPTS/BASELINE/EP10_screenplay.md` unchanged (SHA-256 `aaa9500...16896`); improved written to `SCRIPTS/EP10_screenplay.md`. |
| Human approval status | NOT APPROVED | Script is **AWAITING_HUMAN_REVIEW** (no approval granted). |

## QC not executed / not available (declared)
| Check | Status | Reason |
|---|---|---|
| Repo automated deterministic screenplay validator on this improved file revision | NOT EXECUTED | No automated run invoked against this working file revision in this pass; DB deterministic QC report exists for baseline `SCR_SCRIPT_LAB_10_V14` only (`NOT_TESTED` for missing approved canon, 0 MAJOR/BLOCKER per prior summary). Manual structural/element checks above performed instead. |
| Animatic-measured runtime | NOT AVAILABLE | No animatic; runtime is `SCRIPT_ESTIMATE` only. |
| Final video-measured runtime | NOT AVAILABLE | No render/export. |
| Automated tests / lint / full test suite | NOT EXECUTED | Not run in this pass (no claim of pass). |
| Provider/live pipeline regeneration | NOT EXECUTED | Improvement performed as authored revision; `OPENCODE_CLI` was previously free-limit blocked (historical). |

## Remaining issues & human decisions required
| ID | Severity | Item | Owner/decision |
|---|---|---|---|
| R1 | MINOR (decision) | **7B-Precedent clause** is a plausible in-world procedure introduced to ground Vell’s discretion (episode focus). Confirm acceptability as episode-specific rule text (no canon/governance change). | Human reviewer / story lead |
| R2 | MINOR | Animatic timing/performance read-aloud to validate SC04 pause and overall ~10:00 feel. | Production/animatic |
| R3 | MINOR | Optional storyboard emphasis: shelf+REAL tag (SC01/SC05), dial needle (SC03/SC05), margin writing (SC04), RECEIVED—NOT SCORED stamp and HABITS tray (SC05). | Art/storyboard |
| R4 | NOTE | DB lineage: improved working revision not inserted as new `scripts` row (e.g. next version after V14) in this batch. When accepted for tracking, register per repo convention with correct `previous_version`/references, keeping V14 immutable and all statuses `AWAITING_HUMAN_REVIEW` unless/until human approval process occurs. | Producer/engineering (governed) |
| R5 | NOTE | Packaging (title/thumbnail/text) not evaluated; ensure no misrepresentation if created later. | Human/marketing |
| R6 | NOTE | No canon/approval changes made. Any promotion requires existing human approval process. | Human approver |

## Rollback
- Restore baseline script: copy `SCRIPTS/BASELINE/EP10_screenplay.md` over `SCRIPTS/EP10_screenplay.md`.
- Review artifacts under `DEVELOPMENT/EP10/` are additive; remove or revise if reverting.
- No DB schema/data migrations performed by this pass; DB baseline `SCR_SCRIPT_LAB_10_V14` unchanged. Git branch `script-lab-10/framework-upgrade` contains file changes for review.