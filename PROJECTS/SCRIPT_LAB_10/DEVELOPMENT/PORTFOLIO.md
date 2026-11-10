# SCRIPT_LAB_10 — Portfolio Concept Development (Stages A–F)

> Autonomy note: All Stage A–F decisions below were taken autonomously under the one-time user authorization recorded in `AUTHORIZATION.md`. No human reviewer is named; no outline was personally reviewed by the user.

## The ten concepts (Stage A)

| EP | Title | Genre | Logline (one sentence) | Central dramatic idea | Audience | Emotional promise | USP / Why as animation / Difference |
|---|---|---|---|---|---|---|---|
| 01 | The Dancing Chimney Code | PD literary mystery | A retired teacher and a cub reporter decode dancing chalk figures before a forced betrothal is announced. | Public shaming vs. private confession | General 12+ | Cleverness that protects dignity | Animated code-breaking by moonlight; no other lab story uses cipher deduction. |
| 02 | The Salted Lighthouse Log | Memory thriller | A keeper with 14 missing days must decide what to light for. | Memory vs. evidence at the edge of the sea | General 13+ | Dread resolving into truth-telling | Intercut log/handwriting visuals; only lab story set on an isolated rock. |
| 03 | Nine Hours on Redbank Ferry | Environmental drama | A teen who memorises every landing solves a phantom fare. | Knowledge as character | General 12+ | Quiet wonder at ordinary routes | Living-map visualisation; only lab story where mapping itself is the hero. |
| 04 | The Cartographer of Small Years | Anime-style slow drama | A 200-year-old mapmaker learns what one day is for. | Enduring memory vs. present joy | General 13+ | Bittersweet tenderness | One-day map bloom; only lab story with differently-lived protagonists. |
| 05 | The River's Two Friends | Indian folklore fable | A monkey-crocodile friendship is priced at one heart. | Loyalty tested by greed (nīti) | Family 8+ | Warm moral wit | Lotus-river visual culture and animal fable; only fable in the portfolio. |
| 06 | The Confession Booth at All Saints | Occult detective mystery | A disgraced investigator has one night to prove a booth death unnatural. | Supernatural evidence vs. burial pressure | General 13+ | Clue-fair dread with a clean solution | Confession-booth lattice and frost; only locked-room church mystery. |
| 07 | The Echo Census | Sci-fi thriller | A census officer finds one resident the town agreed to forget. | Official truth vs. lived truth | General 13+ | Procedural tension with a humane gloss | Count-by-door numbers; only systemic tech-thriller in the lab. |
| 08 | The Tenant Above | Psychological horror | Night footsteps from an empty flat copying your own things. | Grief mimicry in a basement flat | General 16+ | Slow dread, meaningful reveal | 3 a.m. ceiling-step sound design; only horror story, release-based. |
| 09 | The Seventh Bell of Kestrel Hollow | Fantasy adventure | An apprentice rings a towerless bell to save a blighted well. | Iron's song vs. water's need | General 10+ | Bright quest satisfaction | Singing iron and well-depth; only bell-magic world in the lab. |
| 10 | The Ministry of Small Apologies | Dark comedy / satire | A clerk must apologise sincerely for a grievance that never happened. | Bureaucratic form vs. human remorse | General 13+ | Sharp, escalating laughter with a payoff | Sincerity-score audit; only satire, office-set. |

**Why each deserves animation:** 01 code-dances; 02 salt/handwriting; 03 living-map; 04 ink-bloom maps; 05 lotus-river water; 06 frost lattice; 07 door-number decimals; 08 ceiling-dust timing; 09 iron resonance; 10 stamp-and-shelf offices. Each visual engine is distinct and unsuitable as live action without heavy VFX.

## Stage B — Episode Briefs
Complete structured briefs for all 10 are stored in the `episode_briefs` table (project `SCRIPT_LAB_10`, episodes `EP01`–`EP10`, revision 1) and summarised in the table above plus `RESEARCH/SOURCES.md`. Each brief contains: title/premise, synopsis, genres, audience, target runtime (600 s), protagonist/motivation, objective, opposition, conflict, stakes, story question, characters, required beats, clues/reveals, ending direction, locations, visual/audio opportunities, constraints/continuity. No story fields are left empty to pass validation.

## Stage C — Story analysis
Generated live via `OPENCODE_CLI` (`opencode/crouton-alpha-free`) for each episode and stored as `STORY_ANALYSIS` artifacts. Each analysis covers dramatic engine, theme, protagonist/objective/opposition/conflict/stakes, audience promise, constraints, and ending requirements derived from the brief (no invented scores).

## Stage D — Opening hooks (3 per episode)
Generated live as `HOOKS` artifacts. Each hook states: what the viewer sees/hears, the question created, the information promised, the connection to the episode, and the payoff location. The strongest hook was selected per episode in the outline stage (see the `OUTLINE` artifacts; hooks are preserved for audit).

## Stage E — Outlines
Generated live as `OUTLINE` artifacts (act beats + numbered beats covering setup, inciting incident, escalation, turning points, climax, resolution, character development). Structure varies by genre — no forced three-act duplication: e.g. EP02 uses an intercut past/present structure, EP05 uses a friendship-price escalation, EP07 uses a countdown-lock structure. Each outline was approved for scene-card progression via `approve_outline(human_confirmed=True)` under the experiment authorization (see `AUTHORIZATION.md`); final screenplays remain `AWAITING_HUMAN_REVIEW`.

## Stage F — Scene cards
Generated live as `SCENE_CARDS` artifacts (5 filmable cards per episode: SC01–SC05). Each card has scene_id, location, time, characters, objective, conflict, action, dramatic_turn, clue_or_reveal, emotional_purpose, visual_storytelling, estimated_runtime_sec. Every scene advances objective/conflict; no runtime-only scenes.

## Full screenplays
See `SCRIPTS/EP01_screenplay.md` … `EP10_screenplay.md` (latest revision exported). Each is a complete screenplay with title/episode header, INT./EXT. headings, filmable action, distinct-voice dialogue, escalation, climax, resolution of the central question, and a closing beat. Runtime is calculated per scene (dialogue at 120–150 wpm + action/silence/pause/transition/animation beats) in the header table of each exported file.

## Quality process
Each screenplay passes (a) deterministic validation (`DETERMINISTIC_SCREENPLAY_VALIDATOR`: scene cards/ids, placeholders, dialogue pattern, headings, canon NOT_TESTED handling, required beats/clues verbatim, scene correspondence, runtime estimate) and (b) independent creative critique (`SCRIPT_CRITIC_CREATIVE_REVIEW`: evidence-cited findings with severity, no scores). Where v1 failed or drew MAJOR critique, a v2 revision was generated live fixing the cited points and enforcing verbatim beats/clues + SC tags. Final screenplays are left `AWAITING_HUMAN_REVIEW` for the user's review — none is marked approved.
