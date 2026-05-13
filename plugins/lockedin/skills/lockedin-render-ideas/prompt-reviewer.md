# prompt-reviewer.md — render-ideas reviewer turn

This is the reviewer-turn instruction for `render-ideas`. It runs
in a SEPARATE Claude turn from the writer.

## Procedure

1. **Load `RUBRIC.md` (load-bearing).** Re-load RUBRIC.md from disk
   fresh in this reviewer turn; do not rely on context from any
   writer turn. The five dimensions and bands are the only thing you
   score against.
   **Hard guard**: if `RUBRIC.md` is not visible in this turn's
   context, STOP and request it before scoring.
2. **Slug verification.** Every `[[type/slug]]` reference must
   resolve in the vault. Missing slugs reduce evidence_ground.
3. **Score the SET** on five dimensions, not each idea individually.
   The user receives a set of ideas; the rubric judges the set.
4. **Decide `revisions_required`** — `true` if any dimension < 4.0
   OR `missing_slugs` non-empty.
5. **Emit JSON** in the schema below.

## Output schema (strict)

```json
{
  "feasibility": 0.0,
  "novelty": 0.0,
  "evidence_ground": 0.0,
  "scope_match": 0.0,
  "motivation_alignment": 0.0,
  "notes": [
    "feasibility: <one short sentence>",
    "novelty: <one short sentence>",
    "evidence_ground: <one short sentence>",
    "scope_match: <one short sentence>",
    "motivation_alignment: <one short sentence>"
  ],
  "missing_slugs": [],
  "revisions_required": false
}
```

- All five dimension keys must be present.
- `notes` is a list of exactly five strings, one per dimension in the
  listed order. Each string is a one-sentence rationale visible to the
  user — this is the trace that lets the user audit the score.
- `missing_slugs` lists `[[type/slug]]` references that do not resolve
  in the vault.
- `revisions_required` is `true` if any dimension < 4.0 OR
  `missing_slugs` non-empty.

## Revision feedback

If `revisions_required` is `true`, the calling skill MAY pass the
JSON back to the writer for one revision cycle. Limit: one revision.

## What you do NOT do

- Rewrite the ideas.
- Skip dimensions.
- Add prose around the JSON.
