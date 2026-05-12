# prompt-reviewer.md — lockedin-audit reviewer turn

This is the reviewer turn for `lockedin-audit`. It runs in a SEPARATE
Claude turn from the scorer (`prompt-scorer.md`). At the start of
this turn, **re-load the correct RUBRIC.md fresh from disk** — do not
rely on memory of the rubric from the scorer turn. Same-context self-
evaluation inflates scores by ~1 point per the CLAUDE.md working
agreement.

## Load sequence (load-bearing)

The reviewer turn MUST execute steps 1–3 before scoring anything:

**Step 1.** Read `RUBRIC.md` from THIS directory
(`plugins/lockedin/skills/lockedin-audit/RUBRIC.md`) to identify
document type routing.

**Step 2.** Based on the document type, read the source rubric:

- English resume -> read `../lockedin-render-resume-en/RUBRIC.md`
  fresh from disk in this turn.
- Korean cover letter (jaso) -> read `../lockedin-render-jaso/RUBRIC.md`
  fresh from disk in this turn.

**Step 3.** Confirm the five dimension names and score bands are
visible in this turn's context BEFORE scoring.

**Hard guard**: if the content of the referenced rubric file is NOT
visible in this turn's context, STOP and request it before scoring.
Do not score from memory. Do not proceed with remembered scores from
the scorer turn.

## Inputs

- The score narrative produced by the scorer turn (`prompt-scorer.md`).
- The original source document text (for independent verification —
  do not rely solely on what the scorer quoted).
- Document type: `english-resume` or `korean-jaso`.
- Persona (English resume only) and company (Korean cover letter (jaso) only).
- The user's vault path (optional — for slug verification; may be
  absent in drive-by mode).

## Procedure

1. **Load rubric** (see Load sequence above).
2. **Load banned phrases**: `../lockedin-render-resume-en/banned_phrases.json`
   for English; `../lockedin-render-jaso/banned_phrases.json` for
   Korean. Run a case-insensitive whole-phrase match on the source
   text. Each `phrases[]` hit drops the cleanliness dimension by 1.0
   (floor 0). `soft_overuse[]` entries flag in notes but deduct 0.5
   only if the same phrase appears >= 2 times.
3. **Slug verification** (post-ingest mode only; skip for drive-by):
   for every `[[type/slug]]` reference in the source, confirm it
   exists in the vault. Missing slugs reduce the metric / concreteness
   dimension score.
4. **Evidence recall** (post-ingest mode only; report N/A for
   drive-by): compute
   `evidence_recall = cited_entities / max(matched_entities, 1)`.
   See the referenced rubric's "Evidence recall (informational)"
   section for the definition. This is informational, not a gate.
5. **Score each dimension independently** on a 0.0–5.0 scale using
   the bands in the referenced rubric. Do NOT average the scorer's
   preliminary scores — read the source document yourself and apply
   the bands independently.
6. **Decide `revisions_required`**: `true` if any dimension < 4.0
   OR `banned_phrase_hits` non-empty OR `missing_slugs` non-empty.
7. **Emit JSON** in the exact schema below. No prose around it.

## Output schema — English resume

```json
{
  "doc_type": "english-resume",
  "persona": "us-tech-senior",
  "metric_density": 0.0,
  "action_verb_quality": 0.0,
  "structural_adherence": 0.0,
  "banned_phrase_cleanliness": 0.0,
  "persona_fit": 0.0,
  "total": 0.0,
  "evidence_recall": 0.0,
  "notes": [
    "metric_density: <one short sentence on why this score>",
    "action_verb_quality: <one short sentence>",
    "structural_adherence: <one short sentence>",
    "banned_phrase_cleanliness: <one short sentence>",
    "persona_fit: <one short sentence>"
  ],
  "banned_phrase_hits": [],
  "missing_slugs": [],
  "revisions_required": false
}
```

`total` is the arithmetic mean of the five dimension scores, rounded
to one decimal place.

## Output schema — Korean cover letter (jaso)

The five dimension keys are the canonical Korean rubric dimension
names from `lockedin-render-jaso/RUBRIC.md`; they are part of the
machine schema and must appear verbatim.

<!-- ko-example -->
```json
{
  "doc_type": "korean-jaso",
  "company": "<company name or null>",
  "두괄식": 0.0,
  "구조화": 0.0,
  "구체성": 0.0,
  "표현": 0.0,
  "적합성": 0.0,
  "total": 0.0,
  "evidence_recall": 0.0,
  "notes": [
    "두괄식: <one short sentence on why this score>",
    "구조화: <one short sentence>",
    "구체성: <one short sentence>",
    "표현: <one short sentence>",
    "적합성: <one short sentence>"
  ],
  "banned_phrase_hits": [],
  "missing_slugs": [],
  "revisions_required": false
}
```
<!-- /ko-example -->

`total` is the arithmetic mean of the five dimension scores, rounded
to one decimal place.

## Schema rules (both types)

- All five dimension keys must be present and scored.
- `notes` is a list of exactly five strings, one per dimension, in
  the order listed in the schema above.
- `banned_phrase_hits` lists each matched phrase with surrounding
  context, pipe-separated:
  `["responsible for|... was responsible for production deploys ..."]`.
- `missing_slugs` lists any `[[type/slug]]` references that do not
  resolve in the vault. Empty list `[]` for drive-by mode.
- `evidence_recall` is 0.0 for drive-by mode (no vault). This is
  expected and non-penalizing.
- `revisions_required` follows the gate rules in step 6.
- Output is a single JSON object. No prose before or after it.

## Mode 3 (Refine then Score) — delta reporting

When this reviewer turn is running the POST-refinement scoring pass
in Mode 3, the calling skill provides both the pre-refinement JSON
score and the current (post-refinement) source text. In that case:

1. Score the post-refinement source exactly as above.
2. Add a `"pre_refinement"` key to the output containing the
   pre-refinement dimension scores (provided by the calling skill):

```json
{
  "doc_type": "english-resume",
  ...five dimension scores for post-refinement...,
  "total": 0.0,
  "pre_refinement": {
    "metric_density": 0.0,
    "action_verb_quality": 0.0,
    "structural_adherence": 0.0,
    "banned_phrase_cleanliness": 0.0,
    "persona_fit": 0.0,
    "total": 0.0
  },
  ...
}
```

The calling skill uses this to render the delta table in the final
report.

## Revision feedback

If `revisions_required` is `true`, the calling skill MAY pass the
JSON back to the scorer for one revision cycle. The scorer reads
`notes` and the hits, updates the narrative, and the reviewer runs
again. Limit: **one revision cycle**. After that, deliver the best
version + JSON to the user.

## What you do NOT do here

- Rewrite the document. You score; the scorer surfaces narrative;
  the refiner proposes changes.
- Skip dimensions. Even a dimension that scores 5/5 must appear in
  `notes` with a one-sentence justification.
- Add prose around the JSON. The output must parse as `json.loads`;
  the calling skill expects a single JSON object.
- Be lenient. Three banned-phrase hits means the cleanliness score
  is 2.0 regardless of how well the rest reads. The rubric is the
  rubric.
- Score from memory. The rubric file must be loaded fresh in this
  turn. See Load sequence above.
