# RUBRIC.md — lockedin-audit routing contract

This file is the **routing layer** for the audit skill's rubric. The
five scoring dimensions are defined and maintained in the render
skills. This file does not duplicate them. It routes to the correct
rubric based on the document type detected by the scorer.

**Hard rule**: the five dimensions and their score bands live in
exactly one place each. If you are scoring an English resume, load
the resume-en rubric. If you are scoring a Korean cover letter (jaso), load the
jaso rubric. Load the referenced file fresh in the reviewer turn.

## Document type routing

### English resume

Load and apply:

```
../lockedin-render-resume-en/RUBRIC.md
```

Five dimensions:
1. Metric Density (impact-first bullets)
2. Action Verb Quality (active voice + diversity)
3. Structural Adherence (XYZ, length, format)
4. Banned Phrase Cleanliness
5. Persona Fit

Banned phrases list: `../lockedin-render-resume-en/banned_phrases.json`

### Korean cover letter (jaso) / cover letter

Load and apply:

```
../lockedin-render-jaso/RUBRIC.md
```

Five dimensions (Korean dimension names are the canonical rubric
keys from `lockedin-render-jaso/RUBRIC.md` and are part of the
machine schema):

<!-- ko-example -->
1. 두괄식 (lead-with-conclusion)
2. 구조화 (STAR / PAR structure adherence)
3. 구체성 (concreteness, ontology-grounded)
4. 표현 (no banned phrases, active voice)
5. 적합성 (company / role fit)
<!-- /ko-example -->

Banned phrases list: `../lockedin-render-jaso/banned_phrases.json`

## How the reviewer turn uses this file

1. Read this file (RUBRIC.md in this directory) at the start of the
   reviewer turn.
2. Identify document type (English resume or Korean cover letter (jaso)).
3. Load the referenced rubric file via the path above. Read it fresh
   from disk in this turn. Do NOT rely on memory from the scorer turn.
4. Score against the five dimensions defined in that file.
5. Emit JSON using the output schema defined in `prompt-reviewer.md`.

**Hard guard**: if neither referenced rubric file is visible in this
turn's context, STOP and request it before scoring. Do not score from
memory of a prior turn.

## Pass criterion

Pass criterion is inherited from the referenced rubric:

- `revisions_required` is false only when ALL dimensions >= 4.0,
  `banned_phrase_hits` is empty, and `missing_slugs` is empty.

For drive-by audits (no vault), `missing_slugs` is vacuously empty
(the user's document has no ontology slug notation). In that case,
pass requires only the dimension and banned-phrase conditions.

## Document type detection heuristics

The scorer turn (`prompt-scorer.md`) makes the type call before
routing. Heuristics:

- File extension `.md`, `.txt`, or `.pdf` with Korean characters ->
  probable jaso. Confirm by presence of common Korean section markers
  <!-- ko-example -->(지원동기, 성장과정, 성격의 장단점, 입사 후 포부)<!-- /ko-example -->
  or overall Korean language.
- English document with "Experience", "Skills", "Education" headers ->
  English resume.
- Ambiguous case: ask the user one question before proceeding.
- For post-ingest audits, the source document type was determined
  during ingest; use that classification.

## Evidence recall (informational)

Both referenced rubrics define evidence recall identically:

```
evidence_recall = cited_entities / max(matched_entities, 1)
```

For drive-by audits with no vault, `matched_entities` is 0 and
`evidence_recall` is 0.0. This is expected and non-penalizing — the
pass gate does not use recall. Surface it in the report as N/A for
drive-by mode.

## Calibration status

This router inherits calibration status from both render skills:

- `../lockedin-render-resume-en/RUBRIC.md`: v1.0, research-based
  calibration (cross-source consensus, 20+ US tech-resume guides).
- `../lockedin-render-jaso/RUBRIC.md`: research-based calibration
  (Korean cover letter (jaso) literature).

The audit skill does not add new dimensions or modify band thresholds.
If calibration drift is observed, update the source rubric file, not
this router.
