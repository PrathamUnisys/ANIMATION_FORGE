# EP10 Revision 1 vs Revision 2 — Comparison

**Episode:** EP10 — *The Ministry of Small Apologies*  
**Revision 1 (preserved):** `REVISIONS/EP10_screenplay_rev1.md` (SHA-256 `01c0602891ff2861578ded4481d5f0bbcd4fa47c7349102b8d45de974b1a1921`)  
**Revision 2 (under review):** `REVISIONS/EP10_screenplay_rev2.md` (SHA-256 `6df5cca4e0cd5f80868e6c44cc5c5e9e6073741a54392c4cc3912bebf4309c6c`)  
**Baseline V14 (preserved):** `REVISIONS/EP10_screenplay_v14.md` (= `SCRIPTS/BASELINE/EP10_screenplay.md`, SHA-256 `aaa95009987caa94e0751bf6a7c2135dc0429893f6114bf08851bd86a5216896`, DB `SCR_SCRIPT_LAB_10_V14`)  
**Identity preserved across revisions:** premise, genre/tone (dark comedy/satire), 5-scene structure (SC01–SC05), core characters, central question, SC04 emotional turn, HABITS-tray/real-file ending, ~10:00 target, required beats/clues.

## Why revision 2 exists
Revision 1 fixed the baseline MAJOR weakness (Vell’s filing had no rule basis) by introducing “Section 7B-Precedent” in SC05. Independent review of revision 2 found the setup/payoff still needed strengthening: the clause should be established **before** SC05 (visually or verbally), Noor’s knowledge should be credible, and Vell’s decision should follow an established rule rather than a newly invented exception. Revision 2 implements those corrections plus review-driven cleanups.

## Changes revision 1 → revision 2
| Area | Revision 1 | Revision 2 | Rationale (evidence) |
|---|---|---|---|
| **7B-Precedent setup (mandatory correction 1)** | Clause first appears in SC05 (Noor cites “Section 7B-Precedent”; Vell checks tablet). | Clause established in **SC02**: Noor reads the form footer in close-up (`7B-PRECEDENT — UNSCORABLE CONDUCT NOTATION — LOGGED WITHOUT REMORSE VALUE`); Senior Clerk confirms practice (“Seventh floor still logs precedents on 7B. No number, just a record.”). SC05 recalls “the clause on the form” and states conditions. | Setup precedes payoff; Noor’s knowledge credible (she reads it; colleague confirms); Vell’s decision follows an established rule. |
| **Vell decision basis** | “Precedent logging is discretionary… Unscorable. Therefore… filed.” Conditions implied. | Noor states conditions: “no citizen injury is claimed and the escalation risk is recorded. Both are true here.” Vell: “Precedent logging is discretionary. It creates no remedy metric.” → logs `RECEIVED — NOT SCORED`. | Decision follows stated rule + conditions met; preserves Vell’s metric integrity and reluctance. |
| **SC04 emotional turn** | Preserved. | Preserved (same beats, minor interiority converted to observable posture). | Mandatory preservation. |
| **HABITS tray ending** | Preserved. | Preserved (same action; article-stacking fixed: “a fresh apology form 7B”). | Mandatory preservation; grammar cleanup. |
| **Dialogue counts (mandatory correction 4)** | Table claimed 210/220/230/230/150 (invented). | Actual counts: SC01 93, SC02 119, SC03 133, SC04 107, SC05 152 (total 604); method stated (spoken lines only, excluding parentheticals/punctuation). | Independent recount; no invented counts. |
| **Runtime (mandatory correction 5)** | ~600 s, no variance note. | ~632 s (≈10:32), within ±30–45 s uncertainty of 600 s target; variance noted in header; `RUNTIME_ESTIMATE.md` updated. | SCRIPT_ESTIMATE only; no animatic/final claim. |
| **Terminology consistency** | “remorse value”, “sincerity score”, “remorse integer” mixed. | Unified: “remorse value — the audit’s sincerity score”; “no audit’s sincerity score assigned”. | Reviewer F5. |
| **Dialogue ambiguity** | “The clause you saw on the form” (unclear referent). | “The clause on the form — 7B-PRECEDENT.” | Reviewer F4. |
| **Grammar/formatting** | “a fresh the apology form 7B”; mixed parentheticals; “naming a conduct”. | “a fresh apology form 7B”; standardized cue/parenthetical style; “naming a habit”; requirement label adjusted to MANDATORY_STORY_BEAT. | Reviewer F6/F14; formatting cleanup. |
| **Interiority** | “Noor understands: the grievance is loneliness dressed in bureaucracy.”; “She chooses procedure over purity.” | Converted to observable action/posture (softened posture; reaches for precedent log). | Visual storytelling playbook; reviewer F7. |
| **Companion artifacts** | Retention map/runtime estimate matched rev1. | `RETENTION_MAP.json` updated to rev2 (clause setup in B002, conditions in B005, SC04 160s/SC05 112s, timecodes); `RUNTIME_ESTIMATE.md` updated; `STORY_LOGIC_AND_CLUE_LEDGER.md` updated. | Traceability to exact revision. |

## What did not change
- Story identity, required beats/clues (verbatim), characters, SC04 turn, HABITS ending, satire tone, 5-scene structure, target runtime intent.
- No canon/approval changes; no protected architecture/schemas/agents/runtime/DB structures modified.

## Known residual items (see `QC_AND_REMAINING_ISSUES.md`)
- SC04 carries 51 s of pauses (intentional emotional hold) — validate in animatic.
- SC02 clause legibility in close-up — storyboard/audio must ensure the verbal line lands.
- DB lineage: rev2 is file-level; scene cards in DB remain rev1-era locations; deterministic validator not yet run on rev2 (see QC report).
- “Seventh floor” detail is color (reviewer NOTE) — keep or trim by human choice.
- No approval granted; remains AWAITING_HUMAN_REVIEW.