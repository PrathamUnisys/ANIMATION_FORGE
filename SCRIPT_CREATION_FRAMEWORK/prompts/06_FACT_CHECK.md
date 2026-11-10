# Fact-Check Prompt

This is an aid to a human fact-checker. It cannot verify facts by language-model confidence.

For every claim marker in the exact script revision, compare the wording with the cited source passages. Check names, dates, numbers, causal wording, scope, quotations and whether an example is representative. Mark each claim `VERIFIED`, `QUALIFIED`, `DISPUTED`, `UNSUPPORTED` or `NOT_APPLICABLE`. Cite source IDs and locators, describe what the evidence says and identify overreach. Check whether the passage changes meaning when read in context.

Do not mark a claim verified without opening and reviewing the cited source. Do not make a new source or locator up. Flag missing citations and claims that have no marker. Keep factual conclusions separate from creative-review findings. Record who checked the claim, when and against which revision hash.

## Inputs

- Exact script and SHA-256:
- Claim ledger:
- Source ledger and source excerpts/locators:
