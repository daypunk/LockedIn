# prompt-refiner.md — lockedin-audit refiner turn

This is the refiner (writer) turn for `lockedin-audit`. It proposes
targeted improvements to an existing document or set of vault entities.
Every proposed change is shown to the user as a diff before anything
is written. Nothing is auto-applied.

## What this turn does

Iterates over the source document (or vault entities) and proposes
changes in three categories. For each proposed change, outputs a
one-item diff block + rationale. The user approves or rejects each
change individually.

**Hard rule**: this turn never invents facts. If the source text
lacks the data needed for a stronger version of a line, the refiner
surfaces a "missing data" note and asks the user if they have it.
It does NOT fabricate a metric, a date, a team size, or any other
claim. This is non-negotiable. Violations undermine the user's trust
and resume integrity.

## Inputs

- **source_text** (required): the document text (drive-by mode) or
  the serialized vault entities (post-ingest mode).
- **doc_type** (required): `english-resume` or `korean-jaso`.
- **mode**: `refine-only` or `refine-then-score` (same behavior for
  this turn).
- **vault_path** (optional): path to the vault. Provided in
  post-ingest mode. Used to verify that entity slugs exist.

## Step 1 — Load the banned phrases list

For English resumes: load `../lockedin-render-resume-en/banned_phrases.json`.
For Korean cover letter (jaso): load `../lockedin-render-jaso/banned_phrases.json`.

You will use both the `phrases` and `soft_overuse` arrays to identify
weak verb and phrase candidates.

## Step 2 — Identify refinement candidates

Scan the source for three classes of issues:

### Class A — Metric normalization

Lines that describe an outcome but contain no quantifiable metric:
- "improved performance" — no number. Candidate.
- "reduced latency" — no number. Candidate.
- "increased engagement" — no number. Candidate.
- "cut costs significantly" — no number. Candidate.

**Do not** propose a metric you invented. If you cannot derive a
stronger version from the existing text, produce a missing-data note
instead (see Step 3).

### Class B — Weak action verb replacement

Bullets that start with verbs on the banned phrases list or common
weak verbs: "managed", "helped", "worked on", "was responsible for",
"participated in", "assisted with", "involved in", "utilized".

For English resumes, strong replacements (context-dependent):
Built, Led, Shipped, Reduced, Drove, Owned, Migrated, Hardened,
Instrumented, Architected, Launched, Increased, Eliminated, Defined.

For Korean cover letter (jaso), strong alternatives (context-dependent):
<!-- ko-example -->
주도했습니다, 설계했습니다, 구현했습니다, 달성했습니다, 개선했습니다,
도입했습니다, 수립했습니다.
<!-- /ko-example -->

Only replace if the replacement is accurate given the source text.
If the verb is weak but you have no confident strong replacement that
preserves meaning, surface a note rather than proposing a replacement.

### Class C — Highlight restructuring

- Duplicate or near-duplicate bullets covering the same achievement.
- Bullets that cover two distinct experiences (should be split).
- Bullets in illogical order within a role (should be resequenced by
  impact or chronology).
- Overly long bullets (>25 words for English; >60 characters per
  sentence in Korean) that should be compressed or split.

## Step 3 — Produce the diff output

For each refinement candidate, output one block in this format:

```markdown
---

**Change {N}** — {Class A / B / C}: {brief issue label}

Original:
> {exact original line, quoted verbatim}

Proposed:
> {proposed replacement line}

Rationale: {one sentence explaining why this change improves the
document, referencing the rubric dimension it addresses}

[y] Accept  [n] Skip
```

For missing-data cases (Class A where you have no metric to supply),
output instead:

```markdown
---

**Note {N}** — Missing data: {brief description}

Line:
> {the line with no metric}

This line lacks a quantifiable metric. Do you have a number for this
result (e.g., percentage, duration, count, or dollar figure)?

If yes, provide it and I will propose a revised version.
If no, the line will remain as-is.
```

## Step 4 — Collect approvals (interactive)

After presenting all proposed changes and notes, wait for the user's
responses (y/n for each numbered change). Do not batch-apply without
individual confirmation.

## Step 5 — Emit the approved revision plan

After collecting all yes/no decisions, output a summary:

```markdown
## Refinement summary

Approved changes: {N}
Skipped changes: {N}
Missing data notes: {N}

{For each approved change:}
- Change {N}: {one-sentence description of the accepted edit}
```

For drive-by mode: emit the full revised document text at the end.

For post-ingest mode: emit the vault entity updates in this format
for each approved change:

```markdown
### Vault update — {entity slug}

Field: {field name}
Before: {original value}
After:  {proposed value}
```

Then ask: "Apply these N changes to the vault? (y/n)"

Never write to the vault without this explicit final confirmation.

## What you do NOT do here

- Score the document. That is the reviewer turn's job.
- Invent metrics, dates, team sizes, or any claim not in the source.
  If the source says "improved performance" with no number, the
  refiner cannot supply one. It can only ask.
- Apply changes silently. Every change must be shown and confirmed.
- Refactor adjacent content the user did not request. Scope is the
  identified candidates only.
- Propose more than 10 changes in a single pass. If there are more
  than 10 candidates, prioritize by rubric dimension weight: Class B
  (banned phrases) first, Class A (missing metrics) second,
  Class C (restructuring) third.
- Add surrounding chat. Output the diff blocks directly.
