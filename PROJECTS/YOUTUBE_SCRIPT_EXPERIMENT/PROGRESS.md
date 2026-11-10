# YouTube Script Experiment — Progress

**Status:** Editorial deliverables complete; no scripts published or audience-tested.  
**Working branch:** `ep10-revision-2` (dedicated branch creation was denied by local Git permissions).  
**Rule:** Keep EP10 changes untouched. Do not change Animation Forge framework files until all ten scripts have reviews, revisions, and the experiment report.

| Batch | Scripts | Concepts | Original | Independent review | Revised | State |
|---|---|---|---|---|---|---|
| 1 | YS01, YS02 | Selected | Complete; counts 958 / 1,012 | Independent first and second passes complete | Complete; revised counts 821 / 848 | Complete; final map audit added YS02's missing 07:35 row |
| 2 | YS03, YS04 | Selected and source-checked | Complete; counts 835 / 860 (narration-only recount; original metadata preserved) | First and second independent passes complete; corrections verified | Complete; revised counts 761 / 860 | Complete; final title/source/map corrections recorded |
| 3 | YS05, YS06 | Selected and sourced | Complete; counts 827 / 892 | Independent first and second passes complete; verification addenda preserved | Complete; revised counts 870 / 954 | Complete; counts, estimates, title, and timecodes reconciled |
| 4 | YS07, YS08 | Selected and source-checked | Complete; counts 901 / 795 | First and blind second passes complete; YS07 opening clarification made after second pass | Complete; current counts 941 / 798 | Complete; YS08 density note retained for pacing; YS07 final sentence not third-reviewed |
| 5 | YS09, YS10 | Selected and source-checked | Complete; counts 810 / 831 | Independent first and blind second passes complete; targeted package/metadata checks complete | Complete; counts 860 / 789 | Complete; title, thumbnail, documented case, runtime, and map checks reconciled |

## Scope and evidence rules

- Audience: general YouTube viewers, teenagers and adults; keep wording clear enough for an average 12-year-old to follow on first listen while preserving mature ideas.
- Runtime: 8–12 minute target, marked `SCRIPT_ESTIMATE` until measured by a recorded narration or animatic.
- Research separates official platform guidance, historical/scientific sources, editorial judgment, and testable hypotheses.
- Independent reviewers receive the package and script without the writer's self-assessment or claimed fixes.
- No performance or retention numbers will be claimed without published-video analytics.
- No framework changes before the final cross-script analysis and proposed change report.
- All ten original scripts are preserved; all ten revised scripts have complete narration, title/thumbnail packages, alternative hooks, sources, visual/audio direction, and an in-script Retention Map.
- All ten revised scripts passed the final deterministic narration-count, metadata, chapter/Retention Map, and stale-runtime-line audit. Per-script independent reviews and change reports are preserved. YS07's final one-sentence opening clarification was not given a third review; YS08's information-density note remains an edit pacing consideration.
- Cross-script analysis and the experiment report are complete. `REPORTS/FRAMEWORK_CHANGE_PROPOSAL.md` is a recommendation only; no protected framework files were changed. No scripts were published or audience-tested, and every duration remains `SCRIPT_ESTIMATE`.

## Final deterministic and repository checks

- **PASS:** All 10 revised narration counts match their metadata.
- **PASS:** All 10 revised chapter timecodes match their Retention Maps.
- **PASS:** All 10 revised document headings match their primary titles; each has two alternative hooks.
- **FAIL:** Prescribed pytest command returned 30 passed / 1 failed. The failure is `ContractTests.test_complete_instruction_repository_passes`, caused by the existing CR_007 missing-frontmatter and missing-audit-inventory findings. Two pytest-cache permission warnings were emitted.
- **FAIL:** Instruction validator returned 131 files / 9 rules / 2 findings, both the existing CR_007 findings. The experiment did not modify CR_007 or its audit inventory.
- **FAIL:** `git diff --check` reports four Markdown hard-break trailing-space lines in the existing EP10 runtime/ledger companion files; they were left untouched as outside this experiment's scope. Git also prints line-ending normalization warnings.
- **NOT_AVAILABLE:** JSON parsing/schema validation do not apply; this deliverable is Markdown and changed no JSON/schema. No timed narration/animatic or published-video analytics exists.
- Test-generated changes to the nine known previously clean tracked files were restored. EP10 and YouTube experiment files remain present.
