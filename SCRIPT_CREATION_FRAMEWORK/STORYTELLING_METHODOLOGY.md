# Storytelling Methodology

**Status:** Proposed method for the isolated Script Creation Framework. It does not replace approved Animation Forge instructions or governance.

## Guiding principle

Choose a story shape that fits the evidence and subject. Do not choose a formula first and force the topic into it. The goal is a clear, compelling promise that the script can honestly fulfil.

## 1. Intake and brief

Accept a question, title, subject, rough story, existing research, or source packet. Capture the intended audience, format, language, runtime target, tone, visual/production limits, rights constraints, known facts, and what the user hopes viewers will understand or feel. Mark unknowns rather than filling them with invention. Keep the approved language rule: everyday English understandable on first listen by an average 12-year-old, while keeping adult themes and intellectual depth.

**Artifact:** Brief with inputs, knowns, assumptions, constraints, open questions and intended outcome.

## 2. Research and story discovery

Research the topic before deciding the story. Build a source dossier with the source's author/publisher, date, source type, primary/secondary status, relevant passage or data locator, claim supported, scope, limitations, access date and link. Seek original records, papers, official data, direct testimony or authoritative subject institutions where available. Use reputable secondary work for context and source discovery. When evidence conflicts, preserve the disagreement and explain why it matters.

Create a claim/evidence ledger before drafting factual narration. Separate:

- verified fact;
- disputed or uncertain claim;
- source interpretation;
- writer inference;
- illustrative example or composite;
- hypothetical/speculation;
- unknown / not established.

Do not treat AI output, an unsourced search snippet, a visual reconstruction or a repeated claim as independent verification. Identify rights/originality questions separately from factual truth.

**Artifact:** Research dossier, claim ledger, chronology/mechanism map as relevant, uncertainty and rights notes.

## 3. Identify story opportunities

Ask: What is surprising, misunderstood, consequential, or unresolved? What does the viewer need to find out? What changes as the answer emerges? What evidence can support a meaningful payoff? Is there a person, event, mechanism, system, object, place or decision that can carry the explanation? What would be dishonest or too speculative to promise?

Possible story engines include:

| Engine | Useful when | Common risk |
|---|---|---|
| Investigation / mystery | Evidence accumulates toward an answer | Artificially withholding known facts or implying certainty that evidence lacks |
| Event-led chronology | A consequential event has a traceable sequence | A date list without causality or stakes |
| Character / decision | A person's choices and constraints are documented and central | Invented inner thoughts or lone-hero exaggeration |
| Mechanism / question | A process or counterintuitive effect explains a puzzle | Detached lecture or analogy mistaken for proof |
| System / infrastructure journey | The viewer can follow a process across components | Generic exposition without a concrete case |
| Failure / investigation | Evidence shows how a system failed and what is known | Overconfident single-cause claims when the record is mixed |
| Survival / changing plans | Obstacles force consequential adaptations | Repetitive peril beats or implied inevitability |
| Hypothetical / thought experiment | A bounded scenario reveals a concept | Passing fiction off as prediction or established science |
| Place / ecology | Contrasts and local conditions make a place legible | Treating a region or ecosystem as uniform |

Generate alternatives only when there are genuinely different evidence-supported routes. Compare each on evidence, clarity, stakes/relevance, visual potential, likely complexity and risks. Recommend one with reasons; the human selects the direction when that choice affects the project.

**Artifact:** One selected concept, or a small slate of meaningful alternatives; each carries an evidence and production note.

## 4. Story architecture

Define:

- central question or tension;
- one-sentence promise to the viewer;
- starting state and necessary context;
- what the viewer currently believes/knows;
- ordered discoveries, events or causal steps;
- points where new evidence changes the explanation;
- emotional and comprehension turns;
- limits/counterarguments that must be addressed;
- ending that resolves the question to the degree the evidence permits;
- visual carrier for each major idea;
- questions intentionally left open.

Select an architecture appropriate to the route: a chronological chain, investigation, mechanism reveal, case study plus general model, comparative account, journey through a system, or another structure. Three-act language can help if it clarifies movement, but is optional. No standard scene count, hook interval or cliffhanger cadence is required.

For each transition, test: “Given the evidence/choice just presented, why does the next section follow?” For fictional narratives, test the equivalent causal bridge and motivation. Mark missing information and uncertain inference.

**Artifact:** Story architecture/beat map with evidence links and open decisions.

## 5. Packaging and opening

Develop truthful titles and thumbnail concepts after the story direction is clear. Evaluate if a viewer can understand the topic and promise quickly, whether the title's scope matches evidence, whether imagery implies a false fact, and where the script fulfils the promise. A package is an editorial proposal, not a predicted click result.

Draft multiple openings only when they differ in useful ways (e.g. event, contradiction, consequence, image, personal dilemma). For each note the exact question raised, information delivered immediately, assumption risk, and later payoff. Avoid generic introductions and avoid manufactured stakes.

## 6. Drafting and production writing

Write narration to be spoken. Use natural sentence rhythm, plain words and explicit references. Define necessary technical terms on first use. Keep mature subject matter intact. Avoid duplicate narration of what the image already communicates. Distinguish fact from reconstruction and label schematic or illustrative visuals. For each visual/audio direction, state the job it does: orient, compare, reveal, demonstrate, establish evidence, carry emotion, or transition. Do not ask animation to depict exact historic footage or geometry if the source only supports a schematic.

## 7. Editorial review, fact verification and revision

Keep three independent work products:

1. **Creative review:** reads the exact script, cites passages, evaluates promise, narrative progression, clarity, pacing, emotional effect, ending, accessibility and feasible presentation. The critic receives no author self-review or claimed resolutions before first review.
2. **Claim verification:** checks each load-bearing factual claim against its linked source(s), scope, quote/number/date, uncertainty and the actual narration. The fact checker does not treat the writer's confidence as evidence.
3. **Deterministic QC:** checks computable properties such as required fields, IDs, count freshness, source-reference existence, script-to-map anchors, timecode ordering, status semantics, and runtime arithmetic. JSON syntax parsing and schema validation are separate checks; report formal schema validation only if a real validator runs against the intended schema.

The reviewer distinguishes evidence, interpretation and preference. Use BLOCKER, MAJOR, MINOR, NOTE with the consequence, not arbitrary numerical thresholds. The writer may accept, partially address, defer or decline a finding with a reason. Revision creates a new immutable artifact/version; preserve prior text and reviewer reports. After revision, run claim verification and deterministic QC again, and obtain another independent review where practical or where a material change affects reviewed logic.

## 8. Runtime and final handoff

Recount spoken text from the exact revision. State the counting convention (for example, narration blocks only), speaking-rate assumption, planned nonverbal pauses/holds and transition budget. Report `SCRIPT_ESTIMATE` until a timed recording or animatic exists. When available, label `ANIMATIC_MEASURED` or final-video measurement and preserve method/source. Do not add text just to fill a target runtime.

Final package links the brief, sources, claim ledger, chosen concept, architecture, script revision, review, responses, fact-check, QC results, count/runtime report, production needs, unresolved issues and human approval status. Do not call a draft approved or production-ready without the configured human gate.
