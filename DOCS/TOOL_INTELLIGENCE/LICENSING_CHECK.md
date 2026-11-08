---
prompt_id: TOOL_INTEL_LICENSING
version: 1.0.0
modified_date: 2026-11-09
description: Verify software, model, content, and output rights before adoption.
dependencies: ["TOOL_INTEL_ONLINE_RESEARCH", "TOOL_INTEL_DISCOVERY"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Initial licensing review procedure
---
# Licensing Check

Review each layer separately: application/software license; plugin/extensions; model/checkpoint/weights; datasets and reference assets; fonts, audio, scripts, and other inputs; generated outputs; and cloud-service terms. Record exact version, rights holder, primary license/terms URL, retrieval date, commercial/redistribution status, attribution obligations, restrictions, and unresolved legal questions.

Do not infer model rights from framework license, “open weights,” free download, or output ownership language. Verify intended distribution/use (including client work, monetization, derivative assets, voice/likeness, and training/data retention) against current primary terms. Escalate ambiguity to the responsible human/legal reviewer; mark `UNKNOWN` pending resolution.

## Evidence discipline
Quote or precisely summarize the relevant clause with a source locator and date. Separate documented permission from a legal conclusion. Community answers are leads, not authoritative permission. Save notices and required attribution with the project when permitted.

The R&D candidate schema stores a free-text license and a commercial-use boolean, but that is not a legal review or enforcement mechanism (`SCHEMAS/TOOL.schema.json`). Record the full evidence and decision outside those fields.

No POC downloads, installs, paid operations, or toolchain lock may bypass applicable human approval. A favorable licensing screen is not approval for creative output or release.
