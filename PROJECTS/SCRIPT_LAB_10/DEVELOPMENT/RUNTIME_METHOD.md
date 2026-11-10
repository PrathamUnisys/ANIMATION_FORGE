# SCRIPT_LAB_10 — Runtime Method (per screenplay)

**Target:** 9:30–10:30 (570–630 s) finished video per episode.

**Method (no word-count-only shortcut):** For each scene:
`scene_seconds = dialogue_words / wpm + action_seconds + silent_beats_seconds + pause_seconds + transition_seconds`
- Dialogue rate: 120–150 wpm (130 wpm used as baseline; comedy/atonal scenes slower, fast exchanges faster).
- Action/silent beats: estimated from screenplay action lines (e.g. 5–8 s per unit of filmable business, 3–5 s per reaction hold, 2 s per transition).
- Emotional pauses: 3–6 s per turn, handled as part of action beats.

**Per-scene table** is printed in each exported screenplay header (`SCRIPTS/EPxx_screenplay.md`) and summed to a total. Card `estimated_runtime_sec` sums are a separate cross-check (pipeline `SUM_SCENE_CARDS` method) — they are estimates only, not measured playback.

**QC/runtime cross-check:** Deterministic validator records `runtime_estimate.total_sec` per script version in `screenplay_qc_reports`. These are reported in `DEVELOPMENT/QC_SUMMARY.md` alongside the manual tables.
