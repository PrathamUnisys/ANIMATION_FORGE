---
prompt_id: TOOL_INTEL_REQUIREMENTS
version: 1.0.0
modified_date: 2026-11-09
description: Convert approved creative direction into measurable tool requirements.
dependencies: ["CORE_SYSTEM_CONSTITUTION", "TOOL_INTEL_ONLINE_RESEARCH"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial requirements analysis procedure
---
# Requirement Analysis

## Entry conditions
Use the approved screenplay/brief and project constraints as the source of truth. In the implemented R&D engine, `run_mandatory_project_rnd` requires an `APPROVED` screenplay before it starts (`backend/rnd/research_engine.py`). This document guides analysis; it does not authorize production.

## Build a traceable requirement set
For each requirement record:
- stable requirement ID; originating scene, shot, or production need;
- user-facing outcome and measurable acceptance criteria (format, resolution/frame rate/duration, quality, latency, throughput, repeatability, offline/online needs as applicable);
- dependencies, inputs/outputs, volume, and expected revision/reuse;
- constraints: platform, hardware, schedule, budget ceiling, data handling, accessibility, and commercial distribution;
- priority (`MUST`, `SHOULD`, `COULD`), owner, and unresolved assumptions.

Separate creative quality judgments from machine-checkable criteria. “Keep character recognizable” needs a human-approved visual reference and a review method; it is not proven by a seed or a model name. Do not invent numerical thresholds—obtain them from the approved brief or label them proposed for human confirmation.

## Candidate-independent requirements
Write requirements before selecting products. Derive tests that can disqualify a candidate, identify what evidence each needs, and distinguish minimum pass conditions from comparative preferences. Map every candidate feature claim to a requirement and evidence source.

## Deliverable
Maintain a requirement-to-evidence-to-test matrix. Record gaps as `UNKNOWN`, not “supported.” Changes to approved creative intent or budget require the appropriate human decision. An R&D report is advisory until the human accepts the toolchain.

Implementation reference: `backend/rnd/research_engine.py` currently uses a fixed demonstration requirement list; do not mistake it for automatic extraction of all project-specific requirements.
