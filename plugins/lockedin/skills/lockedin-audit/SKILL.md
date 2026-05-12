---
name: lockedin-audit
description: |
  Score and refine arbitrary resume or cover-letter documents against
  LockedIn's calibrated rubric. Works with or without a vault. Three
  operating modes: Score only, Refine only, Refine then Score (default).
  Two entry points: drive-by (file path, no vault required) and
  post-ingest (triggered after a completed lockedin ingest).

  Use when the user says: "audit this resume", "score my resume",
  "grade my resume", "audit my cover letter", "how does my resume
  score", "check my resume", or provides a file path and asks for
  feedback. Also triggered automatically after a successful
  `lockedin ingest` to offer the user a scoring pass.
---

# lockedin-audit

Scores and refines existing resume or cover-letter documents against the
same rubric used by `render-resume-en` and `render-jaso`. No vault is
required for the drive-by path.

## Entry points

### A. Drive-by audit (no vault required)

User provides a file path. The skill:

1. Calls `lockedin ingest <path> --dry-run` via Bash to extract text
   without mutating the vault.
2. Detects document type (English resume vs. Korean cover letter (jaso)) from
   content and file name.
3. Routes to the correct rubric (see RUBRIC.md) and runs the
   selected mode (default: Score only for drive-by).
4. Returns a markdown report. No vault writes. No file writes.

### B. Post-ingest audit (existing vault user)

Triggered when `lockedin ingest` has just completed and merged N new
entities into the vault. The skill presents a 4-option menu:

```
Ingest complete. <N> new entities merged into vault.

What next?
  [1] Score only          — apply rubric to the source document as-is.
                            No vault changes.
  [2] Refine only          — diff-based refinement of merged entities
                            (normalize metrics, replace weak action verbs,
                            restructure highlights). Every change shown as
                            diff, user approves before vault write.
  [3] Refine then Score    — refinement followed by scoring of refined
                            output (DEFAULT RECOMMENDED — quantifies score
                            lift)
  [4] Skip
```

## Three operating modes

### Mode 1 — Score only

Applies the rubric to the source document and emits a clean markdown
report. Steps:

1. Detect document type (English resume or Korean cover letter (jaso)).
2. Load the appropriate rubric via RUBRIC.md routing.
3. **Writer turn** (`prompt-scorer.md`): reads the source, quotes specific
   lines as evidence, produces a draft score narrative.
4. **Reviewer turn** (`prompt-reviewer.md`): runs in a SEPARATE Claude
   context, re-loads RUBRIC.md fresh, emits a JSON score.
5. Merge writer narrative and reviewer JSON into the final markdown
   report (see Output format).

No vault writes. Source document is read-only.

### Mode 2 — Refine only

Proposes targeted refinements to the source document (or to vault
entities if triggered post-ingest). Steps:

1. Load the source document (or vault entities to refine).
2. **Refiner turn** (`prompt-refiner.md`): iterates over bullets /
   paragraphs and proposes changes in three categories:
   - Metric normalization (e.g., "improved performance" ->
     "reduced p95 latency 40% over Q3 2025").
   - Action verb replacement (weak -> strong, per banned_phrases.json
     from the relevant render skill).
   - Highlight restructuring (group, sequence, deduplicate).
3. For **each proposed change**: show original line + proposed line +
   one-sentence rationale. Ask the user yes/no.
4. Never invent facts. If the source lacks data for a stronger
   version of a line, the refiner surfaces a "missing data" note and
   asks the user if they have it. It does NOT fabricate a metric.
5. After all yes/no decisions, collect approved changes.
6. Post-ingest path: apply approved changes to vault via documented
   CLI commands (with dry-run preview). Drive-by path: emit a
   revised document as markdown for the user to copy.

### Mode 3 — Refine then Score (default for post-ingest)

Chains Mode 2 then Mode 1. After refinement is approved:

1. Run scorer + reviewer on the refined output.
2. Report both the pre-refinement score (from the original document)
   and the post-refinement score (from the refined version).
3. Display the delta per dimension so the user can see the impact
   of each change.

Output includes a side-by-side comparison table:

```
| Dimension | Before | After | Delta |
```

## Output format

All output is clean markdown. No badges. No verification blocks. No
images. No emoji-heavy decorations.

### Score report

```markdown
## Audit Report — {filename or "source document"}

**Document type**: English resume / Korean cover letter (jaso)
**Mode**: Score only / Refine then Score

### Scores

| Dimension | Score |
| --- | --- |
| {dim 1} | N.N / 5.0 |
| {dim 2} | N.N / 5.0 |
| {dim 3} | N.N / 5.0 |
| {dim 4} | N.N / 5.0 |
| {dim 5} | N.N / 5.0 |
| **Total** | **N.N / 5.0** |

### Evidence

{For each dimension: one sentence rationale + the specific line(s)
from the source that drove the score.}

### Issues to address

{2–3 specific, actionable improvement notes. Each references a
specific line and a specific fix.}

### Banned phrase hits

{List each hit with surrounding context, or "None".}
```

### Refine then Score delta report (Mode 3 only)

Appended after the score section:

```markdown
### Score delta (Refine then Score)

| Dimension | Before | After | Delta |
| --- | --- | --- | --- |
| {dim 1} | N.N | N.N | +N.N |
| ... | | | |
```

## Required design constraints

- **Two-turn writer/reviewer.** Scorer (writer turn) and reviewer
  (reviewer turn) run in separate Claude contexts. RUBRIC.md must be
  re-loaded fresh in the reviewer turn. See CLAUDE.md working
  agreement: same-context self-evaluation inflates scores by ~1 point.
- **Never invent facts.** Refinements reshape existing content.
  Missing data surfaces as a question to the user, never as a
  fabricated claim.
- **Refinement diffs always shown before vault mutation.** The
  default is ask, not auto-apply. This is non-negotiable.
- **Reuses existing rubrics.** The five dimensions are defined in
  `../lockedin-render-resume-en/RUBRIC.md` (English) and
  `../lockedin-render-jaso/RUBRIC.md` (Korean). RUBRIC.md in this
  directory routes to them. No duplication.
- **Clean markdown only.** No badges, no verification blocks,
  no PNG, no emoji-heavy formatting.

## Files in this directory

```
SKILL.md            (this file)
RUBRIC.md           router to the two render-skill rubrics
prompt-scorer.md    writer-turn scoring prompt
prompt-refiner.md   writer-turn refinement prompt
prompt-reviewer.md  reviewer-turn prompt (separate Claude context, fresh RUBRIC load)
AGENTS.md           agent roles and orchestration
TOOLS.md            tool requirements per mode
```

## Routing: when not to use this skill

- User wants a new resume written from vault data -> `render-resume-en`.
- User wants a new jaso written from vault data -> `render-jaso`.
- User wants to import new experience into the vault -> `lockedin ingest`.

## Do NOT use when

- The user just wants to write a resume from scratch; use
  `render-resume-en` instead.
- The vault is completely empty and the user has no existing document
  to audit; direct them to `/lockedin init` first.
