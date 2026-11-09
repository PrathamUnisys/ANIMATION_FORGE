---
prompt_id: STORY_ACQUISITION_INDEX
version: 0.1.0
modified_date: 2026-11-09
description: Preparatory source-discovery, provenance and rights-review workspace for story development
---

# Story Acquisition

## Purpose

`STORY_ACQUISITION/` is the planned entry point for stories and story references before they enter screenplay development. It separates where an idea came from, what use is intended, what evidence supports its provenance, and whether adaptation/publication rights have been reviewed.

This is a preparatory documentation layer. It is not yet connected to the application database, project-creation UI, screenplay context assembler or a legal clearance service.

## Supported source routes

The source taxonomy in `SOURCE_TYPES.json` distinguishes:

- Original idea supplied by the user.
- Original AI-assisted concept developed for the project.
- Public-domain literary or dramatic work.
- Traditional folklore, mythology or oral tradition.
- Historical event or documented mystery.
- Openly licensed work.
- Licensed work.
- Commissioned work.
- Inspiration-only reference.

These categories describe provenance. They do not, by themselves, establish ownership, public-domain status, permission or commercial-use rights.

## Intended workflow

1. Capture the source route and user's intended use.
2. Create a source dossier with bibliographic, historical or provenance details.
3. Identify the exact work, edition, translation, adaptation and relevant territory where applicable.
4. Gather reliable rights evidence and record unresolved questions.
5. Conduct an originality review to distinguish source facts/ideas from protected expression.
6. Route uncertain or permission-dependent cases to a human rights reviewer or qualified counsel.
7. Generate story concepts only within the permitted scope.
8. Obtain human approval of the selected concept before screenplay development.
9. Preserve source references and review decisions with the resulting story and screenplay.

See `RESEARCH_WORKFLOW.md`, `RIGHTS_AND_ORIGINALITY_POLICY.md` and the templates folder.

## Status discipline

Use `SOURCE_TYPES.json` as the provisional vocabulary. A future schema/API may refine it after review.

Important distinctions:

- **Source research status**: whether source information has been collected.
- **Rights assessment status**: whether intended use has been assessed for specified territories.
- **Originality review status**: whether the proposed treatment has been examined for similarities to protected expression.
- **Creative approval status**: whether the human has selected the story concept.
- **Screenplay approval status**: whether a specific screenplay revision has been approved.

Do not collapse these into one green status. A public-domain source can still contain a protected translation or illustration; a rights-cleared source can still lead to a weak story; an approved story concept is not automatically an approved screenplay.

## Safety and legal boundary

The records are evidence-management aids, not legal opinions. Do not label a source globally public domain based only on the author's death date, publication age, an online upload or an AI-generated answer. Record territory, term basis, exact edition/version, rights holder/permission evidence and intended uses. If uncertainty remains, use `REVIEW_REQUIRED` and block adaptation/publication until reviewed.

## Future implementation boundaries

The eventual system may add source search, source records, rights assessments, originality review, source-to-story links, approval gates and screenplay provenance. None of those are currently represented as working runtime capabilities by these documents alone.
