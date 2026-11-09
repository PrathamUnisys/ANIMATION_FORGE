# Animation Forge — Bake-off (2026-11-09)

Companion to `PIPELINE_V2.md` §8. This file exists because the previous pipeline chose its
method by assumption and shipped a 5.5/10 demo. Here the method is **chosen by score**.

Machine-readable counterpart: `PIPELINE/BAKEOFF/scorecard.json`.

---

## 1. Question being answered

Two questions, deliberately separated because they have different answers:

1. **Which production method** produces the best quality-per-hour on this machine?
   (VRM+Blender · MetaHuman+Unreal · 2D Moho · AI video baseline)
2. **Which engine** renders the same asset best?
   (Blender 5.2.1 EEVEE/Cycles vs Unreal 5.8.4 MRQ)

Question 2 is only meaningful once a character exists, so it runs after question 1.

---

## 2. Control shots

Both shots are fixed and identical across tracks. Changing the shot invalidates the comparison.

### Shot 1 — "Performance" (tests the character)
```
A character delivers one line, then turns their head toward camera
and makes one deliberate hand gesture.
Coverage: (a) medium shot, frontal. (b) the SAME character, 30° off-axis.
Duration: 5 s · 24 fps · 120 frames
```
**Why a turn and a gesture:** a head turn is where 2D cutouts tear, where AI video re-invents
the face, and where a rig simply obeys. Two angles is the whole point — a single hero shot
proves nothing about consistency.

### Shot 2 — "Architecture" (tests the environment)
```
A camera pushes forward through an interior corridor toward a lit doorway.
No character. Straight walls, defined perspective lines.
Duration: 5 s · 24 fps · 120 frames
```
**Why this shot:** if AI video is used, the walls will visibly bend. That result settles the
environment half of the architecture permanently.

### Shared audio
One line, generated once by the provider interface, then frozen (`PIPELINE_V2.md` §7).
All tracks must use the **same WAV** or the lip-sync comparison is meaningless.

---

## 3. Tracks

| ID | Method | Character source | Status |
|---|---|---|---|
**1a** | VRM + Blender | `Documents\3D\Anime Character\RedHairGirl.vrm` (or similar) | primary stylised |
**1b** | MetaHuman + Unreal 5.8 | MetaHuman Creator, optimised | primary realistic |
**2** | 2D skeletal | AI layered art → Rigby2D → **Moho 14.4** | stylised 2D |
**3** | AI video baseline | Wan 2.2 I2V — **deferred**, needs ~15 GB of weights | control only |
**E** | Engine comparison | whichever track won, rendered in both engines | decides engine |

Time-box: any track that has not produced a comparable 5 s clip within one working session is
recorded as **abandoned** with the reason, not quietly dropped.

---

## 4. Scoring rubric

Weighted, because "best quality" alone is not actionable.

| # | Criterion | Weight | What good looks like |
|---|---|---|---|
1 | **Character consistency** across the two angles | **30** | same face, proportions, hair, costume — no drift |
2 | Motion believability | 20 | no morphing, warping, extra/missing fingers, jitter |
3 | Cinematic look | 15 | composition, lighting, material response, grade |
4 | Lip-sync accuracy | 10 | mouth lands on the syllables; no flapping |
5 | Prop / texture fidelity | 10 | hands, cloth, held objects hold together |
6 | **Cost** | 15 | minutes per finished second · peak RAM · peak VRAM · **re-roll rate** |

Each criterion scored 1–5. Weighted total = `Σ(score/5 × weight)` → 0–100.

**Re-roll rate** is weighted inside cost on purpose: a method that nails it on take 1 beats a
prettier method that needs 12 attempts. Record `kept / attempts`.

### Engine comparison (question 2) adds
| Criterion | Weight | Measure |
|---|---|---|
Image quality | 30 | aliasing, noise, DOF/motion-blur correctness, sharpness |
Wall clock per frame | 25 | measured |
Peak RAM / VRAM | 20 | measured, not estimated |
Iteration time (edit → see result) | 15 | measured |
Automation friction | 10 | headless viability, scripting effort |

---

## 5. Results

Fill one row per track per shot. `scorecard.json` is the source of truth; this table mirrors it.

### Shot 1 — performance
| Track | Consistency | Motion | Look | Lip | Fidelity | Cost | **Total** | Kept/attempts | Notes |
|---|---|---|---|---|---|---|---|---|---|
1a VRM + Blender | | | | | | | | | |
1b MetaHuman + Unreal | | | | | | | | | |
2 2D Moho | | | | | | | | | |
3 AI video | | | | | | | | | deferred |

### Shot 2 — architecture
| Track | Rigidity | Look | Cost | **Total** | Notes |
|---|---|---|---|---|---|
2.5D projection (C2→C4) | | | | | |
AI video | | | | | deferred |

### Engine comparison (E)
| Engine | Quality | Wall clock | Peak RAM | Peak VRAM | Iteration | Automation | **Total** |
|---|---|---|---|---|---|---|---|
Blender EEVEE | | | | | | | |
Blender Cycles (3 hero frames) | | | | | | | |
Unreal 5.8 MRQ | | | | | | | |

---

## 6. Verdict rule

- No track is declared winner without a completed row.
- A winning row must state the **measured** numbers, not adjectives.
- The routing rule in `PIPELINE_V2.md` §5 is then updated to match what actually won.
- If the result contradicts the plan's prior (e.g. 2D wins outright), **the plan changes** — the
  prior is not defended.

### Current priors (to be tested, not assumed)
| Question | Prior | Reason |
|---|---|---|
Best character method | 1a VRM for stylised, 1b MetaHuman for realistic | standard rig → consistency; MetaHuman Animator for faces |
Best environment | 2.5D projection | rigid geometry under camera moves |
Best engine | Blender for work, Unreal for finishing | automation + RAM vs MRQ/OCIO/DOF |
Best facial method | VRM+Blender for stylised, MetaHuman Animator for realistic | Animator cannot drive a VRM |

---

## 7. Change log

| Date | Change |
|---|---|
| 2026-11-09 | Created. Two control shots, four production tracks plus an engine comparison, weighted rubric, verdict rule. |
