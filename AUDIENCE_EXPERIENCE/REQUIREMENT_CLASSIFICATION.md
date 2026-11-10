# Story Requirement Classification

**Status:** DRAFT PROPOSAL. Companion to SCREENWRITING_CONSTITUTION.md; not yet an active validator contract.

## Purpose

Prevent an episode brief, research note, or task instruction from being translated into unnatural screenplay language. Classify what must happen separately from what must be said exactly.

## Requirement types

| Type | Meaning | Validation expectation |
|---|---|---|
| MANDATORY_STORY_BEAT | A required event, choice, relationship change, or outcome | Confirm that the intended narrative function occurs. Wording and scene placement may vary unless constrained elsewhere. |
| MANDATORY_CLUE | Evidence that must exist and contribute to a deduction or reveal | Confirm that the clue is observable, appears early enough, and has a traceable role in the payoff. Exact phrasing is not required unless separately classified. |
| EXACT_TEXT | A literal phrase, line, label, quote, or text element that must appear unchanged | Compare the exact required string, including punctuation/case rules specified by the source. Do not paraphrase. |

## Classification rules

1. Preserve the source requirement and its source reference.
2. Assign exactly one primary type to each atomic requirement. If one sentence contains multiple requirements, split it into separate records.
3. Record the intended purpose and the evidence location in the screenplay.
4. Do not silently upgrade a story beat or clue into an exact-text requirement.
5. If the source explicitly says a phrase must appear verbatim, classify it as EXACT_TEXT.
6. If classification is ambiguous and materially affects the draft, flag it for human clarification rather than guessing.
7. A requirement may also carry a separate constraint such as character, location, sequence, or deadline; record that constraint without changing its primary type.

## Suggested record

    {
      "requirement_id": "REQ-001",
      "type": "MANDATORY_STORY_BEAT",
      "source_ref": "episode-brief:required_beats[0]",
      "requirement": "The protagonist discovers the second log entry is in their own handwriting.",
      "purpose": "Reveal the source of the apparent second writer.",
      "constraints": ["must occur before the final decision"],
      "evidence_refs": ["SC04"],
      "validation_status": "NOT_TESTED"
    }

The record above is illustrative, not a new persisted schema.

## Validation outcomes

Use only outcomes supported by the relevant validation process:
- PASS: evidence demonstrates the requirement.
- ISSUE: evidence shows the requirement is missing or contradicted.
- NOT_TESTED: no relevant check was performed.
- NOT_APPLICABLE: the requirement does not apply to the reviewed revision, with rationale.

Do not treat absence of an exact string as a failure for a story beat or clue. Do not claim semantic validation was automated unless a validator actually performed it.
