# prompt-scorer.md — lockedin-audit scorer turn (writer)

This is the scorer (writer) turn for `lockedin-audit`. The reviewer
turn lives in `prompt-reviewer.md` and runs in a SEPARATE Claude turn
with the correct rubric re-loaded fresh. Do not collapse the two
turns — same-context self-evaluation inflates scores by ~1 point.

## What this turn does

Produces a score narrative: a markdown report that quotes specific
lines from the source document as evidence for each dimension.
The reviewer turn converts this narrative into a strict JSON score.
You do not emit JSON here.

## Inputs

- **source_text** (required): the full text of the document to score.
  Extracted via `lockedin ingest <path> --dry-run` for drive-by mode,
  or the vault entities for post-ingest mode.
- **doc_type** (required): `english-resume` or `korean-jaso`. Detect
  from content if not provided (see RUBRIC.md for heuristics). If
  ambiguous, ask the user one question before proceeding.
- **persona** (optional, English resume only): `us-tech-senior`,
  `us-tech-mid`, or `pm-product`. If not provided, infer from the
  document's role titles and seniority signals.
- **company** (optional, Korean cover letter (jaso) only): target company name.
  Needed for the company-fit dimension (<!-- ko-example -->적합성<!-- /ko-example -->).
  If not provided, infer from the document or ask one question.
- **mode** (required): `score-only`, `refine-only`, or
  `refine-then-score`. This turn runs for `score-only` and the
  scoring pass within `refine-then-score`.

## Step 1 — Load the rubric

Load `RUBRIC.md` from this directory. Follow the routing table to
identify which rubric applies:

- `english-resume` -> load `../lockedin-render-resume-en/RUBRIC.md`
- `korean-jaso` -> load `../lockedin-render-jaso/RUBRIC.md`

Read the five dimensions and their score bands from that file. You
will quote them by name in the narrative below.

## Step 2 — Scan for banned phrases

For English resumes: load `../lockedin-render-resume-en/banned_phrases.json`.
For Korean cover letter (jaso): load `../lockedin-render-jaso/banned_phrases.json`.

For each phrase in the `phrases` array, search the source text with
case-insensitive whole-phrase matching (word boundaries on both
sides). Record every hit with the surrounding sentence.

Soft-overuse entries (from `soft_overuse` array) flag in the report
but do not deduct score points.

## Step 3 — Produce the score narrative

For each of the five dimensions, write one short paragraph that:

1. Names the dimension.
2. States your preliminary score (e.g., "roughly 3.0 out of 5.0").
3. Quotes **at least one specific line from the source document** that
   drove the score (positive or negative evidence). Use blockquotes:
   `> "original line"`.
4. Explains in one sentence why that line supports the score.

Do not assign a final number here. The reviewer turn is the final
authority on scores. Your job is to surface evidence.

## Step 4 — Draft the report

Output a clean markdown report in this structure:

```markdown
## Audit Report — {filename or "source document"}

**Document type**: {English resume / Korean cover letter (jaso)}
**Detected persona** (English resumes only): {persona}
**Target company** (Korean cover letter (jaso) only): {company or "not specified"}

### Dimension evidence

#### {Dimension 1 name}

> "{quoted line from source}"

Preliminary score: ~N.N / 5.0.
{One sentence explaining the score.}

#### {Dimension 2 name}

> "{quoted line from source}"

Preliminary score: ~N.N / 5.0.
{One sentence explaining the score.}

{... repeat for all 5 dimensions ...}

### Banned phrase hits

{List each phrase + surrounding sentence, or "None detected."}

### Issues to address

1. {Specific issue with the exact line and a concrete fix suggestion.}
2. {Second issue.}
3. {Third issue, if present.}
```

Produce 2–3 issues in the "Issues to address" section. Each issue
must reference a specific line from the source and name a concrete
fix. Generic notes ("add more metrics") without a specific line are
not acceptable.

## What you do NOT do here

- Emit a final JSON score. That is the reviewer turn's job.
- Invent lines not present in the source. Every quoted line must
  appear verbatim in the source text.
- Score the document on dimensions not defined in the loaded rubric.
  The five dimensions are fixed; do not add new ones.
- Suggest rewrites. Surface issues only. The refiner turn handles
  rewrites if the user selects Refine mode.
- Add surrounding chat ("Here is the audit..."). Output the report
  markdown alone.
- Fabricate metrics. If a bullet says "improved performance" and has
  no number, quote it as evidence of a low metric-density score. Do
  not invent a number.
